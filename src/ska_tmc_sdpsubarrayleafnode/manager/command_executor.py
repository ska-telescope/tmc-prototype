import threading
import time
from queue import Empty, Queue

import tango
from ska_tango_base.commands import ResultCode


class CommandExecutor:
    def __init__(
        self,
        logger,
        max_queue_size=100,
        queue_fetch_timeout=1,
        _update_command_in_progress_callback=None,
    ) -> None:
        self._logger = logger
        self._max_queue_size = max_queue_size
        self._work_queue = Queue(self._max_queue_size)
        self._queue_fetch_timeout = queue_fetch_timeout

        self._command_executed = []
        self._command_in_progress = "None"

        self._worker_thread = threading.Thread(
            target=self._run,
            daemon=True,
        )
        self._stop = False
        self._worker_thread.start()

        self._update_command_in_progress_callback = (
            _update_command_in_progress_callback
        )

    @property
    def command_executed(self):
        return self._command_executed

    @property
    def command_in_progress(self):
        return self._command_in_progress

    @command_in_progress.setter
    def command_in_progress(self, value):
        if self._command_in_progress != value:
            self._command_in_progress = value
            if self._update_command_in_progress_callback is not None:
                self._update_command_in_progress_callback(
                    self._command_in_progress
                )

    @property
    def queue_full(self):
        return self._work_queue.full()

    def stop(self):
        self._stop = True

    def enqueue_command(self, command_object, argin=None):
        """Adds the Command to the queue.

        :param command_object: Instance of Command
        :type command_object: Command
        :param argin: The argument to the Tango command
        :type argin: Any
        """
        unique_id = self.get_unique_id(type(command_object).__name__)
        self._work_queue.put([command_object, argin, unique_id])
        return unique_id

    def get_unique_id(self, command_name):
        """Generate a unique ID for the command

        :param command_name: The name of the command
        :type command_name: string
        :return: The unique ID of the command
        :rtype: string
        """
        return f"{time.time()}_{command_name}"

    def add_command_execution(self, id, command_name, result_code, message):
        """
        Add a command execution to the list of the command executed
        """
        self._command_executed.append(
            {
                "Id": id,
                "Command": command_name,
                "ResultCode": result_code,
                "Message": message,
            }
        )

    def _run(self):
        with tango.EnsureOmniThread():
            while not self._stop:
                try:
                    # import debugpy; debugpy.debug_this_thread()
                    self.command_in_progress = "None"
                    (command_object, argin, id) = self._work_queue.get(
                        block=True, timeout=self._queue_fetch_timeout
                    )
                    command_name = type(command_object).__name__
                    try:
                        self.command_in_progress = command_name
                        (result_code, message) = command_object.do(argin)
                        self._logger.info(
                            "Command %s with argin %s executed with result: (%s, %s)",
                            command_name,
                            argin,
                            result_code,
                            message,
                        )
                        self.add_command_execution(
                            id, command_name, result_code, message
                        )
                    except Exception as err:
                        self._logger.exception(
                            (
                                "Unmanaged exception during call to command %s with argin %s: %s",
                                command_name,
                                argin,
                                str(err),
                            ),
                            exc_info=1,
                        )
                        self.add_command_execution(
                            id, command_name, ResultCode.FAILED, str(err)
                        )
                except Empty:
                    continue
