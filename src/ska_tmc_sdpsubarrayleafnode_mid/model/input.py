class InputParameter:
    def __init__(self, changed_callback) -> None:
        self._changed_callback = changed_callback
        self._tm_subarray_dev_names = []

    def update(self, component_manager):
        raise NotImplementedError("This class must be inherited!")


class InputParameterMid(InputParameter):
    def __init__(self, changed_callback) -> None:
        self._sdp_subarray_dev_names = ["mid_sdp/elt/subarray_01"]
        self._changed_callback = changed_callback

    @property
    def sdp_subarray_dev_names(self):
        """
        Input parameter
        Return the SDP Subarray device names

        :return: the SDP Subarray device names
        :rtype: tuple
        """
        return self._sdp_subarray_dev_names

    @sdp_subarray_dev_names.setter
    def sdp_subarray_dev_names(self, value):
        """
        Input parameter
        Set the SDP Subarray device names to be
        managed by the CentralNode

        :param value: the SDP Subarray device names
        :type value: tuple
        """
        self._sdp_subarray_dev_names = value
        if self._changed_callback is not None:
            self._changed_callback()

    def update(self, component_manager):
        list_dev_names = []

        for dev_name in self.sdp_subarray_dev_names:
            if component_manager.get_device(dev_name) is None:
                component_manager.add_device(dev_name)
                list_dev_names.append(dev_name)

        for devInfo in component_manager.devices:
            if devInfo.dev_name not in list_dev_names:
                component_manager.component.remove_device(devInfo.dev_name)
