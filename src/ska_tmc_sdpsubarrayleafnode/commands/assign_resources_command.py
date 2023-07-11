# flake8: noqa:E501
"""
AssignResouces command class for SDPSubarrayLeafNode.
"""
import json
import threading
import time
from json import JSONDecodeError
from typing import Callable, Optional

from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import ObsState
from ska_tango_base.executor import TaskStatus
from ska_tmc_common.timeout_callback import TimeoutCallback
from tango import DevFailed

from ska_tmc_sdpsubarrayleafnode.commands.abstract_command import SdpSLNCommand


class AssignResources(SdpSLNCommand):
    """
    A class for SdpSubarayLeafNode's AssignResources() command.

    Assigns resources to given SDP Subarray.
    """

    def __init__(
        self,
        component_manager,
        logger=None,
    ):
        super().__init__(component_manager, logger)
        self.component_manager = component_manager
        self.timeout_id = f"{time.time()}_{__class__.__name__}"
        self.timeout_callback = TimeoutCallback(self.timeout_id, self.logger)
        self.task_callback: Callable

    # pylint: disable=unused-argument
    def assign_resources(
        self,
        argin: str,
        logger=None,
        task_callback: Callable = None,
        task_abort_event: Optional[threading.Event] = None,
    ) -> None:
        """This is a long running method for AssignResources command, it
        executes do hook, invokes AssignResources command on CspSubarray.

        :param argin: Input JSON string
        :type argin : str
        :param logger: logger
        :type logger: logging.Logger
        :param task_callback: Update task state, defaults to None
        :type task_callback: Callable, optional
        :param task_abort_event: Check for abort, defaults to None
        :type task_abort_event: Event, optional
        """
        self.component_manager.command_in_progress = "AssignResources"
        self.task_callback = task_callback
        task_callback(status=TaskStatus.IN_PROGRESS)
        self.component_manager.start_timer(
            self.timeout_id,
            self.component_manager.command_timeout,
            self.timeout_callback,
        )
        result_code, message = self.do(argin)
        self.logger.info(result_code)
        if result_code == ResultCode.FAILED:
            self.update_task_status(result_code, message)
            self.component_manager.stop_timer()
            self.component_manager.command_in_progress = ""
        else:
            self.start_tracker_thread(
                self.component_manager.get_obs_state,
                ObsState.IDLE,
                self.timeout_id,
                self.timeout_callback,
                command_id=self.component_manager.assign_id,
                # pylint: disable=line-too-long
                lrcr_callback=self.component_manager.long_running_result_callback,
            )
            # self.update_task_status(result_code, message)

        # return result_code, message

    def update_task_status(self, result: ResultCode, message: str = ""):
        if result == ResultCode.FAILED:
            self.task_callback(
                status=TaskStatus.COMPLETED,
                result=result,
                exception=message,
            )
        else:
            self.task_callback(status=TaskStatus.COMPLETED, result=result)
        self.component_manager.command_in_progress = ""

    # pylint: disable=line-too-long
    def do(self, argin=None):
        """
        Method to invoke AssignResources command on SDP Subarray.

        :param argin: The string in JSON format. The JSON contains following values:

            eb_id and maximum length of the SBI:
            Mandatory JSON object consisting of

            eb_id :
                String

            max_length:
                Float

        scan_types:
            Consist of Scan type id name

            scan_type:
                DevVarStringArray

        Processing blocks:
            Mandatory JSON object consisting of

                processing_blocks:
                    DevVarStringArray

        Example:
           "sdp":{"interface":"https://schema.skao.int/ska-sdp-assignres/0.4","execution_block": {"eb_id":
        "eb-mvp01-20200325-00001","max_length": 100,"context":{},"beams":[{"beam_id": "vis0",
        "function":"visibilities"},{"beam_id": "pss1","search_beam_id": 1,"function": "pulsar search"},
        {"beam_id": "pss2","search_beam_id": 2,"function":"pulsar search"},{"beam_id": "pst1",
        "timing_beam_id": 1,"function": "pulsar timing"},{"beam_id":"pst2","timing_beam_id":2,
        "function": "pulsar timing"},{"beam_id": "vlbi1","vlbi_beam_id":1,"function": "vlbi"}],
        "channels": [{"channels_id":"vis_channels","spectral_windows":[{"spectral_window_id":
        "fsp_1_channels","count": 744,"start": 0,"stride": 2,"freq_min":350000000,"freq_max":
        368000000,"link_map": [[0,0],[200,1],[744,2],[944,3]]},{"spectral_window_id":"fsp_2_channels",
        "count": 744,"start": 2000,"stride": 1,"freq_min": 360000000,"freq_max":368000000,
        "link_map": [[2000,4],[2200,5]]},{"spectral_window_id":"zoom_window_1","count": 744,"start":
        4000,"stride": 1,"freq_min": 360000000,"freq_max": 361000000,"link_map": [[4000,6],[4200,7]]}]},
        {"channels_id":"pulsar_channels","spectral_windows":[{"spectral_window_id":
        "pulsar_fsp_channels","count": 744,"start": 0,"freq_min": 350000000,"freq_max": 368000000}]}],
        "polarisations": [{"polarisations_id": "all","corr_type":["XX","XY","YY","YX"]}],"fields":
        [{"field_id": "field_a","phase_dir":{"ra":[123,0.1],"dec":[123,0.1],"reference_time": "...",
        "reference_frame": "ICRF3"},"pointing_fqdn":"low-tmc/telstate/0/pointing"}]},
        "processing_blocks":[{"pb_id": "pb-mvp01-20200325-00001","sbi_ids":["sbi-mvp01-20200325-00001"],
        "script":{},"parameters":{},"dependencies":{}},{"pb_id":"pb-mvp01-20200325-00002","sbi_ids":
        ["sbi-mvp01-20200325-00002"],"script":{},"parameters":{},"dependencies":{}},{"pb_id":
        "pb-mvp01-20200325-00003","sbi_ids":["sbi-mvp01-20200325-00001","sbi-mvp01-20200325-00002"],
        "script":{},"parameters": {},"dependencies":{}}],"resources":{"csp_links":[1,2,3,4],
        "receptors":["FS4","FS8"],"receive_nodes":10}}}

        Note: Enter input without spaces

        return:
            None
        """
        # pylint: enable=line-too-long
        result_code, message = self.init_adapter()
        if result_code == ResultCode.FAILED:
            return result_code, message
        try:
            json_argument = json.loads(argin)
        except JSONDecodeError as e:
            log_msg = (
                "Execution of AssignResources command is failed."
                + "Reason: JSON parsing failed with exception: {}".format(e)
                + "The command is not executed successfully."
                + "The device will continue with normal operation"
            )
            self.logger.exception(log_msg)
            return (
                ResultCode.FAILED,
                "Exception occurred while parsing the JSON. Please check the logs for details.",
            )

        try:
            json_argument[
                "interface"
            ] = "https://schema.skao.int/ska-sdp-assignres/0.4"
            log_msg = (
                "Input JSON for AssignResources command for "
                "{}: {}".format(
                    self.sdp_subarray_adapter.dev_name, json_argument
                )
            )
            self.logger.debug(log_msg)

            self.sdp_subarray_adapter.AssignResources(
                json.dumps(json_argument), self.component_manager.cmd_ended_cb
            )

        except (AttributeError, ValueError, TypeError, DevFailed) as e:
            self.logger.exception("AssignResources Command failed: %s", e)
            return self.component_manager.generate_command_result(
                ResultCode.FAILED,
                "The invocation of the AssignResources command is failed on"
                + "Sdp Subarray Device {}".format(
                    self.sdp_subarray_adapter.dev_name
                )
                + "Reason: Error in calling the AssignResources command on Sdp"
                + "Subarray."
                + "The command has NOT been executed."
                + "This device will continue with normal operation.",
            )

        return (ResultCode.OK, "")
