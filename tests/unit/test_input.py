from ska_tmc_sdpsubarrayleafnode.model.input import InputParameterMid


def test_properties():
    input = InputParameterMid(None)
    input.sdp_subarray_dev_name = "6"
    assert input.sdp_subarray_dev_name == ("6")
