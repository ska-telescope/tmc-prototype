# Delete this module once ska-tmc-common package is ready
"""
This module specifies the operational state ("opState") model for SKA LMC Tango devices.

It consists of:

* an underlying state machine: :py:class:`._OpStateMachine`
* an :py:class:`.OpStateModel` that maps state machine state to device
  "op state". This "op state" is currently represented as a
  :py:class:`tango.DevState` enum value, and reported using the tango
  device's special ``state()`` method.
"""
from ska_tango_base.base import OpStateModel
from tango import DevState
from transitions.extensions import LockedMachine as Machine

__all__ = ["TMCOpStateModel"]


class TMCOpStateMachine(Machine):
    """
    State machine representing the operational state of the device.

    The operational state of a device is either the state of the system
    component that the device monitors, or a state that indicates why
    the device is not monitoring the system component.

    The post-init states supported are:

    * **ON**: the device is monitoring its telescope component and the
      component is turned on
    * **FAULT**: the device is monitoring its telescope component and
      the component has failed or is in an inconsistent state.

    There are also corresponding initialising states: **INIT_ON** and
    **INIT_FAULT**. These states allow for the underlying system
    component to change its state during long-running initialisation,
    and for a device to transition to an appropriate state at the end of
    initialisation.

    Finally, there is an **_UNINITIALISED** starting state, representing
    a device that hasn't started initialising yet.

    The actions supported are:

    * **init_invoked**: the device has started initialising
    * **init_completed**: the device has finished initialising
    * **component_on**: the component has been switched on
    """

    def __init__(self, callback=None, **extra_kwargs):
        """
        Initialise the state model.

        :param callback: A callback to be called when a transition
            implies a change to op state
        :type callback: callable
        :param extra_kwargs: Additional keywords arguments to pass to
            superclass initialiser (useful for graphing)
        """
        self._callback = callback

        states = [
            "_UNINITIALISED",
            "INIT_ON",
            "INIT_FAULT",
            "ON",
            "FAULT",
        ]

        transitions = [
            # Initial transition on the device starting initialisation
            {
                "source": "_UNINITIALISED",
                "trigger": "init_invoked",
                "dest": "INIT_ON",
            },
            {
                "source": [
                    "INIT_ON",
                    "INIT_FAULT",
                ],
                "trigger": "component_on",
                "dest": "INIT_ON",
            },
            {
                "source": [
                    "INIT_ON",
                    "INIT_FAULT",
                ],
                "trigger": "component_fault",
                "dest": "INIT_FAULT",
            },
            # Completion of initialisation
            {
                "source": "INIT_ON",
                "trigger": "init_completed",
                "dest": "ON",
            },
            {
                "source": "INIT_FAULT",
                "trigger": "init_completed",
                "dest": "FAULT",
            },
            # Changes in the state of the monitored component post-initialisation
            {
                "source": ["ON", "FAULT"],
                "trigger": "component_on",
                "dest": "ON",
            },
            {
                "source": ["ON", "FAULT"],
                "trigger": "component_fault",
                "dest": "FAULT",
            },
        ]

        super().__init__(
            states=states,
            initial="_UNINITIALISED",
            transitions=transitions,
            after_state_change=self._state_changed,
            **extra_kwargs,
        )
        self._state_changed()

    def _state_changed(self):
        """
        State machine callback that is called every time the op_state changes.

        Responsible for ensuring that callbacks are called.
        """
        if self._callback is not None:
            self._callback(self.state)


class TMCOpStateModel(OpStateModel):
    """
    This class implements the state model for device operational state ("opState").

    The model supports the following states, represented as values of
    the :py:class:`tango.DevState` enum.

    * **INIT**: the device is initialising.
    * **ON**: the device is monitoring its telescope component and the
      component is turned on
    * **FAULT**: the device is affected by a bug and a developer needs
      to work on it. All operations are denied.

    The actions supported are:

    * **init_invoked**: the device has started initialising
    * **init_completed**: the device has finished initialising
    * **component_on**: the component has been switched on
    """

    def __init__(self, logger, callback=None):
        super().__init__(logger, callback=callback)
        self._op_state_machine = TMCOpStateMachine(
            callback=self._op_state_changed
        )

    _op_state_mapping = {
        "_UNINITIALISED": None,
        "INIT_ON": DevState.INIT,
        "INIT_FAULT": DevState.INIT,
        "ON": DevState.ON,
        "FAULT": DevState.FAULT,
    }
