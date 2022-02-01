from ska_tmc_sdpmasterleafnode.model.input import SdpMLNInputParameter


def test_properties():
    input = SdpMLNInputParameter(None)
    input.sdp_master_dev_name = "mid_sdp/elt/master"
    assert input.sdp_master_dev_name == ("mid_sdp/elt/master")
