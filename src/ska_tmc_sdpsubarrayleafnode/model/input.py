class InputParameter:
    def __init__(self, changed_callback) -> None:
        self._changed_callback = changed_callback

    def update(self, component_manager):
        raise NotImplementedError("This class must be inherited!")


class InputParameterMid(InputParameter):
    def __init__(self, changed_callback) -> None:
        super().__init__(changed_callback)
        self._sdp_subarray_dev_name = "mid_sdp/elt/subarray_1"
        self._changed_callback = changed_callback

    @property
    def sdp_subarray_dev_name(self):
        """
        Input parameter
        Return the SDP Subarray device name

        :return: the SDP Subarray device name
        :rtype: str
        """
        return self._sdp_subarray_dev_name

    @sdp_subarray_dev_name.setter
    def sdp_subarray_dev_name(self, value):
        """
        Input parameter
        Return the SDP Subarray device name

        :return: the SDP Subarray device name
        :rtype: str
        """
        self._sdp_subarray_dev_name = value
        if self._changed_callback is not None:
            self._changed_callback()

    def update(self, component_manager):
        list_dev_names = []

        dev_name = self.sdp_subarray_dev_name
        if dev_name != "" and component_manager.get_device(dev_name) is None:
            component_manager.add_device(dev_name)
            list_dev_names.append(dev_name)

        for devInfo in component_manager.devices:
            if devInfo.dev_name not in list_dev_names:
                component_manager.component.remove_device(devInfo.dev_name)


# TODO: Sdp element device is not present for MVP-Low currently
# In future as the requirements are updated, InputParameterLow class can be added
# class InputParameterLow(InputParameter):
#         pass
