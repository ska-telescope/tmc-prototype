# -*- coding: utf-8 -*-
#
# This file is part of the SKATestDevice project
#
#
#

""" SKATestDevice

A generic Test device for testing SKA base class functionalites.
"""

# PyTango imports
import PyTango
from PyTango import DebugIt
from PyTango.server import run
from PyTango.server import Device, DeviceMeta
from PyTango.server import attribute, command
from PyTango.server import device_property
from PyTango import AttrQuality, DispLevel, DevState
from PyTango import AttrWriteType, PipeWriteType
from SKABaseDevice import SKABaseDevice
# Additional import
# PROTECTED REGION ID(SKATestDevice.additionnal_import) ENABLED START #
import json

from skabase.utils import (exception_manager, convert_api_value, coerce_value)
# PROTECTED REGION END #    //  SKATestDevice.additionnal_import

__all__ = ["SKATestDevice", "main"]


class SKATestDevice(SKABaseDevice):
    """
    A generic Test device for testing SKA base class functionalites.
    """
    __metaclass__ = DeviceMeta
    # PROTECTED REGION ID(SKATestDevice.class_variable) ENABLED START #
    # PROTECTED REGION END #    //  SKATestDevice.class_variable

    # -----------------
    # Device Properties
    # -----------------











    # ----------
    # Attributes
    # ----------

    obsState = attribute(
        dtype='DevEnum',
        doc="Observing State",
        enum_labels=["IDLE", "CONFIGURING", "READY", "SCANNING", "PAUSED", "ABORTED", "FAULT", ],
    )

    obsMode = attribute(
        dtype='DevEnum',
        doc="Observing Mode",
        enum_labels=["IDLE", "IMG_CONTINUUM", "IMG_SPECTRAL_LINE", "IMG_ZOOM", "PULSAR_SEARCH", "TRANSIENT_SEARCH_FAST", "TRANSIENT_SEARCH_SLOW", "PULSAR_TIMING", "VLBI", ],
    )

    configurationProgress = attribute(
        dtype='uint16',
        unit="%",
        max_value=100,
        min_value=0,
        doc="Percentage configuration progress",
    )

    configurationDelayExpected = attribute(
        dtype='uint16',
        unit="seconds",
        doc="Configuration delay expected in seconds",
    )











    # ---------------
    # General methods
    # ---------------

    def init_device(self):
        SKABaseDevice.init_device(self)
        # PROTECTED REGION ID(SKATestDevice.init_device) ENABLED START #
        # PROTECTED REGION END #    //  SKATestDevice.init_device

    def always_executed_hook(self):
        # PROTECTED REGION ID(SKATestDevice.always_executed_hook) ENABLED START #
        pass
        # PROTECTED REGION END #    //  SKATestDevice.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(SKATestDevice.delete_device) ENABLED START #
        pass
        # PROTECTED REGION END #    //  SKATestDevice.delete_device

    # ------------------
    # Attributes methods
    # ------------------

    def read_obsState(self):
        # PROTECTED REGION ID(SKATestDevice.obsState_read) ENABLED START #
        return 0
        # PROTECTED REGION END #    //  SKATestDevice.obsState_read

    def read_obsMode(self):
        # PROTECTED REGION ID(SKATestDevice.obsMode_read) ENABLED START #
        return 0
        # PROTECTED REGION END #    //  SKATestDevice.obsMode_read

    def read_configurationProgress(self):
        # PROTECTED REGION ID(SKATestDevice.configurationProgress_read) ENABLED START #
        return 0
        # PROTECTED REGION END #    //  SKATestDevice.configurationProgress_read

    def read_configurationDelayExpected(self):
        # PROTECTED REGION ID(SKATestDevice.configurationDelayExpected_read) ENABLED START #
        return 0
        # PROTECTED REGION END #    //  SKATestDevice.configurationDelayExpected_read


    # --------
    # Commands
    # --------

    @command(
    dtype_in='str', 
    doc_in="JSON encoded dict with this format\n{``group``: str,  # name of existing group\n  ``command``: str, # name of command to run\n  ``arg_type``: str,  # data type of command input argument\n  ``arg_value``: str, # value for command input argument\n  ``forward``: bool  # True if command should be forwarded to all subgroups (default)\n}", 
    dtype_out='str', 
    doc_out="Return value from command on the group, as a JSON encoded string.\nThis will be a list of dicts of the form \n[ \n{``device_name``: str,  # TANGO device name\n  ``argout``: <value>,  # return value from command (type depends on command)\n  ``failed``: bool  # True if command failed\n},\n{ ... },\n ... ]", 
    )
    @DebugIt()
    def RunGroupCommand(self, argin):
        # PROTECTED REGION ID(SKATestDevice.RunGroupCommand) ENABLED START #
        with exception_manager(self):
            defaults = {'arg_type': None, 'arg_value': None, 'forward': True}
            required = ('group', 'command', 'arg_type', 'arg_value', 'forward')
            args = self._parse_argin(argin, defaults=defaults, required=required)
            group_name = args['group']
            group = self.groups.get(group_name)
            if group:
                command = args['command']
                forward = args['forward']
                if args['arg_type']:
                    _, param = convert_api_value({'type': args['arg_type'],
                                                  'value': args['arg_value']})
                    replies = group.command_inout(command, param, forward=forward)
                else:
                    replies = group.command_inout(command, forward=forward)
                results = []
                for reply in replies:
                    result = {
                        'device_name': reply.dev_name(),
                        'argout': coerce_value(reply.get_data()),
                        'failed': reply.has_failed(),
                    }
                    results.append(result)
                argout = json.dumps(results, sort_keys=True)
            else:
                raise RuntimeError("Invalid group requested. '{}' not in '{}'"
                                   .format(group_name, sorted(self.groups.keys())))
        return argout
        # PROTECTED REGION END #    //  SKATestDevice.RunGroupCommand

# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(SKATestDevice.main) ENABLED START #
    return run((SKATestDevice,), args=args, **kwargs)
    # PROTECTED REGION END #    //  SKATestDevice.main

if __name__ == '__main__':
    main()
