"""Event Reciever for SDP Subarray Leaf Node Manager"""
from concurrent import futures
from time import sleep

import tango
from ska_tmc_common.event_receiver import EventReceiver
from tango import DevFailed


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
        logger=None,
        max_workers=1,
        proxy_timeout=500,
        sleep_time=1,
    ):
        super().__init__(
            component_manager, logger, max_workers, proxy_timeout, sleep_time
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

    def subscribe_events(self, dev_info):
        try:
            proxy = self._dev_factory.get_device(dev_info.dev_name)
            proxy.subscribe_event(
                "obsState",
                tango.EventType.CHANGE_EVENT,
                self.handle_obs_state_event,
                stateless=True,
            )

            proxy.subscribe_event(
                "pointingOffsets",
                tango.EventType.CHANGE_EVENT,
                self.handle_pointing_offsets_event,
                stateless=True,
            )

        except (AttributeError, ValueError, TypeError, DevFailed) as e:
            self._logger.debug(
                "Event not working for the device %s, %s", proxy.dev_name, e
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

    def handle_pointing_offsets_event(self, event):
        """
        Method to handle and update the latest value of
        pointingOffsets attribute.
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
        self._component_manager.update_device_pointing_calibrations(new_value)
        self._logger.info(
            f"Current Pointing Offsets are [dish_id,cross_el,el]: {new_value}"
        )
