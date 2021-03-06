# standard python imports
import pytest
import json

# other imports
from centralnode.input_validator import AssignResourceValidator
from centralnode.exceptions import ResourceReassignmentError, ResourceNotPresentError
from centralnode.exceptions import SubarrayNotPresentError, InvalidJSONError
from centralnode import const

# Sample 'good' JSON
sample_assign_resources_request = {
  "subarrayID": 1,
  "dish": {
    "receptorIDList": [
      "0002",
      "0001"
    ]
  },
  "sdp": {
    "id": "sbi-mvp01-20200325-00001",
    "max_length": 100.0,
    "scan_types": [
      {
        "id": "science_A",
        "coordinate_system": "ICRS",
        "ra": "02:42:40.771",
        "dec": "-00:00:47.84",
        "channels": [
          {
            "count": 744,
            "start": 0,
            "stride": 2,
            "freq_min": 0.35e9,
            "freq_max": 0.368e9,
            "link_map": [
              [
                0,
                0
              ],
              [
                200,
                1
              ],
              [
                744,
                2
              ],
              [
                944,
                3
              ]
            ]
          },
          {
            "count": 744,
            "start": 2000,
            "stride": 1,
            "freq_min": 0.36e9,
            "freq_max": 0.368e9,
            "link_map": [
              [
                2000,
                4
              ],
              [
                2200,
                5
              ]
            ]
          }
        ]
      },
      {
        "id": "calibration_B",
        "coordinate_system": "ICRS",
        "ra": "12:29:06.699",
        "dec": "02:03:08.598",
        "channels": [
          {
            "count": 744,
            "start": 0,
            "stride": 2,
            "freq_min": 0.35e9,
            "freq_max": 0.368e9,
            "link_map": [
              [
                0,
                0
              ],
              [
                200,
                1
              ],
              [
                744,
                2
              ],
              [
                944,
                3
              ]
            ]
          },
          {
            "count": 744,
            "start": 2000,
            "stride": 1,
            "freq_min": 0.36e9,
            "freq_max": 0.368e9,
            "link_map": [
              [
                2000,
                4
              ],
              [
                2200,
                5
              ]
            ]
          }
        ]
      }
    ],
    "processing_blocks": [
      {
        "id": "pb-mvp01-20200325-00001",
        "workflow": {
          "type": "realtime",
          "id": "vis_receive",
          "version": "0.1.0"
        },
        "parameters": {
          
        }
      },
      {
        "id": "pb-mvp01-20200325-00002",
        "workflow": {
          "type": "realtime",
          "id": "test_realtime",
          "version": "0.1.0"
        },
        "parameters": {
          
        }
      },
      {
        "id": "pb-mvp01-20200325-00003",
        "workflow": {
          "type": "batch",
          "id": "ical",
          "version": "0.1.0"
        },
        "parameters": {
          
        },
        "dependencies": [
          {
            "pb_id": "pb-mvp01-20200325-00001",
            "type": [
              "visibilities"
            ]
          }
        ]
      },
      {
        "id": "pb-mvp01-20200325-00004",
        "workflow": {
          "type": "batch",
          "id": "dpreb",
          "version": "0.1.0"
        },
        "parameters": {
          
        },
        "dependencies": [
          {
            "pb_id": "pb-mvp01-20200325-00003",
            "type": [
              "calibration"
            ]
          }
        ]
      }
    ]
  }
}

class TestAssignResourceValidator():
    """Class to test the AssignResourceValidator class methods"""
    _test_subarray_list = ["test/subarray/1", "test/subarray/2", "test/subarray/3"]
    _test_receptor_id_list = ["ska_mid/tm_leaf_node/d0001", "ska_mid/tm_leaf_node/d0002",
                              "ska_mid/tm_leaf_node/d0003", "ska_mid/tm_leaf_node/d0004"]

    def test_validate_good_json(self):
        """This function tests the validate method when good formatted json is provided"""

        input_validator = AssignResourceValidator(self._test_subarray_list, 
          self._test_receptor_id_list,
          "ska_mid/tm_leaf_node/d")
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

        input_validator = AssignResourceValidator(self._test_subarray_list,
              self._test_receptor_id_list, "ska_mid/tm_leaf_node/d")

        with pytest.raises(SubarrayNotPresentError) as excinfo:
            input_validator.loads(json.dumps(input_json))
        assert const.ERR_SUBARRAY_ID_DOES_NOT_EXIST in str(excinfo.value)

    @pytest.mark.skip(reason="Behavior of this test case has changed in tox env.")
    def test_validate_incorrect_receptor_id(self):
        """
        Tests that ResourceNotPresentError is raised when a receptor id is given incorrect
        value in the input string.
        """

        input_json = sample_assign_resources_request
        invalid_receptor_id_list = ["9999"]
        input_json["dish"]["receptorIDList"] = invalid_receptor_id_list

        input_validator = AssignResourceValidator(self._test_subarray_list,
              self._test_receptor_id_list, "ska_mid/tm_leaf_node/d")

        with pytest.raises(ResourceNotPresentError) as excinfo:
            input_validator.loads(json.dumps(input_json))

        assert const.ERR_RECEPTOR_ID_DOES_NOT_EXIST in str(excinfo.value)