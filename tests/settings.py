"""Common Settings for testing of SDP Leaf Node"""
import json
import logging
import time

from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import ObsState
from ska_tmc_common import FaultType
from ska_tmc_common.enum import LivelinessProbeType
from tango import DeviceProxy

from ska_tmc_sdpmasterleafnode.manager.component_manager import (
    SdpMLNComponentManager,
)
from ska_tmc_sdpsubarrayleafnode.manager.component_manager import (
    SdpSLNComponentManager,
)

logger = logging.getLogger(__name__)

SLEEP_TIME = 0.5
TIMEOUT = 100

SDP_SUBARRAY_DEVICE_MID = "mid-sdp/subarray/01"
SDP_SUBARRAY_DEVICE_LOW = "low-sdp/subarray/01"
SDP_MASTER_DEVICE_MID = "mid-sdp/control/0"
SDP_MASTER_DEVICE_LOW = "low-sdp/control/0"
SDP_SUBARRAY_LEAF_NODE_MID = "mid-tmc/subarray-leaf-node-sdp/01"
SDP_SUBARRAY_LEAF_NODE_LOW = "low-tmc/subarray-leaf-node-sdp/01"
SDP_MASTER_LEAF_DEVICE_MID = "mid-tmc/leaf-node-sdp/0"
SDP_MASTER_LEAF_DEVICE_LOW = "low-tmc/leaf-node-sdp/0"
ASSIGN_TIMEOUT = json.dumps({"AssignResources": 35})
RELEASE_TIMEOUT = json.dumps({"ReleaseAllResources": 35})
CONFIGURE_TIMEOUT = json.dumps({"Configure": 35})
END_TIMEOUT = json.dumps({"End": 35})
ENDSCAN_TIMEOUT = json.dumps({"EndScan": 35})
SCAN_TIMEOUT = json.dumps({"Scan": 35})


TIMEOUT_DEFECT = json.dumps(
    {
        "enabled": True,
        "fault_type": FaultType.STUCK_IN_INTERMEDIATE_STATE,
        "error_message": "Command stuck in processing",
        "result": ResultCode.FAILED,
        "intermediate_state": ObsState.RESOURCING,
    }
)

RESET_DEFECT = json.dumps(
    {
        "enabled": False,
        "fault_type": FaultType.FAILED_RESULT,
        "error_message": "Default exception.",
        "result": ResultCode.FAILED,
    }
)
FAILED_RESULT_DEFECT = json.dumps(
    {
        "enabled": True,
        "fault_type": FaultType.FAILED_RESULT,
        "error_message": "Device is defective, cannot process command",
        "result": ResultCode.FAILED,
    }
)
ERROR_PROPAGATION_DEFECT = json.dumps(
    {
        "enabled": True,
        "fault_type": FaultType.LONG_RUNNING_EXCEPTION,
        "error_message": "Exception occurred, command failed.",
        "result": ResultCode.FAILED,
    }
)


def count_faulty_devices(component_manager):
    """Count faulty devices"""
    result = 0
    for dev_info in component_manager.checked_devices:
        if dev_info.unresponsive:
            result += 1
    return result


def update_admin_mode_callback(admin_mode):
    """Dummy update admin mode callback function"""
    logger.info(admin_mode)


def create_cm(cm_class, device):
    """Create Component Manager"""
    if cm_class == "SdpMLNComponentManager":
        return SdpMLNComponentManager(
            sdp_master_admin_mode_enabled=True,
            _update_admin_mode_callback=update_admin_mode_callback,
            sdp_master_device_name=device,
            logger=logger,
            _liveliness_probe=(LivelinessProbeType.NONE),
        )

    return SdpSLNComponentManager(
        _update_admin_mode_callback=update_admin_mode_callback,
        _sdp_subarray_admin_mode_enabled=True,
        sdp_subarray_dev_name=device,
        logger=logger,
        _liveliness_probe=LivelinessProbeType.NONE,
    )


def wait_for_attribute_value(
    device: DeviceProxy,
    attribute_name: str,
    attribute_value,
) -> bool:
    """Waits for attribute value to change on the given device."""
    start_time = time.time()
    while device.read_attribute(attribute_name).value == attribute_value:
        time.sleep(0.5)

        if time.time() - start_time >= 10:
            logger.info(
                "The attribute value after time out is: %s",
                device.read_attribute(attribute_name).value,
            )
            return False
    return True


def wait_for_cm_obstate_attribute_value(cm, obs_state: ObsState) -> bool:
    """Waits for attribute value to change on the given device."""
    start_time = time.time()
    while cm.get_obs_state() != obs_state:
        time.sleep(0.5)
        if time.time() - start_time >= 100:
            logger.info(
                "The attribute value after time out is: %s",
                cm.get_obs_state(),
            )
            return False
    return True


def wait_for_attribute_to_change_to(
    device: str, attribute_name: str, attribute_value: str
) -> None:
    """Wait for the attribute to change to given value.

    :param device: Name of the device
    :param attribute_name: Attribute name as a string
    :param attribute_value: Value of attribute to be asserted
    """
    device_proxy = DeviceProxy(device)
    start_time = time.time()
    elapsed_time = time.time() - start_time
    current_value = device_proxy.read_attribute(attribute_name).value
    while current_value != attribute_value:
        elapsed_time = time.time() - start_time
        if elapsed_time >= TIMEOUT:
            raise AssertionError(
                "Attribute value is not equal to given value. "
                + f"Current value: {current_value}, expected value: "
                + f"{attribute_value}"
            )
        current_value = device_proxy.read_attribute(attribute_name).value
        time.sleep(1)
