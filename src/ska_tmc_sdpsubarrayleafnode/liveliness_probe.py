"""
This module monitors sub devices.
Inherited from liveliness probe functionality
"""
import threading
from concurrent import futures
from enum import IntEnum
from logging import Logger
from time import sleep

import tango
from ska_tmc_common.dev_factory import DevFactory
from ska_tmc_common.device_info import DeviceInfo


# pylint: disable=fixme
# TODO:This liveliness implementation setup on sdp leaf nodes,
# will get removed once the sdp leaf nodes utilises latest base
# classes and there in latest ska-tmc-common package
class BaseLivelinessProbe:
    """
    The BaseLivelinessProbe class has the responsibility
    to monitor the sub devices.

    It is inherited for basic liveliness probe functionality.

    TBD: what about scalability? what if we have 1000 devices?
    """

    def __init__(
        self,
        component_manager,
        logger: Logger,
        proxy_timeout: int = 500,
        sleep_time: int = 1,
    ):
        self._thread = threading.Thread(target=self.run)
        self._stop = False
        self._logger = logger
        self._thread.daemon = True
        self._component_manager = component_manager
        self._proxy_timeout = proxy_timeout
        self._sleep_time = sleep_time
        self._dev_factory = DevFactory()

    def start(self) -> None:
        """
        Starts the sub devices
        """
        if not self._thread.is_alive():
            self._thread.start()

    def stop(self) -> None:
        """
        Stops the sub devices
        """
        self._stop = True

    def run(self) -> NotImplementedError:
        """
        Runs the sub devices
        """
        raise NotImplementedError("This method must be inherited")

    def device_task(self, dev_info: DeviceInfo) -> None:
        """
        Checks device status
        """
        try:
            proxy = self._dev_factory.get_device(dev_info.dev_name)
            proxy.set_timeout_millis(self._proxy_timeout)
            self._component_manager.update_ping_info(proxy.ping())
        except Exception as exp_msg:
            self._logger.error(
                "Device not working %s: %s", dev_info.dev_name, exp_msg
            )
            self._component_manager.device_failed(dev_info, exp_msg)


class SingleDeviceLivelinessProbe(BaseLivelinessProbe):
    """A class for monitoring a single device"""

    def run(self) -> None:
        """A method to run single device in the Queue for monitoring"""
        with tango.EnsureOmniThread() and futures.ThreadPoolExecutor(
            max_workers=1
        ) as executor:
            while not self._stop:
                try:
                    dev_info = self._component_manager.get_device()
                except Exception as exp_msg:
                    self._logger.error(
                        "Exception occured while getting device info: %s",
                        exp_msg,
                    )
                else:
                    try:
                        if dev_info is None:
                            continue
                        executor.submit(self.device_task, dev_info)
                    except Exception as exp_msg:
                        self._logger.error(
                            "Error in submitting the task for %s: %s",
                            dev_info.dev_name,
                            exp_msg,
                        )
                sleep(self._sleep_time)


class LivelinessProbeType(IntEnum):
    """
    This class assigns the enum value to single or multiple devices.
    """

    NONE = 0
    SINGLE_DEVICE = 1
