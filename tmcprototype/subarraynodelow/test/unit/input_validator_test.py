# standard python imports
import json
import pytest
from os.path import dirname, join
# other imports
from subarraynodelow.input_validator import ScanValidator, ConfigureValidator

# Sample 'good' JSON
scan_input_file= 'command_Scan.json'
path= join(dirname(__file__), 'data', scan_input_file)
with open(path, 'r') as f:
    sample_scan_request=f.read()

configure_input_file= 'command_Configure.json'
path= join(dirname(__file__), 'data' , configure_input_file)
with open(path, 'r') as f:
    sample_configure_request=f.read()


class TestScanValidator():
    """Class to test the ConfigureValidator class methods"""

    def test_validate_good_json(self):
        """This function tests the validate method when good formatted json is provided"""

        input_validator = ScanValidator()
        output_config = input_validator.loads(json.dumps(sample_scan_request))
        assert output_config == sample_scan_request


class TestConfigureValidator():
    """Class to test the ConfigureValidator class methods"""

    def test_validate_good_json(self):
        """This function tests the validate method when good formatted json is provided"""

        input_validator = ConfigureValidator()
        output_config = input_validator.loads(json.dumps(sample_configure_request))
        assert output_config == sample_configure_request

    def test_validate_invalid_scan_duration(self):
        """
        Tests that ValueError is raised when a invalid scan duration is given
        in the input string.
        """

        # Set invalid scan duration.
        input_json = sample_configure_request
        input_json["tmc"]["scanDuration"] = 0
        input_validator = ConfigureValidator()
        with pytest.raises(ValueError) as excinfo:
            input_validator.loads(json.dumps(input_json))
        assert "Invalid Scan Duration" in str(excinfo.value)

