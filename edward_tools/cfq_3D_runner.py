import sys
import os
import numpy as np
from sus.protocol_designer import System, Protocol, Potential, Compound_Protocol
from kyle_tools.multisim import SimManager, FillSpace
from SimRunner import SaveParams, SaveSimOutput, SaveFinalWork
from infoenginessims.simprocedures import basic_simprocedures as sp
from infoenginessims.simprocedures import running_measurements as rp
from infoenginessims.simprocedures import trajectory_measurements as tp
from infoenginessims.simprocedures.basic_simprocedures import ReturnFinalState, MeasureWorkDone, MeasureStepValue
from scipy.optimize import fsolve
from IPython.display import Image
from edward_tools import coupled_fq_protocol_library
from quick_sim import setup_sim
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from .initial_state_sampling import self_defined_initial_state
from scipy import optimize
from numba import njit

default_params_dict = {}

pColor = {"00": "#061DF7", "01": "#FCEF51", "10": "#3FC7F2", "11": "#F187F4"}

@njit
def binary_partition(positions, boundary=0):
    '''
    takes a set of position coordinates and sets each value to either 0 or 1 depending on if it is below or above the boundary
    '''
    return (np.sign(positions-boundary)+1)/2


class coupledFluxQubitRunner(SimManager):
    def __init__(self, potential = None, name_func = [None, None], params = default_params_dict, potential_default_param = None, storage_protocol = None, computation_protocol = None , measure_all_states = False, protocol_list = None, has_velocity = True):
        """
        params: parameters for the simulation such as time, lambda, theta and eta
        override_potential_parameter: to override the default parameter for the potential
        """
        self.potential = potential
        self.params = params
        self.save_name = name_func
        self.has_velocity = has_velocity
        self.override_potential_parameter = potential_default_param
        self.storage_protocol = storage_protocol
        self.computation_protocol = computation_protocol
        self.save_procs =  [SaveParams(), SaveSimOutput(), SaveFinalWork()]
        self.sampleSize = round(self.params['N'] * params['percentage'])
        self.as_step = params['as_step']
        self.measure_all_state = measure_all_states
        self.protocol_list = protocol_list
        self.pColor = {"00": "#061DF7", "01": "#FCEF51", "10": "#3FC7F2", "11": "#F187F4"}
        self.protocol_key = ['U0_1', 'U0_2', 'gamma_1', 'gamma_2', 'beta_1', 'beta_2', 'd_beta_1', 'd_beta_2', 'phi_1_x', 'phi_2_x', 'phi_1_dcx', 'phi_2_dcx', 'M_12', 'x_c']


        def verify_param(self, key, val):
            return True

    def initialize_sim(self):
        self.potential.default_params = self.override_potential_parameter
        self.eq_protocol = self.storage_protocol or  self.potential.trivial_protocol().copy()

        self.potential.default_params = np.array(self.override_potential_parameter)
        self.protocol = self.computation_protocol or self.potential.trivial_protocol().copy()
        # print(f"from fq_runner.py: system.protocol.t_i = {self.protocol.t_i}, system.protocol.t_f = {self.protocol.t_f}")

        self.eq_system = System(self.eq_protocol, self.potential)
        self.eq_system.axes_label = ["phi_1", "phi_2", "phi_3", "phi_1dc", "phi_2dc", "phi_3dc"]
        self.eq_system.has_velocity = self.has_velocity
        self.eq_system.capacitance = self.params['capacitance']
        self.eq_system.mass = self.params['mass']
        self.eq_system.v_c = self.params['v_c']
        self.eq_system.k_BT = self.params['k_BT']
        self.eq_system.U0 = self.params['U0']

        self.system = System(self.protocol, self.potential)
        self.system.axes_label = ["phi_1", "phi_2", "phi_3", "phi_1dc", "phi_2dc", "phi_3dc"]
        self.system.has_velocity = self.has_velocity
        self.system.capacitance = self.params['capacitance']
        self.system.mass = self.params['mass']
        self.system.v_c = self.params['v_c']
        self.system.k_BT = self.params['k_BT']
        self.system.U0 = self.params['U0']

        self.createProtocolTimeArray(self.protocol_list, self.params)


    def set_sim_attributes(self, init_state = None, manual_domain = None, axes = None, percentage = 1, as_step = np.s_[::], verbose = True, extra_constraint = None):
        if init_state is not None:
            print("use old initial_state")
            self.init_state = init_state
        else:
            print("generating new initial_state")
            if extra_constraint:
                self.init_state = self_defined_initial_state(self.eq_system, self.params['N'], extra_constraint = extra_constraint)
            else:
                self.init_state = self.eq_system.eq_state(self.params['N'], t=0, resolution = 20, beta=self.params['beta'], manual_domain = manual_domain, axes = axes)

        print(f"as step value: {self.as_step}, sampleSize: {self.sampleSize}" )


        if self.params['measureWorkWithOffset'] == True:
            work_measurement_procedure = sp.MeasureWorkDoneWithOffset(rp.get_dW, trial_request=np.s_[::self.sampleSize], step_request=self.as_step, protocol_time_index_array = self.params['protocol_time_index_array'], measurement_params =  self.params)
        else:
            work_measurement_procedure = sp.MeasureWorkDone(rp.get_dW, trial_request=np.s_[::self.sampleSize], step_request=self.as_step)

        self.procs = [work_measurement_procedure, sp.ReturnFinalState()]


        if self.measure_all_state:
            self.procs.append(sp.MeasureAllState(trial_request=np.s_[:self.sampleSize], step_request=self.as_step),)


        if verbose:
            print(f"from cfq_runner.py, The as_step is {as_step} and dt is {self.params['dt']}")

        # edward added this, to override the 200 states only in all states.
        # self.procs[1] = sp.MeasureAllState()

        sim_kwargs = {
                        'damping':self.params['lambda'],
                        'temp':1/self.params['beta'],
                        'dt':self.params['dt'],
                        'procedures':self.procs,
                        'sim_params': self.params['sim_params']
            }

        self.sim = setup_sim(self.system, self.init_state, verbose = verbose,**sim_kwargs)
        self.sim.reference_system = self.eq_system

        return


    def createProtocolTimeArray(self, protocol_list, params):
        """Return the following four arrays: protocol_time_array, protocol_time_index_array, protocol_all_time_array, protocol_all_time_index_array"""
        protocol_time_array = [item["duration"] for item in protocol_list]
        protocol_time_array.insert(0, 0)
        protocol_time_array = np.cumsum(protocol_time_array)

        protocol_time_index_array = protocol_time_array / params['dt'] - 1
        protocol_time_index_array[0] = 0
        protocol_time_index_array = protocol_time_index_array.astype(int)

        protocol_all_time_index_array = np.array(range(0, int(protocol_time_index_array[-1]) + 2))
        protocol_all_time_array = protocol_all_time_index_array * params['dt']

        params['protocol_time_array'] = protocol_time_array
        params['protocol_time_index_array'] = protocol_time_index_array
        self.protocol_time_array = protocol_time_array
        self.protocol_time_index_array = protocol_time_index_array
        self.protocol_all_time_array = protocol_all_time_array
        self.protocol_all_time_index_array = protocol_all_time_index_array

        return protocol_time_array, protocol_time_index_array, protocol_all_time_array, protocol_all_time_index_array

    def get_all_state(self):
        """get the all_state result from the output"""
        return self.sim.output.all_state['states']

    def separate_by_state(self, state):
        bool_array_000 = binary_partition(state[:, 0:3, 0]) == np.array([0., 0., 0.])
        index_of_000 = np.all(bool_array_000, axis=1)

        bool_array_001 = binary_partition(state[:, 0:3, 0]) == np.array([0., 1., 0.])
        index_of_001 = np.all(bool_array_001, axis=1)

        bool_array_010 = binary_partition(state[:, 0:3, 0]) == np.array([1., 0., 0.])
        index_of_010 = np.all(bool_array_010, axis=1)

        bool_array_011 = binary_partition(state[:, 0:3, 0]) == np.array([1., 1., 0.])
        index_of_011 = np.all(bool_array_011, axis=1)


        bool_array_100 = binary_partition(state[:, 0:3, 0]) == np.array([0., 0., 1.])
        index_of_100 = np.all(bool_array_100, axis=1)

        bool_array_101 = binary_partition(state[:, 0:3, 0]) == np.array([0., 1., 1.])
        index_of_101 = np.all(bool_array_101, axis=1)

        bool_array_110 = binary_partition(state[:, 0:3, 0]) == np.array([1., 0., 1.])
        index_of_110 = np.all(bool_array_110, axis=1)

        bool_array_111 = binary_partition(state[:, 0:3, 0]) == np.array([1., 1., 1.])
        index_of_111 = np.all(bool_array_111, axis=1)

        return {
            "000": index_of_000, "001": index_of_001, "010": index_of_010, "011": index_of_011,
            "100": index_of_100, "101": index_of_101, "110": index_of_110, "111": index_of_111
        }
