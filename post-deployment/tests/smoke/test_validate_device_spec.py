import pytest

from tango_simlib.utilities.validate_device import validate_device_from_url

SPEC_URLS = {
    "ska_tango_guide_ska_wide": (
        "https://gitlab.com/ska-telescope/telescope-model/-/raw/"
        "master/spec/tango/ska_wide/Guidelines.yaml"
    ),
    "dish_master": (
        "https://gitlab.com/ska-telescope/telescope-model/-/raw/"
        "master/spec/tango/dsh/DishMaster.yaml"
    ),
}


@pytest.mark.skamid
def test_dishmaster_conforms_to_tango_wide():
    """Check that dishmaster conforms to tango developers guide"""
    result = validate_device_from_url(
        "mid_d0001/elt/master", SPEC_URLS["ska_tango_guide_ska_wide"], False
    )
    assert not result

@pytest.mark.skamid
def test_dishmaster_conforms_to_dishmaster_spec():
    """Check that dishmaster device conforms to dishmaster specification"""
    result = validate_device_from_url(
        "mid_d0001/elt/master", SPEC_URLS["dish_master"], False
    )
    assert not result
