import numpy as np
import os, sys
from sus.protocol_designer import System, Protocol, Potential, Compound_Protocol
from PARAMETER_INPUT import PHI_0, x_c

[phi_1_bound, phi_2_bound, phi_3_bound, phi_1dc_bound, phi_2dc_bound, phi_3dc_bound] = [4, 4, 4, 4, 4, 4]

coupled_fq_domain = [[-phi_1_bound, -phi_2_bound, -phi_3_bound, -phi_1dc_bound, -phi_2dc_bound, -phi_3dc_bound], [phi_1_bound, phi_2_bound, phi_3_bound, phi_1dc_bound, phi_2dc_bound, phi_3dc_bound]]

{
    0: "U0_1", 1: "U0_2", 3: "U0_3", 4: "gamma_1", 5: "gamma_2", 6: "gamma_3", 7: "beta_1", 8: "beta_2",
    9: "beta_3", 10: "d_beta_1", 11: "d_beta_2", 12: "d_beta_3", 13: "phi_1ax", 14: "phi_1bx",
    15: "phi_2x", 16: "phi_3x", 17: "phi_1xdc", 18: "phi_2xdc", 19: "phi_3xdc", 20: "mu_12", 21: "mu_13"
}




def coupled_flux_qubit_2p5D_non_linear_approx_pot(phi_1, phi_2, phi_3, phi_1dc, phi_2dc, phi_3dc, params):
    """
    8D 4-well potential.

    Parmeters
    -------------
    phi: ndaray of dimension [N, 2]
    phi_dc: ndaray of dimension [N, 2]

    params: list / tuple
    - [U_0, g, beta, delta_beta, phi_x, phi_xdc ]: correspond to the energy scale, gamma
    """

    U0_1, U0_2, U0_3, gamma_1, gamma_2, gamma_3, beta_1, beta_2, beta_3, d_beta_1, d_beta_2, d_beta_3, phi_1ax, phi_1bx, phi_2x, phi_3x, phi_1xdc, phi_2xdc, phi_3xdc, mu_12, mu_13 = params

    U0_kBT_ratio = U0_1
    U0_2, U0_3 = U0_2 / U0_1, U0_3 / U0_1
    U0_1 = 1
    xi_12, xi_13 = 1 / (1 - mu_12**2), 1 / (1 - mu_13**2)

    u_11 = 1/4 * xi_12 * (phi_1 - phi_1ax)**2 + 1/4 * xi_13 * (phi_1 + phi_1ax)**2
    u_12 = 1/2 * gamma_1 * (phi_1dc - phi_1xdc)**2
    u_13 = beta_1 * np.cos(phi_1) * np.cos(phi_1dc/2)
    u_14 = d_beta_1 * np.sin(phi_1) * np.sin(phi_1dc/2)

    u_21 = 1/2 * xi_12 * (phi_2 - phi_2x)**2
    u_22 = 1/2 * gamma_2 * (phi_2dc - phi_2xdc)**2
    u_23 = beta_2 * np.cos(phi_2) * np.cos(phi_2dc/2)
    u_24 = d_beta_2 * np.sin(phi_2) * np.sin(phi_2dc/2)

    u_31 = 1/2 * xi_13 * (phi_3 - phi_3x)**2
    u_32 = 1/2 * gamma_3 * (phi_3dc - phi_3xdc)**2
    u_33 = beta_3 * np.cos(phi_3) * np.cos(phi_3dc/2)
    u_34 = d_beta_3 * np.sin(phi_3) * np.sin(phi_3dc/2)

    u_4 = mu_12 * xi_12 * (phi_1 - phi_1ax) * (phi_2 - phi_2x) + mu_13 * xi_13 * (phi_1 + phi_1bx) * (phi_3 - phi_3x)

    U = (u_11 + u_12 + u_13 + u_14) + (u_21 + u_22 + u_23 + u_24) + (u_31 + u_32 + u_33 + u_34) + u_4

    return U * U0_kBT_ratio



def coupled_flux_qubit_2p5D_non_linear_approx_force(phi_1, phi_2, phi_3, phi_1dc, phi_2dc, phi_3dc, params):
    """
    8D 4-well potential.

    Parmeters
    -------------
    phi: ndaray of dimension [N, 2]
    phi_dc: ndaray of dimension [N, 2]

    params: list / tuple
    - [U_0, g, beta, delta_beta, phi_x, phi_xdc ]: correspond to the energy scale, gamma
    """

    U0_1, U0_2, U0_3, gamma_1, gamma_2, gamma_3, beta_1, beta_2, beta_3, d_beta_1, d_beta_2, d_beta_3, phi_1ax, phi_1bx, phi_2x, phi_3x, phi_1xdc, phi_2xdc, phi_3xdc, mu_12, mu_13 = params

    xi_12, xi_13 = 1 / (1 - mu_12**2), 1 / (1 - mu_13**2)

    U_dp1 = xi_12/2 * (phi_1 - phi_1ax) + xi_13/2 * (phi_1 + phi_1bx) + mu_12 * xi_12 * (phi_2 - phi_2x) + mu_13 * xi_13 * (phi_3 - phi_3x) - beta_1 * np.sin(phi_1) * np.cos(phi_1dc/2) + d_beta_1 * np.cos(phi_1) * np.sin(phi_1dc/2)

    U_dp2 = xi_12 * (phi_2 - phi_2x) + mu_12 * xi_12 * (phi_1 - phi_1ax) - beta_2 * np.sin(phi_2) * np.cos(phi_2dc/2) + d_beta_2 * np.cos(phi_2) * np.sin(phi_2dc/2)

    U_dp3 = xi_13 * (phi_3 - phi_3x) + mu_13 * xi_13 * (phi_1 + phi_1bx) - beta_3 * np.sin(phi_3) * np.cos(phi_3dc/2) + d_beta_3 * np.cos(phi_3) * np.sin(phi_3dc/2)

    U_dp1dc = gamma_1 * (phi_1dc - phi_1xdc) - 1/2 * beta_1 * np.cos(phi_1) * np.sin(phi_1dc / 2) - 1/2 * d_beta_1 * np.sin(phi_1) * np.cos(phi_1dc/2)

    U_dp2dc = gamma_2 * (phi_2dc - phi_2xdc) - 1/2 * beta_2 * np.cos(phi_2) * np.sin(phi_2dc / 2) - 1/2 * d_beta_2 * np.sin(phi_2) * np.cos(phi_2dc/2)

    U_dp3dc = gamma_3 * (phi_3dc - phi_3xdc) - 1/2 * beta_3 * np.cos(phi_3) * np.sin(phi_3dc / 2) - 1/2 * d_beta_3 * np.sin(phi_3) * np.cos(phi_3dc/2)

    return -1 *  np.array([U_dp1, U_dp2, U_dp3, U_dp1dc, U_dp2dc, U_dp3dc])
