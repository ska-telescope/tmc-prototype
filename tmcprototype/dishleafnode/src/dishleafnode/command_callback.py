#-*- coding: utf-8 -*-
#
# This file is part of the DishLeafNode project
#
#
#
# Distributed under the terms of the BSD-3-Clause license.
# See LICENSE.txt for more info.

"""
A Leaf control node for DishMaster.
"""
import json
import importlib.resources
import math
import datetime
import time
import threading

import tango
from tango import DeviceProxy, EventType, ApiUtil, DevState, AttrWriteType, DevFailed
from tango.server import run, command, device_property, attribute
import katpoint

from ska.base.commands import ResultCode, BaseCommand
from ska.base import SKABaseDevice
from tmc.common.tango_client import TangoClient
from ska.base.control_model import HealthState, SimulationMode
from .utils import UnitConverter
from . import release
from .device_data import DeviceData


class CommandCallBack:
    __instance = None

    def __init__(self, device, log):
        self.device = device
        self.logger = log


    def cmd_ended_cb(self, event):
        """
        Callback function immediately executed when the asynchronous invoked
        command returns. Checks whether the command has been successfully invoked on DishMaster.

        :param event: a CmdDoneEvent object. This object is used to pass data
            to the callback method in asynchronous callback model for command
            execution.
        :type: CmdDoneEvent object
            It has the following members:
            - device     : (DeviceProxy) The DeviceProxy object on which the call was executed.
            - cmd_name   : (str) The command name
            - argout_raw : (DeviceData) The command argout
            - argout     : The command argout
            - err        : (bool) A boolean flag set to True if the command failed.
                            False otherwise
            - errors     : (sequence<DevError>) The error stack
            - ext
        """

        device_data = DeviceData.get_instance()

        if event.err:
            log_message = f"Error in invoking command: {event.cmd_name}\n{event.errors}"
            self.logger.error(log_message)
            device_data._read_activity_message = log_message
        else:
            log_message = f"Command :-> {event.cmd_name} invoked successfully."
            self.logger.info(log_message)
            device_data._read_activity_message = log_message
