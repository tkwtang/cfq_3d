import numpy as np

phi_1_dcx , phi_2_dcx = 0, 0
phi_1_dc, phi_2_dc = phi_1_dcx, phi_2_dcx

phi_1_x_off, phi_2_x_off = 0, 0
phi_1_dcx_off, phi_2_dcx_off, M_12_off = 0, 0, 0




parameter_choice = ["chris", "squeeze_by_phi_2xdc", "squeeze_by_L", "experiment"]
parameter_choosen = parameter_choice[-1]

experiment_circuit_params_0 = {
    "L": 5e-12 * 2, "T": 4.2,
    "beta": 2.3, "d_beta": 0,
    "phi_1x": 0.58,   "phi_2x": 0.095, "phi_1xdc": 0, "phi_2xdc": 1.96,
    "M_12": 0.055
}


# experiment_circuit_params = {
#     "L": 5e-12, "T": 4.2,
#     "beta": 2.3, "d_beta": 0,
#     "phi_1x": 0.61,   "phi_2x": 0.10, "phi_1xdc": 0, "phi_2xdc": 1.79,
#     "M_12": 0.06
# }



def choose_NAND_Parameter(parameter_choice):
    print(parameter_choosen)
# Chris' parameter
# i, j = 1, 2

    if parameter_choice == "chris":
        phi_1_x_on_12 = 0.61
        phi_2_x_on_12 = 0.10
        phi_1_dcx_on_12 = 0.0
        phi_2_dcx_on_12 = 1.79

        # i, j = 2, 1
        phi_1_x_on_21 = 0.10
        phi_2_x_on_21 = 0.61
        phi_1_dcx_on_21 = 1.79
        phi_2_dcx_on_21 = 0.0

        M_12_on = 0.06


    if parameter_choice == "squeeze_by_phi_2xdc":
        # i, j = 1, 2
        phi_1_x_on_12 = 0.59
        phi_2_x_on_12 = 0.09
        phi_1_dcx_on_12 = 0.0
        phi_2_dcx_on_12 = 1.9

        # i, j = 2, 1
        phi_1_x_on_21 = 0.09
        phi_2_x_on_21 = 0.59
        phi_1_dcx_on_21 = 1.9
        phi_2_dcx_on_21 = 0.0

        M_12_on = 0.052

    if parameter_choice == "squeeze_by_L":
        # L_factor = 1.55 parameter
        phi_1_x_on_12 = 0.58
        phi_2_x_on_12 = 0.10
        phi_1_dcx_on_12 = 0.0
        phi_2_dcx_on_12 = 1.79

        # i, j = 2, 1
        phi_1_x_on_21 = 0.10
        phi_2_x_on_21 = 0.58
        phi_1_dcx_on_21 = 1.79
        phi_2_dcx_on_21 = 0.0

        M_12_on = 0.06


    if parameter_choice == "experiment":
        # L_factor = 1.5 parameter
        print(f"T = {experiment_circuit_params['T']}, L = {experiment_circuit_params['L']}")
        phi_1_x_on_12 = experiment_circuit_params['phi_1x']
        phi_2_x_on_12 = experiment_circuit_params['phi_2x']
        phi_1_dcx_on_12 = experiment_circuit_params['phi_1xdc']
        phi_2_dcx_on_12 = experiment_circuit_params['phi_2xdc']

        # i, j = 2, 1
        phi_1_x_on_21 = experiment_circuit_params['phi_2x']
        phi_2_x_on_21 = experiment_circuit_params['phi_1x']
        phi_1_dcx_on_21 = experiment_circuit_params['phi_2xdc']
        phi_2_dcx_on_21 = experiment_circuit_params['phi_1xdc']

        M_12_on = experiment_circuit_params['M_12']
        
    four_well = {
        "phi_1_x": phi_1_x_off, "phi_2_x": phi_2_x_off, "M_12": M_12_off, \
        "phi_1_dcx": phi_1_dcx_off, "phi_2_dcx": phi_2_dcx_off, "name":"four well"
    }

    CE_1 = {
        "phi_1_x": phi_1_x_on_12, "phi_2_x": phi_2_x_on_12, "M_12": M_12_on, \
        "phi_1_dcx": phi_1_dcx_off, "phi_2_dcx": phi_2_dcx_on_12, "name":"CE_1"
    }

    CE_3 = {
        "phi_1_x": phi_1_x_on_21, "phi_2_x": -phi_2_x_on_21, "M_12": -M_12_on,\
        "phi_1_dcx": phi_1_dcx_on_21, "phi_2_dcx": phi_2_dcx_off, "name":"CE_3"
    }


    CE_6 = {
        "phi_1_x": -phi_1_x_on_12, "phi_2_x": -phi_2_x_on_12, "M_12": +M_12_on, \
        "phi_1_dcx": phi_1_dcx_off, "phi_2_dcx": phi_2_dcx_on_12, "name":"CE_6"
    }

    CE_7 = {
        "phi_1_x": -phi_1_x_on_21, "phi_2_x": -phi_2_x_on_21, "M_12": +M_12_on,\
        "phi_1_dcx": phi_1_dcx_on_21, "phi_2_dcx": phi_2_dcx_off, "name":"CE_7"
    }

    CE_8 = {
        "phi_1_x": -phi_1_x_on_21, "phi_2_x": phi_2_x_on_21, "M_12": -M_12_on,\
        "phi_1_dcx": phi_1_dcx_on_21, "phi_2_dcx": phi_2_dcx_off, "name":"CE_8"
    }
    
    KE_extraction_protocol_for_CE_1 = {
        "phi_1_x": phi_1_x_on_12, "phi_2_x": 0.00, "M_12": 0.00, \
        "phi_1_dcx": phi_1_dcx_on_12, "phi_2_dcx": phi_2_dcx_on_12, "name":"KE_extraction_protocol"
    }


    KE_extraction_protocol_for_CE_8 = {
        "phi_1_x": 0.00, "phi_2_x": phi_2_x_on_21, "M_12": 0.00, \
        "phi_1_dcx": phi_1_dcx_on_21, "phi_2_dcx": phi_2_dcx_off, "name":"KE_extraction_protocol"
    }



    lower_H_wells = {
        "phi_1_x": 0, "phi_2_x": 0, "M_12": 0,  
        "phi_1_dcx":  np.pi, "phi_2_dcx": 0, "name":"lower_V_wells"
    }

    flip_H= {
        "phi_1_x": 0, "phi_2_x": 0, "M_12": -0.6,  
        "phi_1_dcx": np.pi, "phi_2_dcx": 0, "name":"Flip Vertically"
    }


    lower_V_wells = {
        "phi_1_x": 0, "phi_2_x": 0, "M_12": 0,  
        "phi_1_dcx": 0, "phi_2_dcx": np.pi, "name":"Flip Horizontally"
    }

    flip_V = {
        "phi_1_x": 0, "phi_2_x": 0, "M_12": 0.6,  
        "phi_1_dcx": 0, "phi_2_dcx": np.pi, "name":"Flip Horizontally"
    }

    return phi_1_x_on_12, phi_2_x_on_12, phi_1_dcx_on_12, phi_2_dcx_on_12, phi_1_x_on_21, phi_2_x_on_21, phi_1_dcx_on_21, phi_2_dcx_on_21, M_12_on, four_well, CE_1, CE_8, lower_H_wells, flip_H, lower_V_wells, flip_V, KE_extraction_protocol_for_CE_1, KE_extraction_protocol_for_CE_8





