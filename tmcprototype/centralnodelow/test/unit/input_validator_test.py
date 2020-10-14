# standard python imports
import pytest
import json

# other imports
from centralnodelow.input_validator import AssignResourceValidator
from centralnodelow.input_validator import ReleaseResourceValidator
from centralnodelow.exceptions import InvalidJSONError, SubarrayNotPresentError
from centralnodelow import const
from os.path import dirname, join


# Sample 'good' JSON
assign_input_file = 'command_AssignResources.json'
path = join(dirname(__file__), 'data', assign_input_file)
with open(path, 'r') as f:
    sample_assign_resources_request = f.read()

release_input_file='command_ReleaseResources.json'
path= join(dirname(__file__), 'data' , release_input_file)
with open(path, 'r') as f:
    sample_release_resources_request = f.read()

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
        input_json["subarray_id"] = 999

        input_validator = AssignResourceValidator(self._test_subarray_list)

        with pytest.raises(SubarrayNotPresentError) as excinfo:
            input_validator.loads(json.dumps(input_json))
        assert const.ERR_SUBARRAY_ID_DOES_NOT_EXIST in str(excinfo.value)


class TestReleaseResourceValidator():
    """Class to test the AssignResourceValidator class methods"""
    _test_subarray_list = ["test/subarray/1"]

    def test_validate_correct_json(self):
        """This function tests the validate method when good formatted json is provided"""

        input_validator = ReleaseResourceValidator(self._test_subarray_list)
        output_config = input_validator.loads(json.dumps(sample_release_resources_request))
        assert output_config == sample_release_resources_request

    def test_validate_wrong_subarray_id(self):
        """
        Tests that InvalidJSONError is raised when a wrong subarray id is given
        in the input string.
        """

        # Set wrong subarray id.
        input_json = sample_release_resources_request
        input_json["subarray_id"] = 999

        input_validator = ReleaseResourceValidator(self._test_subarray_list)

        with pytest.raises(SubarrayNotPresentError) as excinfo:
            input_validator.loads(json.dumps(input_json))
        assert const.ERR_SUBARRAY_ID_DOES_NOT_EXIST in str(excinfo.value)
