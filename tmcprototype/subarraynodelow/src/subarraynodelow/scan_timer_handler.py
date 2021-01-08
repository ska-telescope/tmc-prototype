# Standard python imports
import threading
from tmc.common.tango_server_helper import TangoServerHelper

class ScanTimerHandler():
    """
    Class to invoke EndScan command after scan duration is complete.
    """
    def __init__(self):
        self.scan_timer = None
        self.this_server = TangoServerHelper.get_instance()

    def start_scan_timer(self, scan_duration):
        log_message = f"Scan duration: {scan_duration}"
        self.scan_timer = threading.Timer(scan_duration, self.this_server.device.endscan)
        self.scan_timer.start()

    def stop_scan_timer(self):
        self.scan_timer.cancel()

    def is_scan_running(self):
        return self.scan_timer.is_alive()
