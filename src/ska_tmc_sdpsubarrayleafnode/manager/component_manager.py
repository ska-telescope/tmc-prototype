# pylint: disable=no-member
# pylint: disable=abstract-method
"""
This module provided a reference implementation of a BaseComponentManager.

It is provided for explanatory purposes, and to support testing of this
package.
"""
import time

from ska_tmc_common.command_executor import CommandExecutor
from ska_tmc_common.device_info import SubArrayDeviceInfo
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
        update_command_in_progress_callback=None,
        monitoring_loop=False,
        event_receiver=True,
        max_workers=5,
        proxy_timeout=500,
        sleep_time=1,
        timeout=30,
        _update_availablity_callback=None,
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
        self.timeout = timeout
        self._update_availablity_callback = _update_availablity_callback

        self.liveliness_probe_object = SingleDeviceLivelinessProbe(
            self,
            logger=self.logger,
            proxy_timeout=500,
            sleep_time=1,
        )
        # pylint: enable=line-too-long

        self.start_liveliness_probe(LivelinessProbeType.SINGLE_DEVICE)
        # self.stop_liveliness_probe()

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

    def start_liveliness_probe(self, lp: LivelinessProbeType) -> None:
        """Starts Liveliness Probe for the given device.

        :param lp: enum of class LivelinessProbeType
        """
        if lp == LivelinessProbeType.SINGLE_DEVICE:
            self.liveliness_probe_object.start()

        else:
            self.logger.warning("Liveliness Probe is not running")

    def stop_liveliness_probe(self) -> None:
        """Stops the liveliness probe"""
        if self.liveliness_probe_object:
            self.liveliness_probe_object.stop()

    def update_device_info(self, sdp_subarray_dev_name):
        """Updates the device info"""
        self._sdp_subarray_dev_name = sdp_subarray_dev_name
        self._device = SubArrayDeviceInfo(self._sdp_subarray_dev_name, False)

    # def device_failed(self, exception):
    #     """
    #     Return the list of the checked monitored devices

    #     :return: list of the checked monitored devices
    #     """
    #     result = []
    #     for dev in self.component.devices:
    #         if dev.unresponsive:
    #             result.append(dev)
    #             continue
    #         if dev.ping > 0:
    #             result.append(dev)
    #             continue
    #         if dev.last_event_arrived is not None:
    #             result.append(dev)
    #             continue
    #     return result

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
        self.logger.info("Inside device_failed  ")
        device_info.update_unresponsive(True, exception)

        with self.lock:
            if self._update_availablity_callback is not None:
                self._update_availablity_callback(False)
            else:
                print("inside device not found")

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
            if self._update_availablity_callback is not None:
                self.logger.info(
                    "Calling update_availablity_callback from update_ping_info"
                )
                self._update_availablity_callback(True)
