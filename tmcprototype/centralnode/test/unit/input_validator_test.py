# standard python imports
import pytest
import json

# Sample 'good' JSON
sample_json = {
  "subarrayID": 1,
  "dish": {
    "receptorIDList": [
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
        "ra": "21:08:47.92",
        "dec": "-88:57:22.9",
        "subbands": [
          {
            "freq_min": 0.35e9,
            "freq_max": 1.05e9,
            "nchan": 372,
            "input_link_map": [
              [
                1,
                0
              ],
              [
                101,
                1
              ]
            ]
          }
        ]
      },
      {
        "id": "calibration_B",
        "coordinate_system": "ICRS",
        "ra": "21:08:47.92",
        "dec": "-88:57:22.9",
        "subbands": [
          {
            "freq_min": 0.35e9,
            "freq_max": 1.05e9,
            "nchan": 372,
            "input_link_map": [
              [
                1,
                0
              ],
              [
                101,
                1
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

# other imports
from centralnode.input_validator import AssignResourceValidator
from centralnode.exceptions import ResourceReassignmentError, ResourceNotPresentError
from centralnode.exceptions import SubarrayNotPresentError, InvalidJSONError

class TestAssignResourceValidator():
    """Class to test the AssignResourceValidator class methods"""
    _test_subarray_list = ["test/subarray/1", "test/subarray/2", "test/subarray/3"]
    _test_receptor_id_list = ["ska_mid/tm_leaf_node/d0001", "ska_mid/tm_leaf_node/d0002",
                              "ska_mid/tm_leaf_node/d0003", "ska_mid/tm_leaf_node/d0004"]

    def test_validate_good_json(self):
        """This function tests the validate method when good formatted json is provided"""

        # good_json_string =  \
        #     '{"subarrayID":1,"dish":{"receptorIDList":["0001"]},"sdp":{"id":"sbi-mvp01-' \
        #     '20200325-00001","max_length":100.0,"scan_types":[{"id":"science_A","coordinate' \
        #     '_system":"ICRS","ra":"21:08:47.92","dec":"-88:57:22.9","subbands":[{"freq_min"' \
        #     ':0.35e9,"freq_max":1.05e9,"nchan":372,"input_link_map":[[1,0],[101,1]]}]},{"id"' \
        #     ':"calibration_B","coordinate_system":"ICRS","ra":"21:08:47.92","dec":"-88:57:22.9",' \
        #     '"subbands":[{"freq_min":0.35e9,"freq_max":1.05e9,"nchan":372,"input_link_' \
        #     'map":[[1,0],[101,1]]}]}],"processing_blocks":[{"id":"pb-mvp01-20200325-00001",' \
        #     '"workflow":{"type":"realtime","id":"vis_receive","version":"0.1.0"},"parameters"' \
        #     ':{}},{"id":"pb-mvp01-20200325-00002","workflow":{"type":"realtime","id":"test_' \
        #     'realtime","version":"0.1.0"},"parameters":{}},{"id":"pb-mvp01-20200325-00003",' \
        #     '"workflow":{"type":"batch","id":"ical","version":"0.1.0"},"parameters":{},' \
        #     '"dependencies":[{"pb_id":"pb-mvp01-20200325-00001","type":["visibilities"]}]}' \
        #     ',{"id":"pb-mvp01-20200325-00004","workflow":{"type":"batch","id":"dpreb","' \
        #     'version":"0.1.0"},"parameters":{},"dependencies":[{"pb_id":"pb-mvp01-20200325-' \
        #     '00003","type":["calibration"]}]}]}}'

        input_validator = AssignResourceValidator(self._test_subarray_list, 
          self._test_receptor_id_list,
          "ska_mid/tm_leaf_node/d")
        result = input_validator.validate(json.dumps(sample_json))
        assert result == True

    def test_validate_wrong_subarray_id(self):
        """
        Tests that InvalidJSONError is raised when a wrong subarray id is given in the input string.
        """
        # invalid_subarray_id_json_string = \
        #     '{"subarrayID":99,"dish":{"receptorIDList":["0001"]},"sdp":{"id":"sbi-mvp01-' \
        #     '20200325-00001","max_length":100.0,"scan_types":[{"id":"science_A","coordinate' \
        #     '_system":"ICRS","ra":"21:08:47.92","dec":"-88:57:22.9","subbands":[{"freq_min"' \
        #     ':0.35e9,"freq_max":1.05e9,"nchan":372,"input_link_map":[[1,0],[101,1]]}]},{"id"' \
        #     ':"calibration_B","coordinate_system":"ICRS","ra":"21:08:47.92","dec":"-88:57:22.9",' \
        #     '"subbands":[{"freq_min":0.35e9,"freq_max":1.05e9,"nchan":372,"input_link_' \
        #     'map":[[1,0],[101,1]]}]}],"processing_blocks":[{"id":"pb-mvp01-20200325-00001",' \
        #     '"workflow":{"type":"realtime","id":"vis_receive","version":"0.1.0"},"parameters"' \
        #     ':{}},{"id":"pb-mvp01-20200325-00002","workflow":{"type":"realtime","id":"test_' \
        #     'realtime","version":"0.1.0"},"parameters":{}},{"id":"pb-mvp01-20200325-00003",' \
        #     '"workflow":{"type":"batch","id":"ical","version":"0.1.0"},"parameters":{},' \
        #     '"dependencies":[{"pb_id":"pb-mvp01-20200325-00001","type":["visibilities"]}]}' \
        #     ',{"id":"pb-mvp01-20200325-00004","workflow":{"type":"batch","id":"dpreb","' \
        #     'version":"0.1.0"},"parameters":{},"dependencies":[{"pb_id":"pb-mvp01-20200325-' \
        #     '00003","type":["calibration"]}]}]}}'

        # Set wrong subarray id.
        input_json = sample_json
        input_json["subarrayID"] = 99

        with pytest.raises(SubarrayNotPresentError) as excinfo:
            input_validator = AssignResourceValidator(self._test_subarray_list,
              self._test_receptor_id_list, "ska_mid/tm_leaf_node/d")
            input_validator.validate(json.dumps(input_json))
        assert "Invalid subarray ID. Subarray ID must be between 1 and 3." in str(excinfo.value)

    def test_validate_incorrect_receptor_id(self):
        """
        Tests that InvalidJSONError is raised when a receptor id is given incorrect value in the input string.
        """
        # incorrect_receptor_id_json_string = \
        #     '{"subarrayID":1,"dish":{"receptorIDList":["9999"]},"sdp":{"id":"sbi-mvp01-' \
        #     '20200325-00001","max_length":100.0,"scan_types":[{"id":"science_A","coordinate' \
        #     '_system":"ICRS","ra":"21:08:47.92","dec":"-88:57:22.9","subbands":[{"freq_min"' \
        #     ':0.35e9,"freq_max":1.05e9,"nchan":372,"input_link_map":[[1,0],[101,1]]}]},{"id"' \
        #     ':"calibration_B","coordinate_system":"ICRS","ra":"21:08:47.92","dec":"-88:57:22.9",' \
        #     '"subbands":[{"freq_min":0.35e9,"freq_max":1.05e9,"nchan":372,"input_link_' \
        #     'map":[[1,0],[101,1]]}]}],"processing_blocks":[{"id":"pb-mvp01-20200325-00001",' \
        #     '"workflow":{"type":"realtime","id":"vis_receive","version":"0.1.0"},"parameters"' \
        #     ':{}},{"id":"pb-mvp01-20200325-00002","workflow":{"type":"realtime","id":"test_' \
        #     'realtime","version":"0.1.0"},"parameters":{}},{"id":"pb-mvp01-20200325-00003",' \
        #     '"workflow":{"type":"batch","id":"ical","version":"0.1.0"},"parameters":{},' \
        #     '"dependencies":[{"pb_id":"pb-mvp01-20200325-00001","type":["visibilities"]}]}' \
        #     ',{"id":"pb-mvp01-20200325-00004","workflow":{"type":"batch","id":"dpreb","' \
        #     'version":"0.1.0"},"parameters":{},"dependencies":[{"pb_id":"pb-mvp01-20200325-' \
        #     '00003","type":["calibration"]}]}]}}'

        input_json = sample_json
        invalid_receptor_id_list = ["9999"]
        input_json["dish"]["receptorIDList"] = invalid_receptor_id_list

        with pytest.raises(ResourceNotPresentError) as excinfo:
            input_validator = AssignResourceValidator(self._test_subarray_list,
              self._test_receptor_id_list, "ska_mid/tm_leaf_node/d")
            input_validator.validate(json.dumps(input_json))

        assert "Invalid value in receptorIDList. Valid values are '0001', '0002', '0003', '0004'" in str(excinfo.value)

'''
    def test_validate_non_int_subarray_id(self):
        """
        Tests that InvalidJSONError is raised when a wrong subarray id is given in the input string.
        """
        non_int_subarray_id_json_string = \
            '{"subarrayID":12.34,"dish":{"receptorIDList":["0001"]},"sdp":{"id":"sbi-mvp01-' \
            '20200325-00001","max_length":100.0,"scan_types":[{"id":"science_A","coordinate' \
            '_system":"ICRS","ra":"21:08:47.92","dec":"-88:57:22.9","subbands":[{"freq_min"' \
            ':0.35e9,"freq_max":1.05e9,"nchan":372,"input_link_map":[[1,0],[101,1]]}]},{"id"' \
            ':"calibration_B","coordinate_system":"ICRS","ra":"21:08:47.92","dec":"-88:57:22.9",' \
            '"subbands":[{"freq_min":0.35e9,"freq_max":1.05e9,"nchan":372,"input_link_' \
            'map":[[1,0],[101,1]]}]}],"processing_blocks":[{"id":"pb-mvp01-20200325-00001",' \
            '"workflow":{"type":"realtime","id":"vis_receive","version":"0.1.0"},"parameters"' \
            ':{}},{"id":"pb-mvp01-20200325-00002","workflow":{"type":"realtime","id":"test_' \
            'realtime","version":"0.1.0"},"parameters":{}},{"id":"pb-mvp01-20200325-00003",' \
            '"workflow":{"type":"batch","id":"ical","version":"0.1.0"},"parameters":{},' \
            '"dependencies":[{"pb_id":"pb-mvp01-20200325-00001","type":["visibilities"]}]}' \
            ',{"id":"pb-mvp01-20200325-00004","workflow":{"type":"batch","id":"dpreb","' \
            'version":"0.1.0"},"parameters":{},"dependencies":[{"pb_id":"pb-mvp01-20200325-' \
            '00003","type":["calibration"]}]}]}}'

        with pytest.raises(JsonValueTypeMismatchError) as excinfo:
            input_validator = AssignResourceValidator()
            input_validator.validate(non_int_subarray_id_json_string)
        assert "Subarray ID must be an integer value." in str(excinfo.value)

    def test_validate_subarray_id_empty(self):
        """
        Tests that InvalidJSONError is raised when a subarray id is left empty in the input string.
        """
        empty_subarray_id_json_string = \
            '{"subarrayID":,"dish":{"receptorIDList":["0001"]},"sdp":{"id":"sbi-mvp01-' \
            '20200325-00001","max_length":100.0,"scan_types":[{"id":"science_A","coordinate' \
            '_system":"ICRS","ra":"21:08:47.92","dec":"-88:57:22.9","subbands":[{"freq_min"' \
            ':0.35e9,"freq_max":1.05e9,"nchan":372,"input_link_map":[[1,0],[101,1]]}]},{"id"' \
            ':"calibration_B","coordinate_system":"ICRS","ra":"21:08:47.92","dec":"-88:57:22.9",' \
            '"subbands":[{"freq_min":0.35e9,"freq_max":1.05e9,"nchan":372,"input_link_' \
            'map":[[1,0],[101,1]]}]}],"processing_blocks":[{"id":"pb-mvp01-20200325-00001",' \
            '"workflow":{"type":"realtime","id":"vis_receive","version":"0.1.0"},"parameters"' \
            ':{}},{"id":"pb-mvp01-20200325-00002","workflow":{"type":"realtime","id":"test_' \
            'realtime","version":"0.1.0"},"parameters":{}},{"id":"pb-mvp01-20200325-00003",' \
            '"workflow":{"type":"batch","id":"ical","version":"0.1.0"},"parameters":{},' \
            '"dependencies":[{"pb_id":"pb-mvp01-20200325-00001","type":["visibilities"]}]}' \
            ',{"id":"pb-mvp01-20200325-00004","workflow":{"type":"batch","id":"dpreb","' \
            'version":"0.1.0"},"parameters":{},"dependencies":[{"pb_id":"pb-mvp01-20200325-' \
            '00003","type":["calibration"]}]}]}}'

        with pytest.raises(InvalidJSONError) as excinfo:
            input_validator = AssignResourceValidator()
            input_validator.validate(empty_subarray_id_json_string)

        assert "Malformed input string. Please check the JSON format." in str(excinfo.value)

    def test_validate_missing_subarray_id(self):
        """
        Tests that InvalidJSONError is raised when a receptor id is given incorrect value in the input string.
        """
        missing_subarray_id_json_string = \
            '{"dish":{"receptorIDList":["0001"]},"sdp":{"id":"sbi-mvp01-' \
            '20200325-00001","max_length":100.0,"scan_types":[{"id":"science_A","coordinate' \
            '_system":"ICRS","ra":"21:08:47.92","dec":"-88:57:22.9","subbands":[{"freq_min"' \
            ':0.35e9,"freq_max":1.05e9,"nchan":372,"input_link_map":[[1,0],[101,1]]}]},{"id"' \
            ':"calibration_B","coordinate_system":"ICRS","ra":"21:08:47.92","dec":"-88:57:22.9",' \
            '"subbands":[{"freq_min":0.35e9,"freq_max":1.05e9,"nchan":372,"input_link_' \
            'map":[[1,0],[101,1]]}]}],"processing_blocks":[{"id":"pb-mvp01-20200325-00001",' \
            '"workflow":{"type":"realtime","id":"vis_receive","version":"0.1.0"},"parameters"' \
            ':{}},{"id":"pb-mvp01-20200325-00002","workflow":{"type":"realtime","id":"test_' \
            'realtime","version":"0.1.0"},"parameters":{}},{"id":"pb-mvp01-20200325-00003",' \
            '"workflow":{"type":"batch","id":"ical","version":"0.1.0"},"parameters":{},' \
            '"dependencies":[{"pb_id":"pb-mvp01-20200325-00001","type":["visibilities"]}]}' \
            ',{"id":"pb-mvp01-20200325-00004","workflow":{"type":"batch","id":"dpreb","' \
            'version":"0.1.0"},"parameters":{},"dependencies":[{"pb_id":"pb-mvp01-20200325-' \
            '00003","type":["calibration"]}]}]}}'

        with pytest.raises(JsonKeyMissingError) as excinfo:
            input_validator = AssignResourceValidator()
            input_validator.validate(missing_subarray_id_json_string)

        assert "A mandatory key subarrayID is missing from input JSON." in str(excinfo.value)

    def test_validate_incorrect_receptor_id_no_list(self):
        """
        Tests that InvalidJSONError is raised when a receptor id is given incorrect value in the input string.
        """
        receptor_id_no_list_json_string = \
            '{"subarrayID":1,"dish":{"receptorIDList":"9999"},"sdp":{"id":"sbi-mvp01-' \
            '20200325-00001","max_length":100.0,"scan_types":[{"id":"science_A","coordinate' \
            '_system":"ICRS","ra":"21:08:47.92","dec":"-88:57:22.9","subbands":[{"freq_min"' \
            ':0.35e9,"freq_max":1.05e9,"nchan":372,"input_link_map":[[1,0],[101,1]]}]},{"id"' \
            ':"calibration_B","coordinate_system":"ICRS","ra":"21:08:47.92","dec":"-88:57:22.9",' \
            '"subbands":[{"freq_min":0.35e9,"freq_max":1.05e9,"nchan":372,"input_link_' \
            'map":[[1,0],[101,1]]}]}],"processing_blocks":[{"id":"pb-mvp01-20200325-00001",' \
            '"workflow":{"type":"realtime","id":"vis_receive","version":"0.1.0"},"parameters"' \
            ':{}},{"id":"pb-mvp01-20200325-00002","workflow":{"type":"realtime","id":"test_' \
            'realtime","version":"0.1.0"},"parameters":{}},{"id":"pb-mvp01-20200325-00003",' \
            '"workflow":{"type":"batch","id":"ical","version":"0.1.0"},"parameters":{},' \
            '"dependencies":[{"pb_id":"pb-mvp01-20200325-00001","type":["visibilities"]}]}' \
            ',{"id":"pb-mvp01-20200325-00004","workflow":{"type":"batch","id":"dpreb","' \
            'version":"0.1.0"},"parameters":{},"dependencies":[{"pb_id":"pb-mvp01-20200325-' \
            '00003","type":["calibration"]}]}]}}'

        with pytest.raises(InvalidParameterValue) as excinfo:
            input_validator = AssignResourceValidator()
            input_validator.validate(receptor_id_no_list_json_string)

        assert "The parameter receptorIDList must be a list." in str(excinfo.value)
    
    def test_validate_missing_receptor_id_list(self):
        """
        Tests that InvalidJSONError is raised when a receptor id is given incorrect value in the input string.
        """
        missing_receptor_id_list_json_string = \
            '{"subarrayID":1, "dish":{},"sdp":{"id":"sbi-mvp01-' \
            '20200325-00001","max_length":100.0,"scan_types":[{"id":"science_A","coordinate' \
            '_system":"ICRS","ra":"21:08:47.92","dec":"-88:57:22.9","subbands":[{"freq_min"' \
            ':0.35e9,"freq_max":1.05e9,"nchan":372,"input_link_map":[[1,0],[101,1]]}]},{"id"' \
            ':"calibration_B","coordinate_system":"ICRS","ra":"21:08:47.92","dec":"-88:57:22.9",' \
            '"subbands":[{"freq_min":0.35e9,"freq_max":1.05e9,"nchan":372,"input_link_' \
            'map":[[1,0],[101,1]]}]}],"processing_blocks":[{"id":"pb-mvp01-20200325-00001",' \
            '"workflow":{"type":"realtime","id":"vis_receive","version":"0.1.0"},"parameters"' \
            ':{}},{"id":"pb-mvp01-20200325-00002","workflow":{"type":"realtime","id":"test_' \
            'realtime","version":"0.1.0"},"parameters":{}},{"id":"pb-mvp01-20200325-00003",' \
            '"workflow":{"type":"batch","id":"ical","version":"0.1.0"},"parameters":{},' \
            '"dependencies":[{"pb_id":"pb-mvp01-20200325-00001","type":["visibilities"]}]}' \
            ',{"id":"pb-mvp01-20200325-00004","workflow":{"type":"batch","id":"dpreb","' \
            'version":"0.1.0"},"parameters":{},"dependencies":[{"pb_id":"pb-mvp01-20200325-' \
            '00003","type":["calibration"]}]}]}}'

        with pytest.raises(JsonKeyMissingError) as excinfo:
            input_validator = AssignResourceValidator()
            input_validator.validate(missing_receptor_id_list_json_string)

        assert "A mandatory key receptorIDList is missing from input JSON." in str(excinfo.value)
'''