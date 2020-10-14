# standard python imports
import pytest
import json

# other imports
from centralnodelow.input_validator import AssignResourceValidator
from centralnodelow.exceptions import InvalidJSONError, SubarrayNotPresentError
from centralnodelow import const

# Sample 'good' JSON
sample_assign_resources_request = {
  "subarray_id": 1,
  "station_ids": [
    1,
    2
  ],
  "channels": [
    1,
    2,
    3,
    4,
    5,
    6,
    7,
    8
  ],
  "station_beam_ids": [
    1
  ]
}

class TestAssignResourceValidator():
    """Class to test the AssignResourceValidator class methods"""
    _test_subarray_list = ["test/subarray/1"]

    def test_validate_good_json(self):
        """This function tests the validate method when good formatted json is provided"""

        input_validator = AssignResourceValidator(self._test_subarray_list)
        output_config = input_validator.loads(json.dumps(sample_assign_resources_request))
        assert output_config == sample_assign_resources_request

    def test_validate_wrong_subarray_id(self):
        """
        Tests that InvalidJSONError is raised when a wrong subarray id is given
        in the input string.
        """

        # Set wrong subarray id.
        input_json = sample_assign_resources_request
        input_json["subarrayID"] = 99

        input_validator = AssignResourceValidator(self._test_subarray_list)

        with pytest.raises(SubarrayNotPresentError) as excinfo:
            input_validator.loads(json.dumps(input_json))
        assert const.ERR_SUBARRAY_ID_DOES_NOT_EXIST in str(excinfo.value)
