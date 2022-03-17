"""
CSP Master Leaf node acts as a CSP contact point for Master Node and also to monitor
and issue commands to the CSP Master.
"""
from ska_tango_base import SKABaseDevice
from ska_tango_base.commands import ResultCode
from ska_tmc_common.op_state_model import TMCOpStateModel
from tango import AttrWriteType, DebugIt
from tango.server import attribute, command, device_property, run

from ska_tmc_cspmasterleafnode import release

from ska_tmc_cspmasterleafnode.manager import CspMLNComponentManager

__all__ = ["CspMasterLeafNode", "main"]


class CspMasterLeafNode(SKABaseDevice):
    """
    CSP Master Leaf node acts as a CSP contact point for Master Node and also to monitor
    and issue commands to the CSP Master.
    """

    # -----------------
    # Device Properties
    # -----------------
    CspMasterFQDN = device_property(
        default_value="mid_csp/elt/master",
        dtype="str",
        doc="FQDN of the CSP Master Tango Device Server.",
    )

    # -----------------
    # Attributes
    # -----------------
    commandExecuted = attribute(
        dtype=(("DevString",),),
        max_dim_x=4,
        max_dim_y=100,
    )

    cspMasterDevName = attribute(
        dtype="DevString",
        access=AttrWriteType.READ_WRITE,
    )

    SleepTime = device_property(dtype="DevFloat", default_value=1)
    # ---------------
    # General methods
    # ---------------

    class InitCommand(SKABaseDevice.InitCommand):
        """
        A class for the TMC CspMasterLeafNode's init_device() method.
        """

        def do(self):
            """
            Initializes the attributes and properties of the CspMasterLeafNode.

            return:
                A tuple containing a return code and a string message indicating status.
                The message is for information purpose only.

            rtype:
                (ResultCode, str)
            """
            super().do()
            device = self.target

            device._build_state = "{},{},{}".format(
                release.name, release.version, release.description
            )
            device._version_id = release.version
            device.op_state_model.perform_action("component_on")
            device.component_manager._command_executor.add_command_execution(
                "0", "Init", ResultCode.OK, ""
            )
            return (ResultCode.OK, "")

    def always_executed_hook(self):
        pass

    def delete_device(self):
        # if the init is called more than once
        # I need to stop all threads
        if hasattr(self, "component_manager"):
            self.component_manager.stop()

    # ------------------
    # Attributes methods
    # ------------------

    def read_cspMasterDevName(self):
        """Return the cspmasterdevname attribute."""
        return self.component_manager._csp_master_dev_name

    def write_cspMasterDevName(self, value):
        """Set the cspmasterdevname attribute."""
        self.component_manager.update_device_info(value)

    def read_commandExecuted(self):
        """Return the commandExecuted attribute."""
        result = []
        i = 0
        for command_executed in reversed(
            self.component_manager._command_executor.command_executed
        ):
            if i == 100:
                break
            single_res = [
                str(command_executed["Id"]),
                str(command_executed["Command"]),
                str(command_executed["ResultCode"]),
                str(command_executed["Message"]),
            ]
            result.append(single_res)
            i += 1
        return result

    # --------
    # Commands
    # --------

    def is_Off_allowed(self):
        """
        Checks whether this command is allowed to be run in current device state.

        :return: True if this command is allowed to be run in current device state.

        :rtype: boolean
        """
        handler = self.get_command_object("Off")
        return handler.check_allowed()

    @command(dtype_out="DevVarLongStringArray")
    def Off(self):
        """
        This command invokes Off() command on Csp Master.
        """
        handler = self.get_command_object("Off")
        if self.component_manager._command_executor.queue_full:
            message = """The invocation of the Off command on this device failed.
            Reason: The command executor rejected the queuing of the command because its queue is full.
            The Off command has NOT been queued and will not be executed.
            This device will continue with normal operation."""
            return [[ResultCode.FAILED], [message]]
        unique_id = self.component_manager._command_executor.enqueue_command(
            handler
        )
        return [[ResultCode.QUEUED], [str(unique_id)]]

    def is_On_allowed(self):
        """
        Checks whether this command is allowed to be run in current device state.

        :return: True if this command is allowed to be run in current device state.

        :rtype: boolean
        """
        handler = self.get_command_object("On")
        return handler.check_allowed()

    @command(dtype_out="DevVarLongStringArray")
    @DebugIt()
    def On(self):
        """
        This command invokes On() command on Csp Master.
        """
        handler = self.get_command_object("On")
        if self.component_manager._command_executor.queue_full:
            message = """The invocation of the On command on this device failed.
            Reason: The command executor rejected the queuing of the command because its queue is full.
            The On command has NOT been queued and will not be executed.
            This device will continue with normal operation."""
            return [[ResultCode.FAILED], [message]]
        unique_id = self.component_manager._command_executor.enqueue_command(
            handler
        )
        return [[ResultCode.QUEUED], [str(unique_id)]]

    def is_Standby_allowed(self):
        """
        Checks whether this command is allowed to be run in current device state.

        :return: True if this command is allowed to be run in current device state.

        :rtype: boolean
        """
        handler = self.get_command_object("Standby")
        return handler.check_allowed()

    @command(dtype_out="DevVarLongStringArray")
    @DebugIt()
    def Standby(self):
        """
        This command invokes Standby() command on Csp Master.
        """
        handler = self.get_command_object("Standby")
        if self.component_manager._command_executor.queue_full:
            message = """The invocation of the Standby command on this device failed.
            Reason: The command executor rejected the queuing of the command because its queue is full.
            The Standby command has NOT been queued and will not be executed.
            This device will continue with normal operation."""
            return [[ResultCode.FAILED], [message]]
        unique_id = self.component_manager._command_executor.enqueue_command(
            handler
        )
        return [[ResultCode.QUEUED], [str(unique_id)]]

    # default ska mid
    def create_component_manager(self):
        self.op_state_model = TMCOpStateModel(
            logger=self.logger, callback=super()._update_state
        )
        cm = CspMLNComponentManager(
            self.CspMasterFQDN,
            self.op_state_model,
            logger=self.logger,
            sleep_time=self.SleepTime,
        )

        return cm

    # TODO: This block of code will be uncommented on On, Off and Standby commands are implemented
    # def init_command_objects(self):
    #     """
    #     Initialises the command handlers for commands supported by this device.
    #     """
    #     super().init_command_objects()
    #     args = ()
    #     for (command_name, command_class) in [
    #         ("On", On),
    #         ("Off", Off),
    #         ("Standby", Standby),
    #     ]:
    #         command_obj = command_class(
    #             self.component_manager,
    #             self.op_state_model,
    #             *args,
    #             logger=self.logger,
    #         )
    #         self.register_command_object(command_name, command_obj)


# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    """
    Runs the CspMasterLeafNodeMid.
    :param args: Arguments internal to TANGO

    :param kwargs: Arguments internal to TANGO

    :return: CspMasterLeafNodeMid TANGO object.
    """
    return run((CspMasterLeafNode,), args=args, **kwargs)


if __name__ == "__main__":
    main()
