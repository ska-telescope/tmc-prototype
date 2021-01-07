class DeviceData:
    """
    This class represents the MCCS master as functional device. It mainly comprise the data common
    across various functions of a MCCS master.
    """

    __instance = None

    def __init__(self):
        """Private constructor of the class""" 
        if DeviceData.__instance != None:
            raise Exception("This is singletone class")
        else:
            DeviceData.__instance = self
        self._mccs_master_ln_fqdn = ""
        self._read_activity_message= ""
        
        
    @staticmethod
    def get_instance():
        if DeviceData.__instance == None:
            DeviceData()
        return DeviceData.__instance
