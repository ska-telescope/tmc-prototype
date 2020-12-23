# from .attribute_callbacks import CbfHealthStateAttributeUpdator
class DeviceData:
    """
    This class represents the CSP master as functional device. It mainly comprise the data common
    across various functions of a CSP master.
    """

    __instance = None

    def __init__(self):
        """Private constructor of the class""" 
        if DeviceData.__instance != None:
            raise Exception("This is singletone class")
        else:
            DeviceData.__instance = self
        self.csp_master_ln_fqdn = ""
        self._read_activity_message= ""
        from .attribute_callbacks import CbfHealthStateAttributeUpdator
        self.cbf_health_updator = CbfHealthStateAttributeUpdator()

    @staticmethod
    def get_instance():
        if DeviceData.__instance == None:
            DeviceData()
        return DeviceData.__instance
