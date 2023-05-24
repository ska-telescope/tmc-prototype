# pylint: disable=abstract-method
"""
This module implements ComponentManager class for the Sdp Master Leaf Node.
"""
from ska_tmc_common.command_executor import CommandExecutor
from ska_tmc_common.device_info import DeviceInfo
from ska_tmc_common.tmc_component_manager import TmcLeafNodeComponentManager

from ska_tmc_sdpsubarrayleafnode.liveliness_probe import (
    LivelinessProbeType,
    SingleDeviceLivelinessProbe,
)


class SdpMLNComponentManager(TmcLeafNodeComponentManager):
    """
    A component manager for The SDP Master Leaf Node component.

    It supports:

    * Monitoring its component, e.g. detect that it has been turned off
      or on
    * Controlling the behaviour of SDP Master.
    """

    def __init__(
        self,
        sdp_master_dev_name,
        op_state_model,
        logger=None,
        _update_command_in_progress_callback=None,
        _monitoring_loop=False,
        _event_receiver=False,
        max_workers=1,
        proxy_timeout=500,
        sleep_time=1,
        timeout=30,
        _update_availablity_callback=None,
        _liveliness_probe=LivelinessProbeType.SINGLE_DEVICE,
    ):
        """
        Initialise a new ComponentManager instance.

        :param op_state_model: the op state model used by this component
            manager
        :param _component: Optional. Allows setting of the component to be
            managed; for testing purposes only
        :param logger: Optional. A logger for this component manager
        :param _monitoring_loop: Optional. Monitoring loop for the component
        manager
        :param _event_receiver: Optional. Object of EventReceiver class
        :param max_workers: Optional. Maximum worker threads for monitoring
        purpose. Default 1
        :param proxy_timeout: Optional. Time period to wait for event and
        responses. Default 500 milliseconds
        :param sleep_time: Optional. Sleep time between reties. Default 1 Sec
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
        self.sdp_master_dev_name = sdp_master_dev_name
        # pylint: disable=line-too-long
        self._command_executor = CommandExecutor(
            logger,
            _update_command_in_progress_callback=_update_command_in_progress_callback,  # noqa:E501
        )
        self.logger = logger
        self._device = DeviceInfo(sdp_master_dev_name)
        self.timeout = timeout
        # pylint: enable=line-too-long
        self.update_availablity_callback = _update_availablity_callback
        self.liveliness_probe = SingleDeviceLivelinessProbe(
            self,
            logger=self.logger,
            proxy_timeout=500,
            sleep_time=1,
        )

        self.start_liveliness_probe(LivelinessProbeType.SINGLE_DEVICE)

    def stop(self):
        self.stop_liveliness_probe()

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
            if self.update_availablity_callback is not None:
                self.logger.info(
                    "Calling update_availablity_callback from update_ping_info"
                )
                self.update_availablity_callback(True)

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
            if self.update_availablity_callback is not None:
                self.update_availablity_callback(False)
