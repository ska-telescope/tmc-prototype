import logging
import os
from tempfile import NamedTemporaryFile

import pytest
import requests
from tango_simlib.utilities.validate_device import validate_device_from_path

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


def get_job_token_header():
    """Build the request headers

    Authenticated requests for resources from Gitlab are not rate limited as harshly.
    See https://jira.skatelescope.org/browse/SKB-66 for details.

    Returns
    -------
    dict
        The headers to use in the HTTP request
    """
    request_headers = {}
    job_token = os.environ.get("CI_JOB_TOKEN", {})
    if job_token:
        request_headers = {"JOB-TOKEN": job_token}

    return request_headers


@pytest.mark.mid
def test_dishmaster_conforms_to_tango_wide():
    """Check that dishmaster conforms to tango developers guide"""

    request_headers = get_job_token_header()
    if request_headers:
        logging.info("Using job token")

    with NamedTemporaryFile(mode="wb") as tmp_file:
        spec_response = requests.get(SPEC_URLS["ska_tango_guide_ska_wide"], headers=request_headers)
        tmp_file.write(spec_response.content)
        tmp_file.seek(0)
        result = validate_device_from_path("mid_d0001/elt/master", tmp_file.name, False)

    assert not result


@pytest.mark.mid
def test_dishmaster_conforms_to_dishmaster_spec():
    """Check that dishmaster device conforms to dishmaster specification"""

    request_headers = get_job_token_header()
    if request_headers:
        logging.info("Using job token")

    with NamedTemporaryFile(mode="wb") as tmp_file:
        spec_response = requests.get(SPEC_URLS["dish_master"], headers=request_headers)
        tmp_file.write(spec_response.content)
        tmp_file.seek(0)
        result = validate_device_from_path("mid_d0001/elt/master", tmp_file.name, False)

    assert not result
