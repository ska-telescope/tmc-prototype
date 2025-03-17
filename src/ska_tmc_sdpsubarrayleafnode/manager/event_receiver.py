"""Event Reciever for SDP Subarray Leaf Node Manager"""
import logging
from concurrent import futures
from time import sleep
from typing import Dict, Optional

import tango
from ska_ser_logging import configure_logging
from ska_tmc_common.device_info import SubArrayDeviceInfo
from ska_tmc_common.v1.event_receiver import EventReceiver

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
        event_subscription_check_period: int = 1,
    ):
        super().__init__(
            component_manager=component_manager,
            logger=logger,
            max_workers=max_workers,
            proxy_timeout=proxy_timeout,
            event_subscription_check_period=event_subscription_check_period,
        )
        self._max_workers = max_workers
        self._event_subscription_check_period = event_subscription_check_period
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
            sleep(self._event_subscription_check_period)

    def subscribe_events(
        self,
        dev_info: SubArrayDeviceInfo,
        attribute_dictionary: Optional[Dict[str, str]] = None,
    ):
        sdp_subarray_proxy = None
        try:
            sdp_subarray_proxy = self._dev_factory.get_device(
                dev_info.dev_name
            )
            sdp_subarray_proxy.subscribe_event(
                "obsState",
                tango.EventType.CHANGE_EVENT,
                self.handle_obs_state_event,
                stateless=True,
            )
            sdp_subarray_proxy.subscribe_event(
                "adminMode",
                tango.EventType.CHANGE_EVENT,
                self.handle_admin_mode_event,
                stateless=True,
            )
            self.stop()
        except Exception as exception:
            if sdp_subarray_proxy:
                self._logger.debug(
                    "Error on Device %s while event subscription."
                    " Exception: %s",
                    sdp_subarray_proxy.dev_name,
                    exception,
                )
