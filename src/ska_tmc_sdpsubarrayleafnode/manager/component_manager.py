# pylint: disable=no-member
# pylint: disable=abstract-method
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
        _update_device_callback=None,
        update_command_in_progress_callback=None,
        monitoring_loop=False,
        event_receiver=True,
        max_workers=5,
        proxy_timeout=500,
        sleep_time=1,
        time_out=30,
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

        # pylint: disable=line-too-long
        self.command_executor = CommandExecutor(
            logger,
            _update_command_in_progress_callback=update_command_in_progress_callback,  # noqa:E501
        )
        self.time_out = time_out
        # pylint: enable=line-too-long

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
        """Updates the device info"""
        self._sdp_subarray_dev_name = sdp_subarray_dev_name
        self._device = DeviceInfo(self._sdp_subarray_dev_name, False)

    def device_failed(self, exception):
        """
        Return the list of the checked monitored devices

        :return: list of the checked monitored devices
        """
        result = []
        for dev in self.component.devices:
            if dev.unresponsive:
                result.append(dev)
                continue
            if dev.ping > 0:
                result.append(dev)
                continue
            if dev.last_event_arrived is not None:
                result.append(dev)
                continue
        return result

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
        with self.lock:
            dev_info = self.get_device()
            dev_info.obs_state = obs_state
            dev_info.last_event_arrived = time.time()
            dev_info.update_unresponsive(False)
