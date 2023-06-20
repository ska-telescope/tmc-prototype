# pylint: disable=no-member, arguments-renamed, arguments-differ
# pylint: disable=abstract-method
"""
This module provided a reference implementation of a BaseComponentManager.

It is provided for explanatory purposes, and to support testing of this
package.
"""
import time

from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import ObsState

# from ska_tmc_common.command_executor import CommandExecutor
from ska_tmc_common.device_info import SubArrayDeviceInfo
from ska_tmc_common.lrcr_callback import LRCRCallback
from ska_tmc_common.tmc_component_manager import TmcLeafNodeComponentManager

from ska_tmc_sdpsubarrayleafnode.liveliness_probe import (
    LivelinessProbeType,
    SingleDeviceLivelinessProbe,
)
from ska_tmc_sdpsubarrayleafnode.manager.event_receiver import (
    SdpSLNEventReceiver,
)


class SdpSLNComponentManager(TmcLeafNodeComponentManager):
    """
    A component manager for The SDP Subarray Leaf Node component.

    It supports:

    * Monitoring its component, e.g. detect that it has been turned off
      or on
    """

    def __init__(
        self,
        sdp_subarray_dev_name,
        op_state_model,
        logger=None,
        _liveliness_probe=LivelinessProbeType.SINGLE_DEVICE,
        _update_device_callback=None,
        _update_sdp_subarray_obs_state_callback=None,
        _update_lrcr_callback=None,
        monitoring_loop=False,
        event_receiver=True,
        max_workers=5,
        proxy_timeout=500,
        sleep_time=1,
        timeout=30,
        _update_availablity_callback=None,
        command_timeout: int = 15,
    ):
        """
        Initialise a new ComponentManager instance.

        :param op_state_model: the op state model used by this component
            manager
        :param logger: a logger for this component manager
        :param _component: allows setting of the component to be
            managed; for testing purposes only
        """
        super().__init__(
            op_state_model,
            logger,
            monitoring_loop,
            event_receiver,
            max_workers,
            proxy_timeout,
            sleep_time,
        )

        self.update_device_info(sdp_subarray_dev_name)
        if event_receiver:
            self.event_receiver = SdpSLNEventReceiver(
                self,
                logger,
                proxy_timeout=proxy_timeout,
                sleep_time=sleep_time,
            )
            self.event_receiver.start()

        self.timeout = timeout
        self._update_availablity_callback = _update_availablity_callback

        self.liveliness_probe = SingleDeviceLivelinessProbe(
            self,
            logger=self.logger,
            proxy_timeout=500,
            sleep_time=1,
        )
        self.command_timeout = command_timeout
        self.assign_id = None
        # pylint: enable=line-too-long
        self.long_running_result_callback = LRCRCallback(self.logger)
        self._update_sdp_subarray_obs_state_callback = (
            _update_sdp_subarray_obs_state_callback
        )

        self.update_lrcr_callback = _update_lrcr_callback
        self._lrc_result = ("", "")

        self.start_liveliness_probe(LivelinessProbeType.SINGLE_DEVICE)

    def stop(self):
        "Stop the liveliness probe and event receiver."
        self.stop_liveliness_probe()
        self._event_receiver.stop()

    def get_device(self):
        """
        Return the device info our of the monitoring loop with name dev_name

        :param None:
        :return: a device info
        :rtype: DeviceInfo
        """
        return self._device

    def start_liveliness_probe(self, lp: LivelinessProbeType) -> None:
        """Starts Liveliness Probe for the given device.

        :param lp: enum of class LivelinessProbeType
        """
        try:
            if lp == LivelinessProbeType.SINGLE_DEVICE:
                self.liveliness_probe.start()
            else:
                self.logger.warning("Liveliness Probe is not running")
        except Exception as e:
            self.logger.error(
                f"An error occurred during\
                    Liveliness Probe start: {str(e)}"
            )

    def stop_liveliness_probe(self) -> None:
        """Stops the liveliness probe"""
        if self.liveliness_probe:
            self.liveliness_probe.stop()

    def update_device_info(self, sdp_subarray_dev_name):
        """Updates the device info"""
        self._sdp_subarray_dev_name = sdp_subarray_dev_name
        self._device = SubArrayDeviceInfo(self._sdp_subarray_dev_name, False)

    def update_input_parameter(self):
        """Update input parameter"""
        with self.lock:
            self.input_parameter.update(self)

    def update_event_failure(self):
        """Update event failures"""
        with self.lock:
            dev_info = self.get_device()
            dev_info.last_event_arrived = time.time()
            dev_info.update_unresponsive(False)

    def update_device_obs_state(self, obs_state):
        """
        Update a monitored device obs state,
        and call the relative callbacks if available

        :param dev_name: name of the device
        :type dev_name: str
        :param obs_state: obs state of the device
        :type obs_state: ObsState
        """
        self.logger.info(f"Obs State value {obs_state}")
        with self.lock:
            dev_info = self.get_device()
            dev_info.obs_state = obs_state
            dev_info.last_event_arrived = time.time()
            dev_info.update_unresponsive(False)
            self.logger.info(f"Obs State value updated to {obs_state}")
            if self._update_sdp_subarray_obs_state_callback:
                self._update_sdp_subarray_obs_state_callback(obs_state)

    def device_failed(
        self, device_info, exception
    ):  # pylint: disable=arguments-differ
        """
        Set a device to failed and call the relative callback if available

        :param device_info: a device info
        :type device_info: DeviceInfo
        :param exception: an exception
        :type: Exception
        """
        device_info.update_unresponsive(True, exception)

        with self.lock:
            if self._update_availablity_callback is not None:
                self._update_availablity_callback(False)

    def update_ping_info(self, ping: int) -> None:
        """
        Update a device with the correct ping information.

        :param dev_name: name of the device
        :type dev_name: str
        :param ping: device response time
        :type ping: int
        """
        with self.lock:
            self._device.ping = ping
            self._device.update_unresponsive(False)
            if self._update_availablity_callback:
                self._update_availablity_callback(True)

    def get_obs_state(self) -> ObsState:
        """
        Get Current device obsState
        """
        return self.get_device().obs_state

    def update_command_result(self, command_name, value: str):
        """Updates the long running command result callback"""
        self.logger.info(
            "Recieved longRunningCommandResult event with value: %s",
            value,
        )
        try:
            # Ignoring ResultCode events
            int(value)
        except ValueError:
            if command_name == "AssignResources":
                self.logger.info(
                    "Updating LRCRCallback with value: %s for Assign",
                    value,
                )
                self.long_running_result_callback(
                    self.assign_id, ResultCode.FAILED, exception_msg=value
                )

    @property
    def lrc_result(self) -> tuple[str, str]:
        """
        Returns the longRunningCommandResult attribute.

        :return: the longRunningCommandResult
        :rtype: spectrum
        """
        return self._lrc_result

    @lrc_result.setter
    def lrc_result(self, value: str) -> None:
        """
        Sets the longRunningCommandResult value

        :param value: the new longRunningCommandResult value
        :type value: str
        """
        if self._lrc_result != value:
            self._lrc_result = value
            self._invoke_lrcr_callback()

    def _invoke_lrcr_callback(self):
        """This method calls longRunningCommandResult callback"""
        if self.update_lrcr_callback is not None:
            self.update_lrcr_callback(self._lrc_result)

    def add_to_queue(self, handler, argin=None):
        """This methods add command to queue"""
        unique_id = self.command_executor.enqueue_command(handler, argin)
        self.assign_id = unique_id
        return unique_id
