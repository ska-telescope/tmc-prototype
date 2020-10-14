# standard python imports
import json

# other imports
from subarraynodelow.input_validator import ScanValidator, ConfigureValidator

# Sample 'good' JSON
sample_scan_request = {
  "id": 1
}
sample_configure_request = {
  "mccs": {
    "stations": [
      {
        "station_id": 1
      },
      {
        "station_id": 2
      }
    ],
    "station_beam_pointings": [
      {
        "station_beam_id": 1,
        "target": {
          "system": "HORIZON",
          "name": "DriftScan",
          "Az": 180.0,
          "El": 45.0
        },
        "update_rate": 0.0,
        "channels": [
          1,
          2,
          3,
          4,
          5,
          6,
          7,
          8
        ]
      }
    ]
  },
  "tmc": {
    "scanDuration": 10.0
  }
}


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

