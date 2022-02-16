from time import sleep
from concurrent import futures
import tango
from ska_tmc_common.event_receiver import EventReceiver


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


    # def stop(self):
    #     self._stop = True

    def run(self):
        self._logger.info("Inside run method:::::::::")
        while not self._stop:
            with futures.ThreadPoolExecutor(
                max_workers=self._max_workers
            ) as executor:
                devInfo = self._component_manager.get_device()
                if devInfo.last_event_arrived is None:
                    executor.submit(self.subscribe_events, devInfo)
            sleep(self._sleep_time)


    def subscribe_events(self, devInfo):
        self._logger.info("Inside subscribe events:::::::::")
        try:
            proxy = self._dev_factory.get_device(devInfo.dev_name)
            proxy.subscribe_event(
                "ObsState",
                tango.EventType.CHANGE_EVENT,
                self.handle_obs_state_event,
                stateless=True,
            )

        except Exception as e:
            self._logger.debug(
                "event not working for device %s/%s", proxy.dev_name, e
            )

    def handle_obs_state_event(self, evt):
        self._logger.info("Inside handle obsState method:::::::::")
        if evt.err:
            error = evt.errors[0]
            self._logger.error("%s %s", error.reason, error.desc)
            # self._component_manager.update_event_failure(evt.device.dev_name())
            self._component_manager.update_event_failure()
            return
        self._logger.info("Inside handle obs_state:::::::::::::")
        new_value = evt.attr_value.value
        self._logger.info("New value is::::::::::::: %s", new_value)
        # self._component_manager.update_device_obs_state(
        #     evt.device.dev_name(), new_value
        # )
        self._component_manager.update_device_obs_state(new_value)
        self._logger.info("Obstate value is updated")

