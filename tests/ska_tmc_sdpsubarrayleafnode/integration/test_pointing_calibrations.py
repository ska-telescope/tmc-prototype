"""Integration test for testing pointing offset attribute on SDP subarray."""
import json

import pytest
import tango
from ska_tmc_common import DevFactory

from tests.settings import (
    SDP_SUBARRAY_DEVICE_MID,
    SDP_SUBARRAY_LEAF_NODE_MID,
    logger,
    wait_for_attribute_value,
)

POINTING_OFFSETS = [
    "SKA001",
    -6.71102309437987,
    114.11010391244332,
    -7.090356031104502,
    104.10028693155607,
    -4.115211938625473,
    69.9725295732531,
    70.1182176899719,
    78.8829949012184,
    95.49061976199042,
    729.5782881970024,
    119.27311545171803,
    1065.4074085647912,
    0.9948872678443994,
    0.8441090109163307,
]


@pytest.mark.post_deployment
@pytest.mark.SKA_mid
def test_pointing_offsets(tango_context, group_callback):
    dev_factory = DevFactory()
    sdp_leaf_node = dev_factory.get_device(SDP_SUBARRAY_LEAF_NODE_MID)
    sdp_subarray = dev_factory.get_device(SDP_SUBARRAY_DEVICE_MID)
    sdp_subarray.subscribe_event(
        "pointingOffsets",
        tango.EventType.CHANGE_EVENT,
        group_callback["pointingOffsets"],
    )

    # Validation at SDP subarray side
    sdp_subarray.SetDirectPointingOffsets(json.dumps(POINTING_OFFSETS))
    assert wait_for_attribute_value(sdp_subarray, "pointingOffsets")
    sdp_subarray_pointing_offsets = sdp_subarray.read_attribute(
        "pointingOffsets"
    ).value
    logger.info("Pointing Offsets: %s", sdp_subarray_pointing_offsets)
    assert sdp_subarray_pointing_offsets == json.dumps(POINTING_OFFSETS)

    # Validation at SDP SLN side
    assert wait_for_attribute_value(sdp_leaf_node, "pointingCalibrations")
    sdpsln_pointing_offsets = sdp_leaf_node.read_attribute(
        "pointingCalibrations"
    ).value
    cross_elevation_offset = POINTING_OFFSETS[5]
    elevation_offset = POINTING_OFFSETS[3]
    assert sdpsln_pointing_offsets == json.dumps(
        [cross_elevation_offset, elevation_offset]
    )
