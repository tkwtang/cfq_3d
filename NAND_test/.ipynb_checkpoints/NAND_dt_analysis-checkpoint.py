import sys, os
sys.path.append(os.path.expanduser('~/source'))


import numpy as np
import importlib, os, datetime
from sus.protocol_designer import System, Protocol, Potential, Compound_Protocol
from sus.protocol_designer.protocol import sequential_protocol
from IPython import display
from IPython.display import HTML, Image
import matplotlib.animation as animation
from matplotlib.animation import FuncAnimation, PillowWriter


from quick_sim import setup_sim
from edward_tools.coupled_fq_potential import coupled_flux_qubit_non_linear_approx_pot, coupled_flux_qubit_non_linear_approx_force
from edward_tools.visualization import animate_sim_flux_qubit, plotFidelityBarChart, separate_by_state_2
from edward_tools.initial_state_sampling import extra_constraint_00_and_11_only
from NAND_PARAMETERS import *
import importlib

import kyle_tools as kt
import matplotlib.pyplot as plt
import json

from edward_tools import coupled_fq_protocol_library, cfq_runner
from edward_tools import coupled_fq_protocol_library

import edward_tools.cfq_batch_sweep as cfq_batch_sweep
import edward_tools.Analysis_tool.general_analysis_tools as general_analysis_tool
# from edward_tools.Analysis_tool.general_analysis_tools import show_phi_dc_with_time
import edward_tools.Analysis_tool.minimum_value_of_potential as minimum_value_of_potential
from edward_tools.couple_flux_qubit_metrics import fidelityEvaluation
from edward_tools import visualization

coupled_fq_protocol_library = importlib.reload(coupled_fq_protocol_library)
create_system = coupled_fq_protocol_library.create_system
get_potential_shot_at_different_t = coupled_fq_protocol_library.get_potential_shot_at_different_t
get_potential_shot_at_different_t_1D = coupled_fq_protocol_library.get_potential_shot_at_different_t_1D
create_simple_protocol_parameter_dict = coupled_fq_protocol_library.create_simple_protocol_parameter_dict
coupled_fq_runner = importlib.reload(cfq_runner)
coupled_fq_protocol_library = importlib.reload(coupled_fq_protocol_library)
create_system = coupled_fq_protocol_library.create_system
get_potential_along_a_1D_cutline = coupled_fq_protocol_library.get_potential_along_a_1D_cutline
plotCutlines = coupled_fq_protocol_library.plotCutlines

"""
# step 0: modify parameters
- All the parameters are stored in a separate file PARAMETER_INPUT
- You can override some of the parameters here.
"""


has_velocity = True

PHI_0 = 2.067833848 * 1e-15
k_B = 1.38e-23
T = 4.2
# T = 0.1
# T = 7
k_BT = k_B * T

C_factor = 1
L_factor = 1
R_factor = 400
# I_m_factor = 50
# I_m_factor = 15
I_m_factor = 0
time_scale = 1.0



I_p_1, I_p_2 = 5e-6 , 5e-6  # Amp
I_m_1, I_m_2 = 7e-9 * I_m_factor, 7e-9 * I_m_factor                           # Amp
R_1, R_2 = 1 * R_factor, 1 * R_factor                                         # ohm
C_1, C_2 = 500e-15 * C_factor, 500e-15 * C_factor                             # F

L_1, L_2 = 140e-12 * L_factor, 140e-12 * L_factor                             # H 
L_1, L_2 = 5e-12 * L_factor, 5e-12 * L_factor                             # H 
freq = 1/np.sqrt(C_1 * L_1)
characteristic_time = np.sqrt(C_1 * C_factor * L_1 * L_factor)


m_c = C_1
m_1 = C_1
m_2 = C_2
x_c = PHI_0 / (2 * np.pi)
time_scale_factor = 1
t_c = np.sqrt(L_1 * C_1)
v_c = x_c / t_c


U0_1 = m_c * x_c**2 / t_c**2 / k_BT
U0_2 = m_2 * x_c**2 / t_c**2 / k_BT
kappa_1, kappa_2, kappa_3, kappa_4 = 1/U0_1, 1/U0_1, 1/U0_1, 1/U0_1

lambda_1 = 2 * np.sqrt(L_1 * C_1) / (C_1 * R_1)
theta_1  = 1
eta_1    = np.sqrt(np.sqrt(L_1 * C_1)/ (R_1 * C_1)) * np.sqrt(2 * kappa_1 / 1**2)

lambda_2 = 2 * np.sqrt(L_1 * C_1) / (C_2 * R_2)
theta_2  = 1 / (C_2/C_1)
eta_2    = np.sqrt(np.sqrt(L_1 * C_1)/ (R_1 * C_1)) * np.sqrt(2 * kappa_2 * (R_1 * C_1**2) / (R_2 * C_2**2))

lambda_3 = 2 * np.sqrt(L_1 * C_1) / (C_1 * R_1)
theta_3  = 4
eta_3    = np.sqrt(np.sqrt(L_1 * C_1)/ (R_1 * C_1)) * np.sqrt(8 * kappa_3)

