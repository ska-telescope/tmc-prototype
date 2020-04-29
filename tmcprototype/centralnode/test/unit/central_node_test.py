import contextlib
import importlib
import sys
import mock
import types
import json
import pytest
from tango import DevState
from tango.test_context import DeviceTestContext
from mock import MagicMock
from mock import Mock
from centralnode import CentralNode,const
from centralnode.const import CMD_SET_STOW_MODE, STR_STARTUP_CMD_ISSUED, \
    STR_STOW_CMD_ISSUED_CN, STR_STANDBY_CMD_ISSUED
from ska.base.control_model import HealthState


def test_telescope_health_state_is_degraded_when_csp_master_leaf_node_is_degraded_after_start():
    # arrange:
    device_under_test = CentralNode
    csp_master_ln_fqdn = 'ska_mid/tm_leaf_node/csp_master'
    csp_master_ln_health_attribute = 'cspHealthState'
    initial_dut_properties = {
        'CspMasterLeafNodeFQDN': csp_master_ln_fqdn
    }

    event_subscription_map = {}

    csp_master_ln_proxy_mock = Mock()
    csp_master_ln_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args, **kwargs: event_subscription_map.update({attr_name: callback}))

    proxies_to_mock = {
        csp_master_ln_fqdn: csp_master_ln_proxy_mock
    }

    with fake_tango_system(device_under_test, initial_dut_properties, proxies_to_mock) as tango_context:
        # act:
        dummy_event = create_dummy_event(csp_master_ln_fqdn)
        event_subscription_map[csp_master_ln_health_attribute](dummy_event)

        # assert:
        assert tango_context.device.telescopeHealthState == HealthState.DEGRADED


def test_stow_antennas_should_set_stow_mode_on_leaf_nodes():
    # arrange:
    device_under_test = CentralNode
    dish_device_ids = [str(i).zfill(4) for i in range(1,10)]
    fqdn_prefix = "ska_mid/tm_leaf_node/d"
    initial_dut_properties = {
        'DishLeafNodePrefix': fqdn_prefix,
        'NumDishes': len(dish_device_ids)
    }
    proxies_to_mock = { fqdn_prefix + device_id : Mock() for device_id in dish_device_ids }

    # act:
    with fake_tango_system(device_under_test, initial_dut_properties, proxies_to_mock) as tango_context:
        tango_context.device.StowAntennas(dish_device_ids)

    # assert:
    for proxy_mock in proxies_to_mock.values():
        proxy_mock.command_inout.assert_called_with(CMD_SET_STOW_MODE)


def test_activity_message_attribute_captures_the_last_received_command():
    # arrange:
    device_under_test = CentralNode

    # act & assert:
    with fake_tango_system(device_under_test)as tango_context:
        dut = tango_context.device
        dut.StartUpTelescope()
        assert_activity_message(dut, STR_STARTUP_CMD_ISSUED)

        dut.StandByTelescope()
        assert_activity_message(dut, STR_STANDBY_CMD_ISSUED)


def assert_activity_message(dut, expected_message):
    assert dut.activityMessage == expected_message # reads tango attribute


def create_dummy_event(csp_master_ln_fqdn):
    fake_event = Mock()
    fake_event.err = False
    fake_event.attr_name = f"{csp_master_ln_fqdn}/healthState"
    fake_event.attr_value.value = HealthState.DEGRADED
    return fake_event


def any_method(with_name=None):
    class AnyMethod():
        def __eq__(self, other):
            if not isinstance(other, types.MethodType):
                return False

            return other.__func__.__name__ == with_name if with_name else True

    return AnyMethod()


