class DeviceData:
    """
    This class represents the CSP master as functional device. It mainly comprise the data common
    across various functions of a CSP master.
    """

    __instance = None

    def __init__(self):
        """Private constructor of the class"""
        if DeviceData.__instance is not None:
            raise Exception("This is singletone class")
        else:
            DeviceData.__instance = self
        self.cbf_health_updator = None
        self.pss_health_updator = None
        self.pst_health_updator = None
        self._csp_cbf_health_state_log = ""
        self._csp_pss_health_state_log = ""
        self._csp_pst_health_state_log = ""

    @staticmethod
    def get_instance():
        if DeviceData.__instance is None:
            DeviceData()
        return DeviceData.__instance