lambda_4 = 2 * np.sqrt(L_1 * C_1) / (C_2 * R_2)
theta_4  = 4 / (C_2/C_1)
eta_4    = np.sqrt(np.sqrt(L_1 * C_1)/ (R_1 * C_1)) * np.sqrt(8 * kappa_4 * (R_1 * C_1**2) / (R_2 * C_2**2))

gamma = 10


beta_1 = 2 * np.pi * L_1 * I_p_1 / PHI_0; 
beta_2 = 2 * np.pi * L_2 * I_p_2 / PHI_0;

beta_1 = 2.3
beta_2 = 2.3

# beta_1 = 2
# beta_2 = 2



d_beta_1 = 2 * np.pi * L_1 * I_m_1 / PHI_0; 
d_beta_2 = 2 * np.pi * L_2 * I_m_2 / PHI_0;


_damping_factor = 1
_lambda = np.array([lambda_1, lambda_2, lambda_3, lambda_4])
_theta  = np.array([theta_1, theta_2, theta_3, theta_4])
_eta  =   np.array([eta_1, eta_2, eta_3, eta_4])

v_1 = np.random.normal(0, np.sqrt(k_BT/m_1)) / v_c
v_2 = np.random.normal(0, np.sqrt(k_BT/m_2)) / v_c
v_3 = np.random.normal(0, np.sqrt(k_BT/(m_1/4))) / v_c
v_4 = np.random.normal(0, np.sqrt(k_BT/(m_2/4))) / v_c