def test_assign_resources_should_send_json_to_subarraynode():
    # arrange:
    device_under_test = CentralNode
    subarray1_fqdn = 'ska_mid/tm_subarray_node/1'
    dut_properties = {
        'TMMidSubarrayNodes': subarray1_fqdn
    }

    subarray1_proxy_mock = MagicMock()
    subarray1_proxy_mock.DevState = DevState.OFF
    proxies_to_mock = {
        subarray1_fqdn: subarray1_proxy_mock
    }

    with fake_tango_system(device_under_test, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:
        assign_command = '{"subarrayID":1,"dish":{"receptorIDList":["0001"]},"sdp":{"id":"sbi-mvp01-20200325-00001","max_length":100.0,"scan_types":[{"id":"science_A","coordinate_system":"ICRS","ra":"02:42:40.771","dec":"-00:00:47.84","subbands":[{"freq_min":0.35e9,"freq_max":1.05e9,"nchan":372,"input_link_map":[[1,0],[101,1]]}]},{"id":"calibration_B","coordinate_system":"ICRS","ra":"12:29:06.699","dec":"02:03:08.598","subbands":[{"freq_min":0.35e9,"freq_max":1.05e9,"nchan":372,"input_link_map":[[1,0],[101,1]]}]}],"processing_blocks":[{"id":"pb-mvp01-20200325-00001","workflow":{"type":"realtime","id":"vis_receive","version":"0.1.0"},"parameters":{}},{"id":"pb-mvp01-20200325-00002","workflow":{"type":"realtime","id":"test_realtime","version":"0.1.0"},"parameters":{}},{"id":"pb-mvp01-20200325-00003","workflow":{"type":"batch","id":"ical","version":"0.1.0"},"parameters":{},"dependencies":[{"pb_id":"pb-mvp01-20200325-00001","type":["visibilities"]}]},{"id":"pb-mvp01-20200325-00004","workflow":{"type":"batch","id":"dpreb","version":"0.1.0"},"parameters":{},"dependencies":[{"pb_id":"pb-mvp01-20200325-00003","type":["calibration"]}]}]}}'
        device_proxy=tango_context.device
        device_proxy.AssignResources(assign_command)

        # assert:
        jsonArgument = json.loads(assign_command)
        input_json_subarray = jsonArgument.copy()
        del input_json_subarray["subarrayID"]
        input_to_sa = json.dumps(input_json_subarray)
        subarray1_proxy_mock.command_inout.assert_called_with(const.CMD_ASSIGN_RESOURCES,
                                                             input_to_sa)

        assert_activity_message(tango_context.device, const.STR_ASSIGN_RESOURCES_SUCCESS)

@pytest.mark.xfail
def test_release_resources_when_subarray_is_idle():
    # arrange:
    device_under_test = CentralNode
    subarray1_fqdn = 'ska_mid/tm_subarray_node/1'
    dut_properties = {
        'TMMidSubarrayNodes': subarray1_fqdn
    }

    subarray1_proxy_mock = MagicMock()
    subarray1_proxy_mock.DevState = DevState.ON
    subarray1_proxy_mock.receptorIDList = [1]
    proxies_to_mock = {
        subarray1_fqdn: subarray1_proxy_mock
    }

    with fake_tango_system(device_under_test, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:
        # act:
        release_input= '{"subarrayID":1,"releaseALL":true,"receptorIDList":[]}'
        tango_context.device.ReleaseResources(release_input)

        # assert:
        jsonArgument = json.loads(release_input)
        if jsonArgument['releaseALL'] == True:
            subarray1_proxy_mock.command_inout.assert_called_with(const.CMD_RELEASE_RESOURCES)


def test_standby():
    # arrange:
    device_under_test = CentralNode
    csp_master_ln_fqdn = 'ska_mid/tm_leaf_node/csp_master'
    sdp_master_ln_fqdn = 'ska_mid/tm_leaf_node/sdp_master'
    subarray1_fqdn = 'ska_mid/tm_subarray_node/1'
    dish_device_ids = [str(i).zfill(1) for i in range(1,4)]
    dish_leaf_fqdn_prefix = "ska_mid/tm_leaf_node/d"

    dut_properties = {
        'DishLeafNodePrefix': dish_leaf_fqdn_prefix,
        'SdpMasterLeafNodeFQDN': sdp_master_ln_fqdn,
        'CspMasterLeafNodeFQDN': csp_master_ln_fqdn,
        'TMMidSubarrayNodes': subarray1_fqdn,
        'NumDishes': len(dish_device_ids)
    }
    dish_ln1_proxy_mock = MagicMock()
    csp_master_ln_proxy_mock = Mock()
    sdp_master_ln_proxy_mock = Mock()
    subarray1_proxy_mock = MagicMock()
    proxies_to_mock = {
        dish_leaf_fqdn_prefix + "0001": dish_ln1_proxy_mock,
        csp_master_ln_fqdn: csp_master_ln_proxy_mock,
        sdp_master_ln_fqdn: sdp_master_ln_proxy_mock,
        subarray1_fqdn: subarray1_proxy_mock
    }
    with fake_tango_system(device_under_test, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:
        # act:
        tango_context.device.StandByTelescope()

        # assert:
        dish_ln1_proxy_mock.command_inout.assert_called_with(const.CMD_SET_STANDBY_MODE)
        csp_master_ln_proxy_mock.command_inout.assert_called_with(const.CMD_STANDBY, [])
        sdp_master_ln_proxy_mock.command_inout.assert_called_with(const.CMD_STANDBY)
        subarray1_proxy_mock.command_inout.assert_called_with(const.CMD_STANDBY)
        assert_activity_message(tango_context.device, const.STR_STANDBY_CMD_ISSUED)

def test_startup():
    # arrange:
    device_under_test = CentralNode
    csp_master_ln_fqdn = 'ska_mid/tm_leaf_node/csp_master'
    sdp_master_ln_fqdn = 'ska_mid/tm_leaf_node/sdp_master'
    subarray1_fqdn = 'ska_mid/tm_subarray_node/1'
    dish_device_ids = [str(i).zfill(1) for i in range(1,4)]
    dish_leaf_fqdn_prefix = "ska_mid/tm_leaf_node/d"

    dut_properties = {
        'DishLeafNodePrefix': dish_leaf_fqdn_prefix,
        'SdpMasterLeafNodeFQDN': sdp_master_ln_fqdn,
        'CspMasterLeafNodeFQDN': csp_master_ln_fqdn,
        'TMMidSubarrayNodes': subarray1_fqdn,
        'NumDishes': len(dish_device_ids)
    }
    dish_ln1_proxy_mock = MagicMock()
    csp_master_ln_proxy_mock = Mock()
    sdp_master_ln_proxy_mock = Mock()
    subarray1_proxy_mock = MagicMock()
    proxies_to_mock = {
        dish_leaf_fqdn_prefix + "0001": dish_ln1_proxy_mock,
        csp_master_ln_fqdn: csp_master_ln_proxy_mock,
        sdp_master_ln_fqdn: sdp_master_ln_proxy_mock,
        subarray1_fqdn: subarray1_proxy_mock
    }

    with fake_tango_system(device_under_test, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:
        # act:
        tango_context.device.StartUpTelescope()

        # assert:
        dish_ln1_proxy_mock.command_inout.assert_called_with(const.CMD_SET_OPERATE_MODE)
        csp_master_ln_proxy_mock.command_inout.assert_called_with(const.CMD_STARTUP, [])
        sdp_master_ln_proxy_mock.command_inout.assert_called_with(const.CMD_STARTUP)
        subarray1_proxy_mock.command_inout.assert_called_with(const.CMD_STARTUP)
        assert_activity_message(tango_context.device, const.STR_STARTUP_CMD_ISSUED)


@contextlib.contextmanager
def fake_tango_system(device_under_test, initial_dut_properties={}, proxies_to_mock={},
                      device_proxy_import_path='tango.DeviceProxy'):

    with mock.patch(device_proxy_import_path) as patched_constructor:
        patched_constructor.side_effect = lambda device_fqdn: proxies_to_mock.get(device_fqdn, Mock())
        patched_module = importlib.reload(sys.modules[device_under_test.__module__])

    device_under_test = getattr(patched_module, device_under_test.__name__)

    device_test_context = DeviceTestContext(device_under_test, properties=initial_dut_properties)
    device_test_context.start()
    yield device_test_context
    device_test_context.stop()