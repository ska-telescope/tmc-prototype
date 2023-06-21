# pylint: disable=abstract-method, arguments-differ
"""
This module implements ComponentManager class for the Sdp Master Leaf Node.
"""
from typing import Tuple

from ska_tango_base.executor import TaskStatus
from ska_tmc_common.device_info import DeviceInfo
from ska_tmc_common.enum import LivelinessProbeType
from ska_tmc_common.exceptions import CommandNotAllowed, DeviceUnresponsive
from ska_tmc_common.tmc_component_manager import TmcLeafNodeComponentManager
from tango import DevState

from ska_tmc_sdpmasterleafnode.commands import Off, On


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
        _adapter_factory,
        logger=None,
        _liveliness_probe=LivelinessProbeType.SINGLE_DEVICE,
        _event_receiver=False,
        max_workers=1,
        proxy_timeout=500,
        sleep_time=1,
        timeout=30,
        _update_availablity_callback=None,
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
            logger,
            _liveliness_probe=_liveliness_probe,
            _event_receiver=False,
            max_workers=max_workers,
            proxy_timeout=proxy_timeout,
            sleep_time=sleep_time,
        )
        self._device = DeviceInfo(sdp_master_dev_name)
        self.sdp_master_dev_name = sdp_master_dev_name
        self._adapter_factory = _adapter_factory
        self.timeout = timeout
        self.update_availablity_callback = _update_availablity_callback
        self.on_command = On(
            self, self.op_state_model, self._adapter_factory, logger
        )

        self.off_command = Off(
            self, self.op_state_model, self._adapter_factory, logger
        )

    @property
    def sdp_master_device_name(self) -> str:
        """Returns device name for the SDP Master Device."""
        return self.sdp_master_dev_name

    @sdp_master_device_name.setter
    def sdp_master_device_name(self, device_name: str) -> None:
        """Sets the device name for SDP Master Device."""
        self.sdp_master_dev_name = device_name

    def update_ping_info(self, ping: int, dev_name: str) -> None:
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

    def _check_if_sdp_master_is_responsive(self) -> None:
        """Checks if SDP Master device is responsive."""

        if self._device is None or self._device.unresponsive:
            raise DeviceUnresponsive(
                f"{self.sdp_master_dev_name} not available"
            )

    def is_command_allowed(self, command_name: str) -> bool:
        """
        Checks whether this command is allowed.
        It checks that the device is in the right state to execute this command
        and that all the components needed for the operation are not
        unresponsive.

        :return: True if this command is allowed

        :rtype: boolean
        """

        if command_name in ["On", "Off"] and self.op_state_model.op_state in [
            DevState.FAULT,
            DevState.UNKNOWN,
        ]:
            raise CommandNotAllowed(
                f"The invocation of the {__class__} command on this "
                + "device is not allowed.\n"
                + "Reason: The current operational state "
                + f"is {self.op_state_model.op_state}."
                + "The command has NOT been executed."
                + "This device will continue with normal operation.",
                self.op_state_model.op_state,
            )
        self._check_if_sdp_master_is_responsive()
        return True

    def submit_on_command(self, task_callback=None) -> Tuple[TaskStatus, str]:
        """Submits the On command for execution.

        :rtype: tuple
        """
        task_status, response = self.submit_task(
            self.on_command.on,
            args=[self.logger],
            task_callback=task_callback,
        )
        self.logger.info("On command queued for execution")
        return task_status, response

    def submit_off_command(self, task_callback=None) -> Tuple[TaskStatus, str]:
        """Submits the Off command for execution.

        :rtype: tuple
        """
        task_status, response = self.submit_task(
            self.off_command.off,
            args=[self.logger],
            task_callback=task_callback,
        )
        self.logger.info("Off command queued for execution")
        return task_status, response
