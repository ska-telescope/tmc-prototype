"""
ResourceManager class for CentralNode.
"""
from centralnode.device_data import DeviceData
class ResourceManager:
    """
    ResourceManager class for Resource management.
    """
    def init_resource_matrix(self,):
        """
        Initializes Resource Matrix which maintains resource allocation to a perticular subarray.
        :return: None
        """
        device_data = DeviceData.get_instance()
        for dish in range(1, (device_data.num_dishes + 1)):
            # Update device._dish_leaf_node_devices variable
            device_data._dish_leaf_node_devices.append(device_data.dln_prefix + "000" + str(dish))
            # Initialize device._subarray_allocation variable (map of Dish Id and allocation status)
            # to indicate availability of the dishes
            dish_ID = "dish000" + str(dish)
            device_data._subarray_allocation[dish_ID] = "NOT_ALLOCATED"

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
            device_data._subarray_allocation[dish_ID] = "SA" + str(subarrayID)
            device_data.receptorIDList.append(resources_allocated[dish])