for _ in range(0, 1):
    for _dt in [1/100, 1/500, 1/1000, 1/5000]:
    # for _dt in [1/100]:
        params = {}
        params['N'] = 1000
        params['dt'] = _dt
        params['lambda'] = 1
        params['beta'] = 1
        params['sim_params'] = [_lambda, _theta, _eta]
        params['target_work'] = None
        params['applyOffset'] = False
        params['measureWorkWithOffset'] = True
        params['monitor_work_dist_in_whole_process'] = True # To monitor the work process
        params['comment'] = "Experiment 2 (2024/10/11): dt analysis of conditional tilt with dt = 1/100 to 1/5000"
        params['capacitance'] = np.array([C_1, C_2, C_1/4, C_2/4])
        params['mass'] = np.array([1, 1, 1/4, 1/4])
        params['v_c'] = x_c/t_c
        params['k_BT'] = k_BT
        params['U0'] = U0_1
        params['as_step'] = np.s_[::100] # the time step to skep for the all_state
        params['percentage'] = 1 # For what percentage of the total sample do you want to keep in the output all_state
        
        """
        # step 1: Define potential
        """
        coupled_fq_default_param = [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, x_c]
        [phi_1_bound, phi_2_bound, phi_1dc_bound, phi_2dc_bound] = np.array([4, 4, 4, 4])/time_scale_factor

        coupled_fq_domain = [[-phi_1_bound, -phi_2_bound, -phi_1dc_bound, -phi_2dc_bound], \
                             [phi_1_bound, phi_2_bound, phi_1dc_bound, phi_2dc_bound]]

        # coupled_fq_pot = Potential(coupled_flux_qubit_pot_with_offset_at_00_xy, coupled_flux_qubit_force, 14, 4,\
        #                            default_params = coupled_fq_default_param,  relevant_domain = coupled_fq_domain)

        coupled_fq_pot = Potential(coupled_flux_qubit_non_linear_approx_pot, coupled_flux_qubit_non_linear_approx_force, 14, 4,\
                                   default_params = coupled_fq_default_param,  relevant_domain = coupled_fq_domain)


        """
        # step 2: Define initial condition and protocol
        """
        manual_domain=[np.array([-5, -5]), np.array([5, 5])]

        initial_parameter_dict = {
                "U0_1": U0_1,     "U0_2": U0_2,     "gamma_1": gamma,  "gamma_2": gamma,
                "beta_1": beta_1,   "beta_2": beta_2,   "d_beta_1": d_beta_1 ,   "d_beta_2": d_beta_2,
                "phi_1_x": phi_1_x_off,  "phi_2_x": phi_2_x_off,  "phi_1_dcx": phi_1_dcx_off,  "phi_2_dcx": phi_1_dcx_off,
                "M_12": M_12_off, 'x_c': x_c
        }

        zeroDissipation = False
        # zeroDissipation = True

        saveAllStates = False

        params['sim_params'] = [_lambda, _theta, _eta]

        if zeroDissipation:
            params['sim_params'] = [_lambda * 0, _theta, _eta * 0]

        params['circuit_parameters'] = {
            "C_factor":C_factor, "L_factor": L_factor, "R_factor": R_factor, "I_m_factor": I_m_factor, "T": T, 
            "I_p_1": I_p_1, "I_p_2": I_p_2, "I_m_1": I_m_1, "I_m_2": I_m_2,
            "R_1": R_1, "R_2": R_2, "C_1": C_1, "C_2": C_2, "L_1": L_1, "L_2": L_2, 
            "characteristic_time": np.sqrt(C_1 * C_factor * L_1 * L_factor),
            "phi_1_x_on": phi_1_x_on_12, "phi_2_x_on": phi_2_x_on_12,
            "phi_1_dcx_on": phi_1_dcx_on_12, "phi_2_dcx_on": phi_2_dcx_on_12, "M_12_on": M_12_on,
            "gamma": gamma
        }


        # bookmark
        initial_parameter_dict["phi_1_dcx"], initial_parameter_dict["phi_2_dcx"], initial_parameter_dict["M_12"] = \
        phi_1_dcx_off, phi_2_dcx_off, M_12_off


        initial_parameter_dict["phi_1_dcx"] = phi_1_dcx_off
        initial_parameter_dict["phi_2_dcx"] = phi_2_dcx_off
        initial_parameter_dict["phi_1_x"]   = phi_1_x_off
        initial_parameter_dict["phi_2_x"]   = phi_2_x_off
        initial_parameter_dict["M_12"]      = M_12_off

        
        ratio_array = [0.999] * 5
        fixed_time = 200
        protocol_list_variable_duration_without_KE_extraction = [
            # forward
            # create_CE_Protocol(fixed_time/4, CE_8, ratio_array),
            # create_CE_Protocol(fixed_time/4, CE_8),
            # create_CE_Protocol(fixed_time/2, KE_extraction_protocol_for_CE_8),
            # create_CE_Protocol(fixed_time/2, KE_extraction_protocol_for_CE_8),
            # create_CE_Protocol(fixed_time/2, four_well),

            create_CE_Protocol(fixed_time, lower_V_wells),
            create_CE_Protocol(fixed_time, flip_V),

#             create_CE_Protocol(fixed_time, lower_H_wells),
#             create_CE_Protocol(fixed_time, flip_H),
            create_CE_Protocol(fixed_time, four_well),
        ]

        protocol_list = protocol_list_variable_duration_without_KE_extraction
        
        
        """
        # create initial state
        """
        regenerate_init_state = False
        regenerate_init_state = True
        if regenerate_init_state:
            initial_potential_protocol_list = [create_CE_Protocol(10, four_well)]
            init_state_saved = cfq_batch_sweep.create_initial_state(initial_parameter_dict, initial_potential_protocol_list, coupled_fq_pot, params)
        else:
            init_state_saved = np.load("four_well_default_init_state_N_1000.npy")
            pass

        init_state_used = init_state_saved

        
        """
        # create cfqr object
        """
        computation_protocol_parameter_dict = coupled_fq_protocol_library.customizedProtocol(initial_parameter_dict, \
                                                                    protocol_list)
        storage_protocol, comp_protocol = create_system(computation_protocol_parameter_dict, modifiedFunction = None)

        cfqr = cfq_runner.coupledFluxQubitRunner(potential = coupled_fq_pot, 
                    params = params, storage_protocol= storage_protocol,
                    computation_protocol= comp_protocol, 
                    protocol_list = protocol_list, 
                    has_velocity=has_velocity)

        protocol_time_array, protocol_time_index_array, protocol_all_time_array, protocol_time_all_index_array = cfqr.createProtocolTimeArray(protocol_list, params)
        cfqr.initialize_sim()
        # cfqr.set_sim_attributes(init_state=init_state_saved)
        cfqr.set_sim_attributes(init_state=init_state_used)

        
        """
        # simulation
        """
        pickle_save_path = os.path.join("..", "coupled_flux_qubit_protocol", "simulation_protocol_history")
        
        simResult = cfq_batch_sweep.simulateSingleCoupledFluxQubit(params, initial_parameter_dict, protocol_list, potential = coupled_fq_pot, potential_default_param = coupled_fq_default_param, initial_state = init_state_used, manual_domain = manual_domain, phi_1_dcx = phi_1_dcx,  phi_2_dcx = phi_2_dcx, measure_all_states=saveAllStates, has_velocity = has_velocity, pickle_save_path = pickle_save_path)
        
        
        
        """
        # save results
        """
        cfq_batch_sweep.saveSimulationResult(simResult, U0_1, timeOrStep = 'step', save = True, save_final_state = False, saveFolderPath = "../coupled_flux_qubit_protocol/coupled_flux_qubit_data_gallery")

        step_time_array = np.cumsum(np.array([x["duration"] for x in protocol_list]))/params['dt']
        name_array = [x["name"] for x in protocol_list]
        mean_work = np.mean(simResult["work_distribution"])
        jarzyn_term = np.mean(np.exp(-simResult["work_distribution"]))
        print("The simulation id is", simResult["simulation_data"]["simulation_id"])
        print(params['comment'])
        print(f"N = {params['N']}, dt = {params['dt']}")
        print(f"phi_1dcx_on: {phi_1_dcx_on_12}, phi_2dcx_on: {phi_2_dcx_on_12}, M_12_on: {M_12_on}")
        print(f"L_factor = {L_factor}, C_factor = {C_factor}, I_m_factor = {I_m_factor}")
        print([x["duration"] for x in protocol_list])
        print(f'jarzyn = {jarzyn_term}, mean work = {mean_work}')
