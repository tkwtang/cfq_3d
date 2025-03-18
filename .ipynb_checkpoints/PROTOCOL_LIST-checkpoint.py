# Exchange corners, Control exchange

protocol_list = []
protocol_list += [{
    'duration': 0.02,
    'phi_1x': 0.0,
    'phi_2x': 0.0,
    'phi_3x': 0,
    'mu_12': 0.2,
    'mu_13': 0.0,
    'mu_23': 0.0,
    'phi_1xdc': np.pi,
    'phi_2xdc': np.pi,
    'phi_3xdc': 0,
    'name': 'conditional_tilt_xz'
}] * 2

protocol_list[-1]['duration'] = 0.16

protocol_list += [{
    'duration': 0.02,
    'phi_1x': 0.0,
    'phi_2x': 0.0,
    'phi_3x': 0.0,
    'mu_12': 0.0,
    'mu_13': 0.0,
    'mu_23': 0.0,
    'phi_1xdc': 0.0,
    'phi_2xdc': 0.0,
    'phi_3xdc': 0.0,
    'name': 'conditional_tilt_xz'
}] * 2
protocol_list[-1]['duration'] = 10




# Exchange corners, Control corners

protocol_list = []
protocol_list += [{
    'duration': 0.02,
    'phi_1x': 0.0,
    'phi_2x': 0.0,
    'phi_3x': 0.0,
    'mu_12': 0.25,
    'mu_13': 0.0,
    'mu_23': 0.0,
    'phi_1xdc': np.pi,
    'phi_2xdc': np.pi,
    'phi_3xdc': 0,
    'name': 'conditional_tilt_xz'
}] * 2

protocol_list[-1]['duration'] = 0.27

protocol_list += [{
    'duration': 0.02,
    'phi_1x': 0.0,
    'phi_2x': 0.0,
    'phi_3x': 0.0,
    'mu_12': 0.0,
    'mu_13': 0.0,
    'mu_23': 0.0,
    'phi_1xdc': 0.0,
    'phi_2xdc': 0.0,
    'phi_3xdc': 0.0,
    'name': 'conditional_tilt_xz'
}] * 2
protocol_list[-1]['duration'] = 10