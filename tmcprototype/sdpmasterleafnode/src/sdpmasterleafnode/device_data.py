from ska.base.control_model import HealthState

class DeviceData:
    """
    This class represents the SDP master as functional device. It mainly comprise the data common
    across various functions of a SDP master.
    """

    __instance = None

    def __init__(self):
        """Private constructor of the class"""
        if DeviceData.__instance != None:
            raise Exception("This is singletone class")
        else:
            DeviceData.__instance = self
        self._health_state = HealthState.UNKNOWN

    @staticmethod
    def get_instance():
        if DeviceData.__instance == None:
            DeviceData()
        return DeviceData.__instance
