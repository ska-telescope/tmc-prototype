# Standard python imports
import threading

class ScanStopper():
    """
    Class to invoke EndScan command after scan duration is complete.
    """
    def __init__(self):
        self.scan_timer = None

    def start_scan_timer(self, scan_duration, end_scan_command):
        log_message = f"Scan duration: {scan_duration}"
        self.scan_timer = threading.Timer(scan_duration, end_scan_command)
        self.scan_timer.start()

    def stop_scan_timer(self):
        self.scan_timer.cancel()

    def is_scan_running(self):
        return self.scan_timer.is_alive()