import datetime
import importlib.resources
import threading
from datetime import datetime, timedelta
import json
import logging
import pytz
import numpy as np
import katpoint
from cspsubarrayleafnode.device_data import DeviceData
from ska.base.control_model import ObsState
from tmc.common.tango_client import TangoClient

class DelayManager:
    __instance = None
    def __init__(self, logger = None):
        """Private constructor of the class"""
        if DelayManager.__instance is not None:
            raise Exception("This is singletone class")
        else:
            DelayManager.__instance = self

        if logger is None:
            self.logger = logging.getLogger(__name__)
        else:
            self.logger = logger

        self.fsids_list = []
        self.delay_model_json = {}
        self.device_data = DeviceData.get_instance()
        self._DELAY_UPDATE_INTERVAL = 10
        # _delay_in_advance variable (in seconds) is added to current timestamp and is used to calculate advance
        # delay coefficients.
        self._delay_in_advance = 60
    
    @staticmethod
    def get_instance():
        if DelayManager.__instance is None:
            DelayManager()
        return DelayManager.__instance


    def start(self):
        ## Start thread to update delay model ##
        # Start thread to update delay model
        # Create event
        self._stop_delay_model_event = threading.Event()
        # create lock
        self.delay_model_lock = threading.Lock()
        # create thread
        self.logger.debug("Starting thread to calculate delay model.")
        self.delay_model_calculator_thread = threading.Thread(
            target=self.delay_model_handler,
            args=[self._DELAY_UPDATE_INTERVAL],
            daemon=False)
        self.delay_model_calculator_thread.start()

    def stop(self):
        # Stop thread to update delay model
        self.logger.debug("Stopping delay model thread.")
        self._stop_delay_model_event.set()
        self.delay_model_calculator_thread.join()

    def update_config_params(self):
        """
        In this method parameters related to the resources assigned, are updated every time assign, release
        or configure commands are executed.

        :param argin: None

        :return: None

        """
        assigned_receptors_dict = {}
        assigned_receptors = []

        self.logger.info("Updating config parameters.")

        # Load a set of antenna descriptions and construct Antenna objects from them
        with importlib.resources.open_text("cspsubarrayleafnode", "ska_antennas.txt") as f:
            descriptions = f.readlines()
        antennas = [katpoint.Antenna(line) for line in descriptions]
        # Create a dictionary including antenna objects
        antennas_dict = {ant.name: ant for ant in antennas}
        antenna_keys_list = antennas_dict.keys()
        for receptor in self.device_data.receptorIDList_str:
            if receptor in antenna_keys_list:
                assigned_receptors.append(antennas_dict[receptor])
                # Create a dictionary including antennas (objects) assigned to the Subarray
                assigned_receptors_dict[receptor] = antennas_dict[receptor]

        # Antenna having key 'ref_ant' from antennas_dict, is referred as a reference antenna.
        ref_ant = antennas_dict["ref_ant"]

        # Create DelayCorrection Object
        self.delay_correction_object = katpoint.DelayCorrection(assigned_receptors, ref_ant)
        self.antenna_names = list(self.delay_correction_object.ant_models.keys())

        # list of frequency slice ids
        for fsp_entry in self.device_data.fsp_ids_object:
            self.fsids_list.append(fsp_entry["fspID"])


    def calculate_geometric_delays(self, time_t0):
        """
        This method calculates geometric delay values (in Second) using KATPoint library. It requires delay
        correction object, timestamp t0 and target RaDec.
        Numpy library is used to convert delay values (in Seconds) to fifth order polynomial coefficients.
        Six timestamps from the time-frame t0 to t+10, are used to calculate delays per antenna. These six
        delay values are then used to calculate fifth order polynomial coefficients.
        In order to calculate delays in advance, timestamp t0 is considered to be one minute ahead of the
        the current timestamp.

        :param argin: time_t0

        :return: Dictionary containing fifth order polynomial coefficients per antenna per fsp.
        """
        delay_corrections_h_array_t0 = []
        delay_corrections_h_array_t1 = []
        delay_corrections_h_array_t2 = []
        delay_corrections_h_array_t3 = []
        delay_corrections_h_array_t4 = []
        delay_corrections_h_array_t5 = []
        delay_corrections_h_array_dict = {}
        delay_corrections_v_array_t0 = []
        delay_corrections_v_array_t1 = []
        delay_corrections_v_array_t2 = []
        delay_corrections_v_array_t3 = []
        delay_corrections_v_array_t4 = []
        delay_corrections_v_array_t5 = []

        # Delays are calculated for the timestamps between "t0 - 25" to "t0 + 25" at an interval of 10
        # seconds.
        timestamp_array = [time_t0 - timedelta(seconds=25), (time_t0 - timedelta(seconds=15)),
                            (time_t0 - timedelta(seconds=5)), (time_t0 + timedelta(seconds=5)),
                            (time_t0 + timedelta(seconds=15)), (time_t0 + timedelta(seconds=25))]

        for timestamp_index in range(0, len(timestamp_array)):
            # Calculate geometric delay value.
            delay = self.delay_correction_object._calculate_delays(self.device_data.target,
                                                                    str(timestamp_array[timestamp_index]))
            # Horizontal and vertical delay corrections for each antenna
            for i in range(0, len(delay)):
                if i % 2 == 0:
                    if timestamp_index == 0:
                        delay_corrections_h_array_t0.append(delay[i])
                    elif timestamp_index == 1:
                        delay_corrections_h_array_t1.append(delay[i])
                    elif timestamp_index == 2:
                        delay_corrections_h_array_t2.append(delay[i])
                    elif timestamp_index == 3:
                        delay_corrections_h_array_t3.append(delay[i])
                    elif timestamp_index == 4:
                        delay_corrections_h_array_t4.append(delay[i])
                    elif timestamp_index == 5:
                        delay_corrections_h_array_t5.append(delay[i])
                else:
                    if timestamp_index == 0:
                        delay_corrections_v_array_t0.append(delay[i])
                    elif timestamp_index == 1:
                        delay_corrections_v_array_t1.append(delay[i])
                    elif timestamp_index == 2:
                        delay_corrections_v_array_t2.append(delay[i])
                    elif timestamp_index == 3:
                        delay_corrections_v_array_t3.append(delay[i])
                    elif timestamp_index == 4:
                        delay_corrections_v_array_t4.append(delay[i])
                    elif timestamp_index == 5:
                        delay_corrections_v_array_t5.append(delay[i])

        # Convert delays in seconds to 5th order polynomial coefficients
        # x is always [-25, -15, -5, 5, 15, 25] as the delays are calculated for the timestamps between
        # "t0 - 25" to "t0 + 25" at an interval of 10 seconds.
        x = np.array([-25, -15, -5, 5, 15, 25])
        for i in range(0, len(self.antenna_names)):
            antenna_delay_list = []
            antenna_delay_list.append(delay_corrections_h_array_t0[i])
            antenna_delay_list.append(delay_corrections_h_array_t1[i])
            antenna_delay_list.append(delay_corrections_h_array_t2[i])
            antenna_delay_list.append(delay_corrections_h_array_t3[i])
            antenna_delay_list.append(delay_corrections_h_array_t4[i])
            antenna_delay_list.append(delay_corrections_h_array_t5[i])

            # Array including delay values per antenna for the timestamps between "t0 - 25" to "t0 + 25"
            # at an interval of 10 seconds.
            y = np.array(antenna_delay_list)

            # Fit polynomial to the values over 50-second range
            polynomial = np.polynomial.Polynomial.fit(x, y, 5)
            polynomial_coefficients = polynomial.convert().coef
            delay_corrections_h_array_dict[self.antenna_names[i]] = polynomial_coefficients
        return delay_corrections_h_array_dict


    def delay_model_handler(self, argin):
        """
        This method calculates the delay model for consumption of CSP subarray.
        The epoch value is the current timestamp value. Delay calculation starts when configure
        command is invoked. It calls the function which internally calculates delay values using KATPoint
        library and converts them to fifth order polynomial coefficients.

        :param argin: int.
            The argument contains delay model update interval in seconds.

        :return: None.

        """
        delay_update_interval = argin
        csp_sub_client_obj = TangoClient(self.device_data.csp_subarray_fqdn)
        while not self._stop_delay_model_event.isSet():
            if csp_sub_client_obj.deviceproxy.obsState in (ObsState.CONFIGURING, ObsState.READY, ObsState.SCANNING):
                self.delay_model_calculator()
                # update the attribute
                self.delay_model_lock.acquire()
                self.device_data._delay_model = json.dumps(self.delay_model_json)
                self.delay_model_lock.release()

                # wait for timer event
                self._stop_delay_model_event.wait(delay_update_interval)
            else:
                # TODO: This waiting on event is added temporarily to reduce high CPU usage.
                self._stop_delay_model_event.wait(0.02)
                self.device_data._delay_model = " "

        self.logger.debug("Stop event received. Thread exit.")

    def delay_model_calculator(self):
        self.logger.info("Calculating delays.")
        time_t0 = datetime.today() + timedelta(seconds=self._delay_in_advance)
        time_t0_utc = (time_t0.astimezone(pytz.UTC)).timestamp()
        self.logger.info("calling Calculate_geometric delays.")
        delay_corrections_h_array_dict = self.calculate_geometric_delays(time_t0)
        delay_model = []
        receptor_delay_model = []
        delay_model_per_epoch = {}
        for receptor in self.device_data.receptorIDList_str:
            receptor_delay_object = {}
            receptor_delay_object["receptor"] = receptor
            receptor_specific_delay_details = []
            for fsid in self.fsids_list:
                fsid_delay_object = {}
                fsid_delay_object["fsid"] = fsid
                delay_coeff_array = []
                receptor_delay_coeffs = delay_corrections_h_array_dict[receptor]
                for i in range(0, len(receptor_delay_coeffs)):
                    delay_coeff_array.append(receptor_delay_coeffs[i])
                fsid_delay_object["delayCoeff"] = delay_coeff_array
                receptor_specific_delay_details.append(fsid_delay_object)
            receptor_delay_object["receptorDelayDetails"] = receptor_specific_delay_details
            receptor_delay_model.append(receptor_delay_object)
        delay_model_per_epoch["epoch"] = str(time_t0_utc)
        delay_model_per_epoch["delayDetails"] = receptor_delay_model
        delay_model.append(delay_model_per_epoch)
        self.delay_model_json["delayModel"] = delay_model
        log_msg = "delay_model_json: " + str(self.delay_model_json)
        self.logger.debug(log_msg)    
