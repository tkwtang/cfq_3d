import sys, os
sys.path.append(os.path.expanduser('~/source'))

import numpy as np
from sus.protocol_designer import System, Protocol, Potential, Compound_Protocol
from sus.protocol_designer.protocol import sequential_protocol
from IPython import display
from IPython.display import HTML
from quick_sim import setup_sim
from edward_tools.coupled_fq_potential import coupled_flux_qubit_non_linear_approx_pot, coupled_flux_qubit_non_linear_approx_force
import edward_tools.fq_runner as fq_runner
from edward_tools.visualization import animate_sim_flux_qubit
from edward_tools.initial_state_sampling import extra_constraint_00_and_11_only
from PARAMETER_INPUT import *
from PARAMETER_INPUT import _lambda, _theta, _eta


import kyle_tools as kt
import matplotlib.pyplot as plt

import importlib, os, datetime
from edward_tools import coupled_fq_protocol_library, cfq_runner
from edward_tools import coupled_fq_protocol_library
import edward_tools.cfq_batch_sweep as cfq_batch_sweep



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


for _t_4 in [40, 60, 80, 100, 120, 140, 160, 180, 200]:
    # override parameters
    PHI_0 = 2.067833848 * 1e-15
    k_B = 1.38e-23
    T = 0.5
    k_BT = k_B * T

    L_factor = 1
    C_factor = 50

    I_p_1, I_p_2 = 2e-6 , 2e-6  # Amp
    I_m_1, I_m_2 = 7e-9, 7e-9                          # Amp
    R_1, R_2 = 371, 371                                # ohm
    C_1, C_2 = 4e-9 * C_factor, 4e-9 * C_factor                              # F
    L_1, L_2 = 1e-9 * L_factor, 1e-9 * L_factor        # H 

    quick_doubler = lambda x1, x2: np.hstack([np.array([x1] * 2), np.array([x2]*2)])
    I_p, I_m = quick_doubler(I_p_1, I_p_2), quick_doubler(I_m_1, I_m_2)

    m_c = C_1
    m_1 = C_1
    m_2 = C_2
    x_c = PHI_0 / (2 * np.pi)
    time_scale_factor = 1
    t_c = np.sqrt(L_1 * C_1)


    U0_1 = m_c * x_c**2 / t_c
    U0_2 = m_2 * x_c**2 / t_c
    kappa_1, kappa_2, kappa_3, kappa_4 = k_BT/U0_1, k_BT/U0_1, k_BT/U0_1, k_BT/U0_1




    lambda_1 = 2 * np.sqrt(L_1 * C_1) / (C_1 * R_1)
    theta_1  = 1
    eta_1    = (L_1 * C_1 / R_1**2)**0.25 * np.sqrt(2 * kappa_1)

    lambda_2 = 2 * np.sqrt(L_1 * C_1) / (C_2 * R_2)
    theta_2  = 1 / (C_2/C_1)
    eta_2    = (L_1 * C_1 / R_1**2)**0.25 * np.sqrt(2 * kappa_2 * (R_1 * C_1) / (R_2 * C_2))

    lambda_3 = 2 * np.sqrt(L_1 * C_1) / (C_1 * R_1)
    theta_3  = 4
    eta_3    = (L_1 * C_1 / R_1**2)**0.25 * np.sqrt(2 * kappa_3)

    lambda_4 = 2 * np.sqrt(L_1 * C_1) / (C_2 * R_2)
    theta_4  = 4 / (C_2/C_1)
    eta_4    = (L_1 * C_1 / R_1**2)**0.25 * np.sqrt(2 * kappa_4 * (R_1 * C_1) / (R_2 * C_2))

    gamma = 20


    beta_1 = 2 * np.pi * L_1 * I_p_1 / PHI_0; 
    beta_2 = 2 * np.pi * L_2 * I_p_2 / PHI_0;

    d_beta_1 = 2 * np.pi * L_1 * I_m_1 / PHI_0; 
    d_beta_2 = 2 * np.pi * L_2 * I_m_2 / PHI_0;


    _lambda = np.array([lambda_1, lambda_2, lambda_3, lambda_4])
    _theta  = np.array([theta_1, theta_2, theta_3, theta_4])
    _eta  =   np.array([eta_1, eta_2, eta_3, eta_4])

    """
    # step 0: modify parameters
    - All the parameters are stored in a separate file PARAMETER_INPUT
    - You can override some of the parameters here.
    """
    params = {}
    params['N'] = 10_000
    params['dt'] = 1/100_0
    params['lambda'] = 1
    params['beta'] = 1
    params['sim_params'] = [_lambda, _theta, _eta]
    params['target_work'] = None
    params['comment'] = "Experiment 1 (2024/2/8) Bit erasure minimize work done test"

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
    # phi_1_dcx, phi_2_dcx = 3, 3
    phi_1_dcx, phi_2_dcx = 0, 0
    phi_1_dc, phi_2_dc = phi_1_dcx, phi_2_dcx

    phi_1_dcx_off = 0
    phi_2_dcx_off = 0
    M_12_off = 0

    # bookmark
    phi_1_dcx_on = 3.0
    phi_2_dcx_on = 3.0
    M_12_on = -0.6

    initial_parameter_dict = {
            "U0_1": U0_1,     "U0_2": U0_2,     "gamma_1": gamma,  "gamma_2": gamma,
            "beta_1": beta_1,   "beta_2": beta_2,   "d_beta_1": d_beta_1 ,   "d_beta_2": d_beta_2,
            "phi_1_x": 0,  "phi_2_x": 0,  "phi_1_dcx": phi_1_dcx_off,  "phi_2_dcx": phi_1_dcx_off,
            "M_12": M_12_off, 'x_c': x_c
    }


    zeroDissipation = False
    params['sim_params'] = [_lambda, _theta, _eta]
    if zeroDissipation:
        params['sim_params'] = [_lambda * 0, _theta, _eta * 0]

    TR_initial_condition = [
        (phi_1_dcx_off, phi_2_dcx_off, M_12_off), 
        (phi_1_dcx_off, phi_2_dcx_on,  M_12_off), 
        (phi_1_dcx_off, phi_2_dcx_on,  M_12_on), 
        (phi_1_dcx_off, phi_2_dcx_off, M_12_on), 
        (phi_1_dcx_off, phi_2_dcx_off, M_12_off), 
        (phi_1_dcx_on,  phi_2_dcx_off, M_12_off)]

    protocol_index = 0

    # bookmark
    # initial_parameter_dict["phi_1_dcx"], initial_parameter_dict["phi_2_dcx"], initial_parameter_dict["M_12"] = TR_initial_condition[protocol_index-1]
    initial_parameter_dict["phi_1_dcx"], initial_parameter_dict["phi_2_dcx"], initial_parameter_dict["M_12"] = \
    TR_initial_condition[0]

    rest = lambda t: {"duration": t, "name":"rest"}
    duration_t = 40
    # protocol_list = [
    #     # forward
    #     {"duration":duration_t, "phi_1_dcx": phi_1_dcx_off, "phi_2_dcx": phi_2_dcx_on,  "M_12": M_12_off,  "name":"(1) mix in y direction"},
    #     {"duration":duration_t, "phi_1_dcx": phi_1_dcx_off, "phi_2_dcx": phi_2_dcx_on,  "M_12": M_12_on,   "name":"(2) conditional tilt"},
    #     {"duration":duration_t, "phi_1_dcx": phi_1_dcx_off, "phi_2_dcx": phi_2_dcx_off, "M_12": M_12_on,   "name":"(3) raise the barrier"},
    #     # {"duration":duration_t, "phi_1_dcx": phi_1_dcx_on,  "phi_2_dcx": phi_2_dcx_off, "M_12": M_12_on,  "name": "(4) conditional tilt in x"}, 
    #     # {"duration":duration_t, "phi_1_dcx": phi_1_dcx_on,  "phi_2_dcx": phi_2_dcx_off, "M_12": M_12_off,  "name":"(5) mix in x direction"}, 
    #     {"duration":duration_t, "phi_1_dcx": phi_1_dcx_off, "phi_2_dcx": phi_2_dcx_off, "M_12": M_12_off,  "name":"(6) 4 well potential"}, 

    # ]

    protocol_list = [
        # forward
        {"duration": 120, "phi_1_dcx": phi_1_dcx_off, "phi_2_dcx": phi_2_dcx_on,  "M_12": M_12_off,  "name":"(1) mix in y direction"},
        {"duration": 200, "phi_1_dcx": phi_1_dcx_off, "phi_2_dcx": phi_2_dcx_on,  "M_12": M_12_on,   "name":"(2) conditional tilt"},
        {"duration": 180, "phi_1_dcx": phi_1_dcx_off, "phi_2_dcx": phi_2_dcx_off, "M_12": M_12_on,   "name":"(3) raise the barrier"},
        # {"duration": 40, "phi_1_dcx": phi_1_dcx_on,  "phi_2_dcx": phi_2_dcx_off, "M_12": M_12_on,  "name": "(4) conditional tilt in x"}, 
        # {"duration": 100, "phi_1_dcx": phi_1_dcx_on,  "phi_2_dcx": phi_2_dcx_off, "M_12": M_12_off,  "name":"(5) mix in x direction"}, 
        {"duration": _t_4, "phi_1_dcx": phi_1_dcx_off, "phi_2_dcx": phi_2_dcx_off, "M_12": M_12_off,  "name":"(6) 4 well potential"}, 

    ]

    protocol_time_array = [item["duration"] for item in protocol_list]
    protocol_time_array.insert(0, 0)


    """
    # step 3: create the relevant storage protocol and computation protocol
    """
    computation_protocol_parameter_dict = coupled_fq_protocol_library.customizedProtocol(initial_parameter_dict, \
                                                                        protocol_list)
    storage_protocol, comp_protocol = create_system(computation_protocol_parameter_dict)

    """
    # step 4: create the coupled_fq_runner
    """
    cfqr = cfq_runner.coupledFluxQubitRunner(potential = coupled_fq_pot, params = params, \
                                                    storage_protocol= storage_protocol, \
                                                    computation_protocol= comp_protocol, measure_all_states=True)
    cfqr.initialize_sim()
    # cfqr.set_sim_attributes(extra_constraint=extra_constraint_00_and_11_only)
    cfqr.set_sim_attributes()
    init_state_saved = cfqr.init_state

    manual_domain=[np.array([-5, -5])/time_scale_factor, np.array([5, 5])/time_scale_factor]
    mapping_state_1_to_state_2_dict = {"00": ["00", "10"], "01": ["00", "10"], "10": ["01", "11"], "11": ["01", "11"]}

    # step 5: perform simulations

    simResult = cfq_batch_sweep.simulateSingleCoupledFluxQubit(params, initial_parameter_dict, protocol_list, \
                            potential = coupled_fq_pot, potential_default_param = coupled_fq_default_param,            
                            initial_state = init_state_saved, manual_domain = manual_domain, \
                            phi_1_dcx = phi_1_dcx,  phi_2_dcx = phi_2_dcx, \
                            percentage = 1, as_step = np.s_[::], measure_all_states=False)

    # 100, w_mena = 1.37, jarzyn = 0.342
    # 80, w_mena = 1.37, jarzyn = 0.342
    # 40, w_mena = 1.36, jarzyn = 0.34
    cfq_batch_sweep.saveSimulationResult(simResult, U0_1, timeOrStep = 'step', save = True, save_final_state = False, saveFolderPath = "../coupled_flux_qubit_protocol/coupled_flux_qubit_data_gallery")

    print("The simulation id is", simResult["simulation_data"]["simulation_id"])