# pylint: disable=attribute-defined-outside-init, too-many-ancestors

"""Helper device for SdpSubarray device"""
import json
import logging
import threading
import time
from typing import Tuple

import tango
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import ObsState
from ska_tango_base.subarray import SKASubarray
from ska_tmc_common import CommandNotAllowed, FaultType, HelperSubArrayDevice
from ska_tmc_common.test_helpers.constants import (
    ABORT,
    ASSIGN_RESOURCES,
    CONFIGURE,
    END,
    END_SCAN,
    OFF,
    ON,
    RELEASE_ALL_RESOURCES,
    RELEASE_RESOURCES,
    RESTART,
    SCAN,
)
from tango import AttrWriteType, DevState
from tango.server import attribute, command, run

logger = logging.getLogger(__name__)


# pylint: disable=invalid-name
class HelperSdpSubarray(HelperSubArrayDevice):
    """A  helper SdpSubarray device for triggering state changes with a
    command.
    It can be used to mock SdpSubarray's bahavior to test error propagation
    from SdpSubarray to SdpSubarrayLeafNode in case of command failure"""

    def init_device(self):
        super().init_device()
        self.lock = threading.Lock()
        self._delay = 2
        self._obs_state = ObsState.EMPTY
        self._state = DevState.OFF
        self._receive_addresses = json.dumps(
            {
                "science_A": {
                    "host": [[0, "192.168.0.1"], [2000, "192.168.0.1"]],
                    "port": [[0, 9000, 1], [2000, 9000, 1]],
                },
                "target:a": {
                    "vis0": {
                        "function": "visibilities",
                        "host": [
                            [
                                0,
                                "proc-pb-test-20220916-00000-test-"
                                + "receive-0.receive.test-sdp",
                            ]
                        ],
                        "port": [[0, 9000, 1]],
                    }
                },
                "calibration:b": {
                    "vis0": {
                        "function": "visibilities",
                        "host": [
                            [
                                0,
                                "proc-pb-test-20220916-00000-test-"
                                + "receive-0.receive.test-sdp",
                            ]
                        ],
                        "port": [[0, 9000, 1]],
                    }
                },
            }
        )

        self.push_change_event("receiveAddresses", self._receive_addresses)

    class InitCommand(SKASubarray.InitCommand):
        """A class for the HelperSubarrayDevice's init_device() "command"."""

        def do(self) -> Tuple[ResultCode, str]:
            """
            Stateless hook for device initialisation.
            :return: ResultCode and message
            """
            super().do()
            self._device.set_change_event("receiveAddresses", True, False)
            self._device.set_change_event("healthState", True, False)
            self._device.set_change_event(
                "longRunningCommandResult", True, False
            )
            self._device.set_change_event("commandCallInfo", True, False)
            return ResultCode.OK, ""

    receiveAddresses = attribute(
        label="Receive addresses",
        dtype=str,
        access=AttrWriteType.READ,
        doc="Host addresses for visibility receive as a JSON string.",
    )
    defective = attribute(dtype=str, access=AttrWriteType.READ)

    delay = attribute(dtype=int, access=AttrWriteType.READ)

    def read_delay(self) -> int:
        """
        This method is used to read the attribute value for delay.
        :return: delay
        """
        return self._delay

    @command(dtype_in=str, doc_in="Set the receive_addresses")
    def SetDirectreceiveAddresses(self, argin: str) -> None:
        """Set the receivedAddresses"""
        self._receive_addresses = argin
        self.push_change_event("receiveAddresses", argin)

    def read_receiveAddresses(self):
        """
        Returns receive addresses.
        :return: receiveAddresses
        """
        return self._receive_addresses

    def read_defective(self) -> str:
        """
        Returns defective status of devices
        :return: defective parameters
        :rtype: str
        """
        return json.dumps(self.defective_params)

    def push_obs_state_event(self, obs_state: ObsState):
        """Place holder method. This method will be implemented in the child
        classes."""
        with self.lock:
            self._obs_state = obs_state
            self.push_change_event("obsState", self._obs_state)

    def update_device_obsstate(self, obs_state: ObsState):
        """Updates the device obsState"""
        with tango.EnsureOmniThread():
            with self.lock:
                self._obs_state = obs_state
                self.push_obs_state_event(self._obs_state)

    def is_On_allowed(self) -> bool:
        """
        Check if command On is allowed in the current device
        state.

        :return: ``True`` if the command is allowed
        :rtype: bool
        :raises CommandNotAllowed: command is not allowed
        """
        if self.defective_params["enabled"]:
            if (
                self.defective_params["fault_type"]
                == FaultType.COMMAND_NOT_ALLOWED
            ):
                self.logger.info(
                    "Device is defective, cannot process command."
                )
                raise CommandNotAllowed(self.defective_params["error_message"])
        self.logger.info("On Command is allowed")
        return True

    @command()
    def On(self):
        self.update_command_info(ON, "")
        if self.defective_params["enabled"]:
            self.induce_fault(
                "On",
            )
        else:
            self.set_state(DevState.ON)
            self.push_change_event("State", self.dev_state())
            self.push_command_result(ResultCode.OK, "On")

    def is_Off_allowed(self) -> bool:
        """
        Check if command Off is allowed in the current device
        state.

        :return: ``True`` if the command is allowed
        :rtype: bool
        :raises CommandNotAllowed: command is not allowed
        """
        if self.defective_params["enabled"]:
            if (
                self.defective_params["fault_type"]
                == FaultType.COMMAND_NOT_ALLOWED
            ):
                logger.info("Device is defective, cannot process command.")
                raise CommandNotAllowed(self.defective_params["error_message"])
        self.logger.info("Off Command is allowed")
        return True

    @command()
    def Off(self):
        self.update_command_info(OFF, "")
        if self.defective_params["enabled"]:
            self.induce_fault(
                "Off",
            )
        else:
            self.set_state(DevState.OFF)
            self.push_change_event("State", self.dev_state())
            self.push_command_result(ResultCode.OK, "Off")

    def is_AssignResources_allowed(self):
        """
        Check if command `AssignResources` is allowed in the current device
        state.

        :return: ``True`` if the command is allowed
        :rtype: boolean
        """
        self.logger.info("AssignResources Command is allowed")
        return True

    @command(
        dtype_in=("str"),
        doc_in="The input string in JSON format.",
    )
    def AssignResources(self, argin):
        """
        This method invokes AssignResources command on SdpSubarray
        device.
        :return: None
        :raises throw_exception: when input json is wrong
        """
        initial_obstate = self._obs_state
        self.logger.info(
            "Initial obsstate of SdpSubarray for AssignResources command is:"
            + "%s",
            initial_obstate,
        )
        self.update_command_info(ASSIGN_RESOURCES, argin)
        input_json = json.loads(argin)
        if "eb_id" not in input_json["execution_block"]:
            self.logger.info("Missing eb_id in the AssignResources input json")
            raise tango.Except.throw_exception(
                "Incorrect input json string",
                "Missing eb_id in the AssignResources input json",
                "SdpSubarry.AssignResources()",
                tango.ErrSeverity.ERR,
            )

        self._obs_state = ObsState.RESOURCING
        self.push_obs_state_event(self._obs_state)

        # if eb_id in JSON is invalid, SDP Subarray
        # remains in obsState=RESOURCING and raises exception
        eb_id = input_json["execution_block"]["eb_id"]
        invalid_eb_id = "eb-xxx"
        if eb_id.startswith(invalid_eb_id):
            self.logger.info("eb_id is invalid")

            raise tango.Except.throw_exception(
                "Incorrect input json string",
                "Invalid eb_id in the AssignResources input json",
                "SdpSubarry.AssignResources()",
                tango.ErrSeverity.ERR,
            )

        # if receive nodes not present in JSON, SDP Subarray moves to
        # obsState=EMPTY and raises exception
        if input_json["resources"]["receive_nodes"] == 0:
            self.logger.info(
                "Missing receive nodes in the AssignResources input json"
            )
            # Return to the initial obsState
            self._obs_state = initial_obstate
            # Wait before pushing obsState EMPTY event
            time.sleep(1)
            self.push_obs_state_event(self._obs_state)
            raise tango.Except.throw_exception(
                "Incorrect input json string",
                "Missing receive nodes in the AssignResources input json",
                "SdpSubarry.AssignResources()",
                tango.ErrSeverity.ERR,
            )

        # TODO: Keeping below condition for now as many repositories are
        # using it. However this method should not be used for inducing fault
        # on SDP Subarray. Need to remove it once all the instances in other
        # repositories are updated
        if self.defective_params["enabled"]:
            return self.induce_fault(
                "AssignResources",
            )

        thread = threading.Timer(
            self._command_delay_info[ASSIGN_RESOURCES],
            self.update_device_obsstate,
            args=[ObsState.IDLE],
        )

        thread.start()
        self.push_command_result(ResultCode.OK, "AssignResources")
        return None

    def is_ReleaseResources_allowed(self):
        """
        Check if command `ReleaseResources` is allowed in the current device
        state.

        :return: ``True`` if the command is allowed
        :rtype: boolean
        :raises CommandNotAllowed: command is not allowed
        """
        if self.defective_params["enabled"]:
            if (
                self.defective_params["fault_type"]
                == FaultType.COMMAND_NOT_ALLOWED
            ):
                raise CommandNotAllowed(self.defective_params["error_message"])
        self.logger.info("ReleaseResource Command is allowed")
        return True

    @command()
    def ReleaseResources(self):
        """This method invokes ReleaseResources command on SdpSubarray
        device."""
        self.update_command_info(RELEASE_RESOURCES)
        if self.defective_params["enabled"]:
            self.induce_fault(
                "ReleaseResources",
            )
        else:
            self._obs_state = ObsState.RESOURCING
            self.push_obs_state_event(self._obs_state)

            thread = threading.Timer(
                self._command_delay_info[RELEASE_RESOURCES],
                self.update_device_obsstate,
                args=[ObsState.IDLE],
            )
            thread.start()
            self.logger.debug(
                "ReleaseResources command invoked, obsState will transition to"
                + "IDLE, current obsState is %s",
                self._obs_state,
            )
            self.push_command_result(ResultCode.OK, "ReleaseResources")

    def is_ReleaseAllResources_allowed(self):
        """
        Check if command `ReleaseAllResources` is allowed in the current
        device state.

        :return: ``True`` if the command is allowed
        :rtype: boolean
        :raises CommandNotAllowed: command is not allowed
        """
        if self.defective_params["enabled"]:
            if (
                self.defective_params["fault_type"]
                == FaultType.COMMAND_NOT_ALLOWED
            ):
                self.logger.info(
                    "Device is defective, cannot process command."
                )
                raise CommandNotAllowed(self.defective_params["error_message"])
        self.logger.info("ReleaseAllResources Command is allowed")
        return True

    @command()
    def ReleaseAllResources(self):
        """This method invokes ReleaseAllResources command on SdpSubarray
        device."""
        self.update_command_info(RELEASE_ALL_RESOURCES)
        if self.defective_params["enabled"]:
            self.induce_fault(
                "ReleaseAllResources",
            )
        else:
            self._obs_state = ObsState.RESOURCING
            self.push_obs_state_event(self._obs_state)
           
            thread = threading.Timer(
                self._command_delay_info[RELEASE_ALL_RESOURCES],
                self.update_device_obsstate,
                args=[ObsState.EMPTY],
            )
            thread.start()
            self.push_command_result(ResultCode.OK, "ReleaseAllResources")

    def is_Configure_allowed(self):
        """
        Check if command `Configure` is allowed in the current device state.

        :return: ``True`` if the command is allowed
        :rtype: boolean
        :raises CommandNotAllowed: command is not allowed
        """
        if self.defective_params["enabled"]:
            if (
                self.defective_params["fault_type"]
                == FaultType.COMMAND_NOT_ALLOWED
            ):
                self.logger.info(
                    "Device is defective, cannot process command."
                )
                raise CommandNotAllowed(self.defective_params["error_message"])
        self.logger.info("Configure Command is allowed")
        return True

    @command(
        dtype_in=("str"),
        doc_in="The input string in JSON format.",
    )
    def Configure(self, argin):
        """
        This method invokes Configure command on SdpSubarray device.
        :raises throw_exception: when input json is wrong
        """
        self.update_command_info(CONFIGURE, argin)
        input_json = json.loads(argin)
        if "scan_type" not in input_json:
            self.logger.info("Missing scan_type in the Configure input json")
            raise tango.Except.throw_exception(
                "Incorrect input json string",
                "Missing scan_type in the Configure input json",
                "SdpSubarry.Configure()",
                tango.ErrSeverity.ERR,
            )

        self._obs_state = ObsState.CONFIGURING
        self.push_obs_state_event(self._obs_state)

        # if scan_type in JSON is invalid , SDP Subarray moves to
        # obsState=IDLE and raises exception
        scan_type = input_json["scan_type"]
        invalid_scan_type = "xxxxxxx_X"
        if scan_type == invalid_scan_type:
            self._obs_state = ObsState.CONFIGURING
            self.push_obs_state_event(self._obs_state)
            self.logger.info("Wrong scan_type in the Configure input json")
            self._obs_state = ObsState.IDLE
            with tango.EnsureOmniThread():
                thread = threading.Timer(
                    1, self.push_obs_state_event, args=[self._obs_state]
                )
                thread.start()
            raise tango.Except.throw_exception(
                "Incorrect input json string",
                "Wrong scan_type in the Configure input json",
                "SdpSubarry.Configure()",
                tango.ErrSeverity.ERR,
            )

        # if scan_type in JSON does not have valid value, SDP Subarray
        # remains in obsState=CONFIGURING and raises exception
        scan_type = input_json["scan_type"]
        invalid_scan_type = "zzzzzzz_Z"
        if scan_type == invalid_scan_type:
            self.logger.info("Wrong scan_type in the Configure input json")
            self._obs_state = ObsState.CONFIGURING
            self.push_obs_state_event(self._obs_state)
            raise tango.Except.throw_exception(
                "Incorrect input json string",
                "Wrong scan_type in the Configure input json",
                "SdpSubarry.Configure()",
                tango.ErrSeverity.ERR,
            )

        if self.defective_params["enabled"]:
            self.induce_fault(
                "Configure",
            )
        else:
            if self._state_duration_info:
                self._follow_state_duration()
            else:
                self._obs_state = ObsState.CONFIGURING
                self.push_obs_state_event(self._obs_state)

                thread = threading.Timer(
                    self._command_delay_info[CONFIGURE],
                    self.update_device_obsstate,
                    args=[ObsState.READY],
                )
                thread.start()
                self.push_command_result(ResultCode.OK, "Configure")

    def is_Scan_allowed(self):
        """
        Check if command `Scan` is allowed in the current device state.

        :return: ``True`` if the command is allowed
        :rtype: boolean
        :raises CommandNotAllowed: command is not allowed
        """
        if self.defective_params["enabled"]:
            if (
                self.defective_params["fault_type"]
                == FaultType.COMMAND_NOT_ALLOWED
            ):
                self.logger.info(
                    "Device is defective, cannot process command."
                )
                raise CommandNotAllowed(self.defective_params["error_message"])
        self.logger.info("Scan Command is allowed")
        return True

    @command(
        dtype_in=("str"),
        doc_in="The input string in JSON format.",
    )
    def Scan(self, argin):
        """
        This method invokes Scan command on SdpSubarray device.
        :raises throw_exception: when input json is wrong
        """
        self.update_command_info(SCAN, argin)
        input_json = json.loads(argin)
        if "scan_id" not in input_json:
            self.logger.info("Missing scan_id in the Scan input json")
            raise tango.Except.throw_exception(
                "Incorrect input json string",
                "Missing scan_id in the Scan input json",
                "SdpSubarry.Configure()",
                tango.ErrSeverity.ERR,
            )
        if self.defective_params["enabled"]:
            self.induce_fault(
                "Scan",
            )
        else:
            self._obs_state = ObsState.SCANNING
            self.push_obs_state_event(self._obs_state)
            self.push_command_result(ResultCode.OK, "Scan")

    def is_EndScan_allowed(self):
        """
        Check if command `EndScan` is allowed in the current device state.

        :return: ``True`` if the command is allowed
        :rtype: boolean
        :raises CommandNotAllowed: command is not allowed
        """
        if self.defective_params["enabled"]:
            if (
                self.defective_params["fault_type"]
                == FaultType.COMMAND_NOT_ALLOWED
            ):
                self.logger.info(
                    "Device is defective, cannot process command."
                )
                raise CommandNotAllowed(self.defective_params["error_message"])
        self.logger.info("EndScan Command is allowed")
        return True

    @command()
    def EndScan(self):
        """This method invokes EndScan command on SdpSubarray device."""
        self.update_command_info(END_SCAN)
        if self.defective_params["enabled"]:
            self.induce_fault(
                "EndScan",
            )
        else:
            self._obs_state = ObsState.READY
            self.push_obs_state_event(self._obs_state)
            self.push_command_result(ResultCode.OK, "EndScan")

    def is_End_allowed(self):
        """
        Check if command `End` is allowed in the current device state.

        :return: ``True`` if the command is allowed
        :rtype: boolean
        :raises CommandNotAllowed: command is not allowed
        """
        if self.defective_params["enabled"]:
            if (
                self.defective_params["fault_type"]
                == FaultType.COMMAND_NOT_ALLOWED
            ):
                self.logger.info(
                    "Device is defective, cannot process command."
                )
                raise CommandNotAllowed(self.defective_params["error_message"])
        return True

    @command()
    def End(self):
        """This method invokes End command on SdpSubarray device."""
        self.update_command_info(END)
        if self.defective_params["enabled"]:
            self.induce_fault(
                "End",
            )
        else:
            if self._state_duration_info:
                self._follow_state_duration()
            else:

                thread = threading.Timer(
                    self._command_delay_info[END],
                    self.update_device_obsstate,
                    args=[ObsState.IDLE],
                )
                thread.start()
                self.logger.debug(
                    "End command invoked, obsState will transition to IDLE,"
                    + "current obsState is %s",
                    self._obs_state,
                )
                self.push_command_result(ResultCode.OK, "End")

    def is_Abort_allowed(self):
        """
        Check if command `Abort` is allowed in the current device state.

        :return: ``True`` if the command is allowed
        :rtype: boolean
        :raises CommandNotAllowed: command is not allowed
        """
        if self.defective_params["enabled"]:
            if (
                self.defective_params["fault_type"]
                == FaultType.COMMAND_NOT_ALLOWED
            ):
                self.logger.info(
                    "Device is defective, cannot process command."
                )
                raise CommandNotAllowed(self.defective_params["error_message"])
        return True

    @command()
    def Abort(self):
        """This method invokes Abort command on SdpSubarray device."""
        self.update_command_info(ABORT)
        if self.defective_params["enabled"]:
            self.induce_fault(
                "Abort",
            )
        else:
            self._obs_state = ObsState.ABORTING
            self.push_obs_state_event(self._obs_state)
            
            thread = threading.Timer(
                self._command_delay_info[ABORT],
                self.update_device_obsstate,
                args=[ObsState.ABORTED],
            )
            thread.start()
            self.push_command_result(ResultCode.OK, "Abort")

    def is_Restart_allowed(self):
        """
        Check if command `Restart` is allowed in the current device state.

        :return: ``True`` if the command is allowed
        :rtype: boolean
        :raises CommandNotAllowed: command is not allowed
        """
        if self.defective_params["enabled"]:
            if (
                self.defective_params["fault_type"]
                == FaultType.COMMAND_NOT_ALLOWED
            ):
                self.logger.info(
                    "Device is defective, cannot process command."
                )
                raise CommandNotAllowed(self.defective_params["error_message"])
        return True

    @command()
    def Restart(self):
        """This method invokes Restart command on SdpSubarray device."""
        self.update_command_info(RESTART)
        if self.defective_params["enabled"]:
            self.induce_fault(
                "Restart",
            )
        else:
            self._obs_state = ObsState.RESTARTING
            self.push_obs_state_event(self._obs_state)

            thread = threading.Timer(
                self._command_delay_info[RESTART],
                self.update_device_obsstate,
                args=[ObsState.EMPTY],
            )
            thread.start()
            self.logger.debug(
                "Restart command invoked, obsState will transition to EMPTY,"
                + "current obsState is %s",
                self._obs_state,
            )
            self.push_command_result(ResultCode.OK, "Restart")


def main(args=None, **kwargs):
    """
    Runs the HelperSdpSubarray Tango device.
    :param args: Arguments internal to TANGO

    :param kwargs: Arguments internal to TANGO

    :return: integer. Exit code of the run method.
    """
    return run((HelperSdpSubarray,), args=args, **kwargs)


if __name__ == "__main__":
    main()
