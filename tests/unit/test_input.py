from ska_tmc_sdpsubarrayleafnode.model.input import SdpSLNInputParameter


def test_properties():
    input = SdpSLNInputParameter(None)
    input.sdp_subarray_dev_name = "6"
    assert input.sdp_subarray_dev_name == ("6")
