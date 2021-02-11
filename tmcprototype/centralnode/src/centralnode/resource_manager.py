"""
ResourceManager class for CentralNode.
"""
# Standard Python imports
import logging

from centralnode.device_data import DeviceData


class ResourceManager:
    """
    ResourceManager class for managing the resource allocation status per subarray in a matrix.
    """

    __instance = None

    def __init__(self, logger=None):
        """Private constructor of the class"""
        if ResourceManager.__instance != None:
            raise Exception("This is singletone class")
        else:
            ResourceManager.__instance = self
        if logger is None:
            self.logger = logging.getLogger(__name__)
        else:
            self.logger = logger
        self._subarray_allocation = {}

    def initialize_resource_matrix(self):
        """
        Initializes Resource Matrix which maintains resource allocation to a perticular subarray.
        :return: None
        """
        device_data = DeviceData.get_instance()
        for dish in range(1, (device_data.num_dishes + 1)):
            # Update device._dish_leaf_node_devices variable
            device_data._dish_leaf_node_devices.append(
                device_data.dln_prefix + f"000{dish}"
            )
            # Initialize device._subarray_allocation variable (map of Dish Id and allocation status)
            # to indicate availability of the dishes
            dish_ID = f"dish000{dish}"
            self._subarray_allocation[dish_ID] = "NOT_ALLOCATED"

    def update_resource_matrix(self, resources_allocated, subarrayID):
        """
        Updates Resource Matrix.
        :param resources_allocated: list od dishes allocated to a subarray.
        :param subarrayID: Subarray id
        :return: None
        """
        device_data = DeviceData.get_instance()
        for dish in range(0, len(resources_allocated)):
            dish_ID = "dish" + (resources_allocated[dish])
            self._subarray_allocation[dish_ID] = f"SA{subarrayID}"
            device_data.receptorIDList.append(resources_allocated[dish])

    def update_resource_deallocation(self, subarray_name):
        for Dish_ID, Dish_Status in self._subarray_allocation.items():
            if Dish_Status == subarray_name:
                self._subarray_allocation[Dish_ID] = "NOT_ALLOCATED"

    def is_already_assigned(self, dish_ID):
        return self._subarray_allocation[dish_ID] != "NOT_ALLOCATED"

    @staticmethod
    def get_instance():
        if ResourceManager.__instance is None:
            ResourceManager()
        return ResourceManager.__instance
