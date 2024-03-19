"""Event Reciever for SDP Subarray Leaf Node Manager"""
import logging
from concurrent import futures
from time import sleep
from typing import Dict, Optional

import tango
from ska_ser_logging import configure_logging
from ska_tmc_common.device_info import SubArrayDeviceInfo
from ska_tmc_common.event_receiver import EventReceiver

configure_logging()
LOGGER: logging.Logger = logging.getLogger(__name__)


class SdpSLNEventReceiver(EventReceiver):
    """
    The SdpSLNEventReceiver class has the responsibility to receive events
    from the sub devices managed by the Sdp Subarray Leaf Node.

    The ComponentManager uses the handle events methods
    for the attribute of interest.
    For each of them a callback is defined.

    """

    def __init__(
        self,
        component_manager,
        logger: logging.Logger = LOGGER,
        max_workers: int = 1,
        proxy_timeout: int = 500,
        sleep_time: int = 1,
    ):
        super().__init__(
            component_manager=component_manager,
            logger=logger,
            max_workers=max_workers,
            proxy_timeout=proxy_timeout,
            sleep_time=sleep_time,
        )
        self._max_workers = max_workers
        self._sleep_time = sleep_time
        self._stop = False
        self._component_manager = component_manager

    def run(self):
        while not self._stop:
            with futures.ThreadPoolExecutor(
                max_workers=self._max_workers
            ) as executor:
                dev_info = self._component_manager.get_device()
                if dev_info.last_event_arrived is None:
                    executor.submit(self.subscribe_events, dev_info)
            sleep(self._sleep_time)

    def subscribe_events(
        self,
        dev_info: SubArrayDeviceInfo,
        attribute_dictionary: Optional[Dict[str, str]] = None,
    ):
        try:
            proxy = self._dev_factory.get_device(dev_info.dev_name)
            proxy.subscribe_event(
                "obsState",
                tango.EventType.CHANGE_EVENT,
                self.handle_obs_state_event,
                stateless=True,
            )
        except Exception as exception:
            self._logger.debug(
                "Event not working for the device %s, %s",
                proxy.dev_name,
                exception,
            )

    def handle_obs_state_event(self, event):
        """
        Method to handle and update the latest value of
        obsState attribute.
        Args:
            event (tango.EventType): to flag the
            change in event.
        """
        if event.err:
            error = event.errors[0]
            self._logger.error("%s %s", error.reason, error.desc)
            self._component_manager.update_event_failure()
            return
        new_value = event.attr_value.value
        self._component_manager.update_device_obs_state(new_value)
        self._logger.info("ObsState value is updated to %s", new_value)
