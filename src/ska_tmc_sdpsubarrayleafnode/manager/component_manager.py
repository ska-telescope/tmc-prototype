"""
This module provided a reference implementation of a BaseComponentManager.

It is provided for explanatory purposes, and to support testing of this
package.
"""
import time

from ska_tmc_common.command_executor import CommandExecutor
from ska_tmc_common.device_info import DeviceInfo
from ska_tmc_common.tmc_component_manager import TmcLeafNodeComponentManager

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
        _update_command_in_progress_callback=None,
        _monitoring_loop=False,
        _event_receiver=True,
        max_workers=5,
        proxy_timeout=500,
        sleep_time=1,
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
            _monitoring_loop,
            _event_receiver,
            max_workers,
            proxy_timeout,
            sleep_time,
        )

        # self._sdp_subarray_dev_name = sdp_subarray_device
        # self._device = SubArrayDeviceInfo(self._sdp_subarray_dev_name, False)
        self.update_device_info(sdp_subarray_dev_name)

        self._event_receiver = None
        if _event_receiver:
            self._event_receiver = SdpSLNEventReceiver(
                self,
                logger,
                proxy_timeout=proxy_timeout,
                sleep_time=sleep_time,
            )

        if _event_receiver:
            self._event_receiver.start()

        self.command_executor = CommandExecutor(
            logger,
            _update_command_in_progress_callback=_update_command_in_progress_callback,
        )

    def stop(self):
        self._event_receiver.stop()

    def get_device(self):
        """
        Return the device info our of the monitoring loop with name dev_name

        :param None:
        :return: a device info
        :rtype: DeviceInfo
        """
        return self._device

    def update_device_info(self, sdp_subarray_dev_name):
        self._sdp_subarray_dev_name = sdp_subarray_dev_name
        self._device = DeviceInfo(self._sdp_subarray_dev_name, False)

    def device_failed(self, exception):
        """
        Set a device to failed and call the relative callback if available

        :param exception: an exception
        :type: Exception
        """
        with self.lock:
            self._device.exception = exception

    def update_event_failure(self):
        with self.lock:
            dev_info = self.get_device()
            # self._device.last_event_arrived = time.time()
            # self._device.update_unresponsive(False)
            dev_info.last_event_arrived = time.time()
            dev_info.update_unresponsive(False)

    def update_device_health_state(self, health_state):
        """
        Update a monitored device health state
        aggregate the health states available

        :param health_state: health state of the device
        :type health_state: HealthState
        """
        with self.lock:
            self._device.healthState = health_state
            self._device.last_event_arrived = time.time()
            self._device.update_unresponsive(False)

    def update_device_state(self, state):
        """
        Update a monitored device state,
        aggregate the states available
        and call the relative callbacks if available

        :param state: state of the device
        :type state: DevState
        """
        with self.lock:
            self._device.state = state
            self._device.last_event_arrived = time.time()
            self._device.update_unresponsive(False)

    def update_device_obs_state(self, obs_state):
        """
        Update a monitored device obs state,
        and call the relative callbacks if available

        :param obs_state: obs state of the device
        :type obs_state: ObsState
        """
        with self.lock:
            dev_info = self.get_device()
            # self._device.obsState = obs_state
            # self._device.last_event_arrived = time.time()
            # self._device.update_unresponsive(False)
            dev_info.obsState = obs_state
            dev_info.last_event_arrived = time.time()
            dev_info.update_unresponsive(False)
