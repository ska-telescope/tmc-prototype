# pylint: disable=arguments-differ, no-value-for-parameter
"""
SDP Subarray Leaf node is to monitor the SDP Subarray and issue control
actions during an observation.
It also acts as a SDP contact point for Subarray Node for observation execution
"""

# pylint: disable=attribute-defined-outside-init
import tango
from ska_control_model import HealthState
from ska_tango_base import SKABaseDevice
from ska_tango_base.commands import ResultCode, SubmittedSlowCommand
from ska_tango_base.control_model import ObsState
from ska_tmc_common.enum import LivelinessProbeType
from tango import ApiUtil, AttrWriteType, DebugIt
from tango.server import attribute, command, device_property, run

from ska_tmc_sdpsubarrayleafnode import release
from ska_tmc_sdpsubarrayleafnode.manager import SdpSLNComponentManager


class SdpSubarrayLeafNode(SKABaseDevice):
    """
    SDP Subarray Leaf node is to monitor the SDP Subarray and issue control
    actions during an observation.
    """

    def init_device(self):
        super().init_device()
        self._sdp_subarray_obs_state = ObsState.EMPTY
        self.set_change_event("sdpSubarrayObsState", True)
        self._command_result = ("", "")
        self.set_change_event("longRunningCommandResult", True)
        self._issubsystemavailable = False
        self.set_change_event("isSubsystemAvailable", True, False)

    # -----------------
    # Device Properties
    # -----------------
    SdpSubarrayFQDN = device_property(
        dtype="str", doc="FQDN of the SDP Subarray Tango Device Server."
    )

    SleepTime = device_property(dtype="DevFloat", default_value=1)
    TimeOut = device_property(dtype="DevFloat", default_value=2)

    # -----------------
    # Attributes
    # -----------------

    isSubsystemAvailable = attribute(
        dtype="DevBoolean",
        access=AttrWriteType.READ,
    )

    lastDeviceInfoChanged = attribute(
        dtype="DevString",
        access=AttrWriteType.READ,
        doc="""Json String representing the last device changed in the
        internal model.""",
    )

    sdpSubarrayDevName = attribute(
        dtype="DevString",
        access=AttrWriteType.READ_WRITE,
    )

    sdpSubarrayObsState = attribute(
        dtype=ObsState,
        access=AttrWriteType.READ,
    )

    # ---------------
    # General methods
    # ---------------

    # pylint: disable=attribute-defined-outside-init
    def update_device_callback(self, dev_info):
        """Updates device callback info"""
        self._LastDeviceInfoChanged = dev_info.to_json()
        self.push_change_event("lastDeviceInfoChanged", dev_info.to_json())

    # pylint: disable=attribute-defined-outside-init
    def update_sdp_subarray_obs_state_callback(
        self, obs_state: ObsState
    ) -> None:
        """Updates SDP Subarray ObsState"""
        self._sdp_subarray_obs_state = obs_state
        self.push_change_event(
            "sdpSubarrayObsState", self._sdp_subarray_obs_state
        )

    def update_lrcr_callback(self, lrc_result):
        """Change event callback for longRunningCommandResult"""
        self.push_change_event("longRunningCommandResult", lrc_result)

    def update_availablity_callback(self, availablity):
        """Change event callback for isSubsystemAvailable"""
        if availablity != self._issubsystemavailable:
            self._issubsystemavailable = availablity
            self.push_change_event(
                "isSubsystemAvailable", self._issubsystemavailable
            )

    class InitCommand(
        SKABaseDevice.InitCommand
    ):  # pylint: disable=too-few-public-methods
        """
        A class for the TMC SdpSubarrayLeafNode's init_device() method.
        """

        def do(self, *args, **kwargs) -> tuple:
            """
            Initializes the attributes and properties of the
            SdpSubarrayLeafNode.

            return:
                A tuple containing a return code and a string message
                indicating status.
                The message is for information purpose only.

            rtype:
                (ResultCode, str)
            """
            super().do()
            device = self._device
            device._build_state = (
                f"{release.name},{release.version},{release.description}"
            )
            device._health_state = HealthState.OK
            device._version_id = release.version
            device._LastDeviceInfoChanged = ""
            device.set_change_event("healthState", True, False)
            device._isSubsystemAvailable = False
            ApiUtil.instance().set_asynch_cb_sub_model(
                tango.cb_sub_model.PUSH_CALLBACK
            )
            device.op_state_model.perform_action("component_on")
            return (ResultCode.OK, "")

    def always_executed_hook(self):
        pass

    def delete_device(self):
        # if the init is called more than once
        # I need to stop all threads
        if hasattr(self, "component_manager"):
            self.component_manager.stop()

    def read_sdpSubarrayDevName(self):
        """Return the sdpsubarraydevname attribute."""
        # return self.component_manager.sdp_subarray_dev_name
        return self.component_manager._sdp_subarray_dev_name

    def write_sdpSubarrayDevName(self, value):
        """Set the sdpsubarraydevname attribute."""
        # self.component_manager.sdp_subarray_dev_name = value
        self.component_manager.update_device_info(value)

    # ------------------
    # Attributes methods
    # ------------------

    def read_isSubsystemAvailable(self):
        """Read method for issubsystemavailable"""
        return self._issubsystemavailable

    def read_lastDeviceInfoChanged(self):
        """Return the last device info change"""
        return self._LastDeviceInfoChanged

    def read_sdpSubarrayObsState(self):
        """Reads the current observation state of the SDP subarray"""
        return self._sdp_subarray_obs_state

    # --------
    # Commands
    # --------

    def is_On_allowed(self):
        """
        Checks whether this command is allowed to be run in current device \
        state. \

        :return: True if this command is allowed to be run in current device \
        state. \

        :rtype: boolean
        """
        return self.component_manager.is_command_allowed("On")

    @command(dtype_out="DevVarLongStringArray")
    @DebugIt()
    def On(self):
        """
        This command invokes On() command on SDP Subarray.
        """
        handler = self.get_command_object("On")
        result_code, unique_id = handler()

        return [result_code], [unique_id]

    def is_Off_allowed(self):
        """
        Checks whether this command is allowed to be run in current \
        device state. \

        :return: True if this command is allowed to be run in current \
        device state. \

        :rtype: boolean
        """
        return self.component_manager.is_command_allowed("Off")

    @command(dtype_out="DevVarLongStringArray")
    @DebugIt()
    def Off(self):
        """
        This command invokes Off() command on SDP Subarray.
        """
        handler = self.get_command_object("Off")
        result_code, unique_id = handler()

        return [result_code], [unique_id]

    def create_component_manager(self):
        """Returns Sdp Subarray Leaf Node component manager object"""
        cm = SdpSLNComponentManager(
            self.SdpSubarrayFQDN,
            logger=self.logger,
            communication_state_callback=None,
            component_state_callback=None,
            _liveliness_probe=LivelinessProbeType.SINGLE_DEVICE,
            _event_receiver=True,
            _update_sdp_subarray_obs_state_callback=(
                self.update_sdp_subarray_obs_state_callback
            ),
            _update_lrcr_callback=self.update_lrcr_callback,
            sleep_time=self.SleepTime,
            timeout=self.TimeOut,
            _update_availablity_callback=self.update_availablity_callback,
        )
        return cm

    # pylint: disable=unexpected-keyword-arg
    def init_command_objects(self) -> None:
        """
        Initialises the command handlers for commands supported by this
        device.
        """
        super().init_command_objects()

        for command_name, method_name in [("On", "on"), ("Off", "off")]:
            self.register_command_object(
                command_name,
                SubmittedSlowCommand(
                    command_name,
                    self._command_tracker,
                    self.component_manager,
                    method_name,
                    logger=None,
                ),
            )


# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    """
    Runs the SdpSubarrayLeafNode Tango device.
    :param args: Arguments internal to TANGO

    :param kwargs: Arguments internal to TANGO

    :return: integer. Exit code of the run method.
    """
    return run((SdpSubarrayLeafNode,), args=args, **kwargs)


if __name__ == "__main__":
    main()
