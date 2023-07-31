from ska_control_model import HealthState
from ska_tmc_common.dev_factory import DevFactory
from tango import DevState


def test_attributes(tango_context, sdp_master_device):
    dev_factory = DevFactory()
    sdpmln_node = dev_factory.get_device(sdp_master_device)
    assert sdpmln_node.On()
    assert sdpmln_node.State() == DevState.ON
    assert sdpmln_node.Off()
    assert sdpmln_node.State() == DevState.OFF
    assert sdpmln_node.healthState == HealthState.OK
    assert not sdpmln_node.isSubsystemAvailable
