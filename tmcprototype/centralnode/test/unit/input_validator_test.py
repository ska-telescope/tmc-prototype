from input_validator import AssignResourceValidator

class TestAssignResourceValidator():
    """Class to test the AssignResourceValidator class methods"""

    def test_validate_good_json(self):
        """This function tests the validate method when good formatted json is provided"""

        good_json_string = \
            '{"subarrayID":1,"dish":{"receptorIDList":["0001"]},"sdp":{"id":"sbi-mvp01-' \
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

        input_validator = AssignResourceValidator()
        result = input_validator.validate(good_json_string)
        assert result == True

    def test_validate_wrong_subarray_id(self):
        """
        Tests that InvalidJSONError is raised when a wrong subarray id is given in the input string.
        """
        invalid_subarray_id_json_string = \
            '{"subarrayID":99,"dish":{"receptorIDList":["0001"]},"sdp":{"id":"sbi-mvp01-' \
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
        
        with pytest.raises(InvalidJSONError):
            input_validator = AssignResourceValidator()
            assert input_validator.validate(invalid_subarray_id_json_string)