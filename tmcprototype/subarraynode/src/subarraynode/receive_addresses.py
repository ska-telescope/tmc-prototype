# Standard Python imports
import logging

# Additional imports
from tmc.common.tango_client import TangoClient

from . import const
from .device_data import DeviceData


class ReceiveAddressesUpdater:
    """
    Receive Addresses Updater class
    """

    def __init__(self, logger=None):
        if logger == None:
            self.logger = logging.getLogger(__name__)
        else:
            self.logger = logger
        self.sdp_ln_receive_addresses_event_id = {}
        self.device_data = DeviceData.get_instance()

    def subscribe(self):
        self.sdp_sa_client = TangoClient(self.device_data.sdp_sa_fqdn)

        # Subscribe ReceiveAddresses of SdpSubarray
        sdp_receive_addr_event_id = self.sdp_sa_client.subscribe_attribute(
            "receiveAddresses", self.receive_addresses_cb
        )
        self.sdp_ln_receive_addresses_event_id[
            self.sdp_sa_client
        ] = sdp_receive_addr_event_id

    def receive_addresses_cb(self, event):
        """
        Retrieves the receiveAddresses attribute of SDP Subarray.

        :param event: A TANGO_CHANGE event on SDP Subarray receiveAddresses attribute.

        :return: None
        """
        if not event.err:
            self.device_data._receive_addresses_map = event.attr_value.value
        else:
            log_msg = f"{const.ERR_SUBSR_RECEIVE_ADDRESSES_SDP_SA}{event}"
            self.logger.debug(log_msg)
            self._read_activity_message = log_msg

    def unsubscribe(self):
        """
        This function unsubscribes to receive_addresses attribute change events given by the event ids and their
        corresponding SDP leaf node DeviceProxy objects.

        :param : None

        :return: None

        """
        for tango_client, event_id in self.sdp_ln_receive_addresses_event_id.items():
            tango_client.unsubscribe_attribute(event_id)