def generate_protocols_from_circuit_params(circuit_params):
    phi_1_x_on_12 = circuit_params['phi_1x']
    phi_2_x_on_12 = circuit_params['phi_2x']
    phi_1_dcx_on_12 = circuit_params['phi_1xdc']
    phi_2_dcx_on_12 = circuit_params['phi_2xdc']

    # i, j = 2, 1
    phi_1_x_on_21 = circuit_params['phi_2x']
    phi_2_x_on_21 = circuit_params['phi_1x']
    phi_1_dcx_on_21 = circuit_params['phi_2xdc']
    phi_2_dcx_on_21 = circuit_params['phi_1xdc']
    M_12_on = circuit_params['M_12']
    
    print(f"T = {circuit_params['T']}, L = {circuit_params['L']}")
    print(f"phi_1_x_on_12 = {phi_1_x_on_12}, phi_2_x_on_12 = {phi_2_x_on_12}, phi_1_dcx_on_12 = {phi_1_dcx_on_12}, phi_2_dcx_on_12 = {phi_2_dcx_on_12}, M_12_on = {M_12_on}")

    
    four_well = {
        "phi_1_x": phi_1_x_off, "phi_2_x": phi_2_x_off, "M_12": M_12_off, \
        "phi_1_dcx": phi_1_dcx_off, "phi_2_dcx": phi_2_dcx_off, "name":"four well"
    }

    CE_1 = {
        "phi_1_x": phi_1_x_on_12, "phi_2_x": phi_2_x_on_12, "M_12": M_12_on, \
        "phi_1_dcx": phi_1_dcx_off, "phi_2_dcx": phi_2_dcx_on_12, "name":"CE_1"
    }

    CE_3 = {
        "phi_1_x": phi_1_x_on_21, "phi_2_x": -phi_2_x_on_21, "M_12": -M_12_on,\
        "phi_1_dcx": phi_1_dcx_on_21, "phi_2_dcx": phi_2_dcx_off, "name":"CE_3"
    }


    CE_6 = {
        "phi_1_x": -phi_1_x_on_12, "phi_2_x": -phi_2_x_on_12, "M_12": +M_12_on, \
        "phi_1_dcx": phi_1_dcx_off, "phi_2_dcx": phi_2_dcx_on_12, "name":"CE_6"
    }

    CE_7 = {
        "phi_1_x": -phi_1_x_on_21, "phi_2_x": -phi_2_x_on_21, "M_12": +M_12_on,\
        "phi_1_dcx": phi_1_dcx_on_21, "phi_2_dcx": phi_2_dcx_off, "name":"CE_7"
    }

    CE_8 = {
        "phi_1_x": -phi_1_x_on_21, "phi_2_x": phi_2_x_on_21, "M_12": -M_12_on,\
        "phi_1_dcx": phi_1_dcx_on_21, "phi_2_dcx": phi_2_dcx_off, "name":"CE_8"
    }
    
    KE_extraction_protocol_for_CE_1 = {
        "phi_1_x": phi_1_x_on_12, "phi_2_x": 0.00, "M_12": 0.00, \
        "phi_1_dcx": phi_1_dcx_on_12, "phi_2_dcx": phi_2_dcx_on_12, "name":"KE_extraction_protocol"
    }


    KE_extraction_protocol_for_CE_8 = {
        "phi_1_x": 0.00, "phi_2_x": phi_2_x_on_21, "M_12": 0.00, \
        "phi_1_dcx": phi_1_dcx_on_21, "phi_2_dcx": phi_2_dcx_off, "name":"KE_extraction_protocol"
    }



    lower_H_wells = {
        "phi_1_x": 0, "phi_2_x": 0, "M_12": 0,  
        "phi_1_dcx":  np.pi, "phi_2_dcx": 0, "name":"lower_V_wells"
    }

    flip_H= {
        "phi_1_x": 0, "phi_2_x": 0, "M_12": -0.6,  
        "phi_1_dcx": np.pi, "phi_2_dcx": 0, "name":"Flip Vertically"
    }


    lower_V_wells = {
        "phi_1_x": 0, "phi_2_x": 0, "M_12": 0,  
        "phi_1_dcx": 0, "phi_2_dcx": np.pi, "name":"Flip Horizontally"
    }

    flip_V = {
        "phi_1_x": 0, "phi_2_x": 0, "M_12": 0.6,  
        "phi_1_dcx": 0, "phi_2_dcx": np.pi, "name":"Flip Horizontally"
    }

    return phi_1_x_on_12, phi_2_x_on_12, phi_1_dcx_on_12, phi_2_dcx_on_12, phi_1_x_on_21, phi_2_x_on_21, phi_1_dcx_on_21, phi_2_dcx_on_21, M_12_on, four_well, CE_1, CE_8, lower_H_wells, flip_H, lower_V_wells, flip_V, KE_extraction_protocol_for_CE_1, KE_extraction_protocol_for_CE_8


def create_CE_Protocol(_t, _CE, ratio = [1, 1, 1, 1, 1]):
    return {
        "duration": _t, 
        "phi_1_x": _CE["phi_1_x"] * ratio[0] , "phi_2_x": _CE["phi_2_x"] * ratio[1], 
        "M_12": _CE["M_12"] * ratio[2], "phi_1_dcx": _CE["phi_1_dcx"] * ratio[3], 
        "phi_2_dcx": _CE["phi_2_dcx"] * ratio[4], "name": _CE["name"]
    }


mapping_index = {"00": 0, "01": 1, "10": 2, "11": 3}

mapping_state_1_to_state_2_dict_CE = {"00": ["00"], "01": ["01"], "10": ["00"], "11": ["11"]}

mapping_state_1_to_state_2_dict_NAND = {"00": ["11"], "01": ["11"], "10": ["11"], "11": ["00"]}