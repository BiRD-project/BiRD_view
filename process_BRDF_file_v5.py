import json
import numpy as np
import colour as clr

def process_BRDF_json_new(dict_from_json):
    data = dict_from_json
    wls = np.array(data['data']['wavelengths'])
    bulk_data = np.array(data['data']['data'])

    theta_Vs = np.array(data['data']['theta_v'])
    phi_Vs = np.array(data['data']['phi_v'])
    theta_Is = np.array(data['data']['theta_i'])
    phi_Is = np.array(data['data']['phi_i'])
    pols = np.array(list(data['data']['pol']))

    # print(theta_Vs.size)
    # print(phi_Vs.size)
    # print(theta_Is.size)
    # print(phi_Is.size)
    # print(pols.size)

    u_wls = np.unique(wls)
    u_theta_Vs = np.unique(theta_Vs)
    u_phi_Vs = np.unique(phi_Vs)
    u_theta_Is = np.unique(theta_Is)
    u_phi_Is = np.unique(phi_Is)
    u_pols = np.unique(pols)

    arranged_data = np.full((u_pols.size, u_theta_Is.size, u_phi_Is.size, u_wls.size, u_theta_Vs.size, u_phi_Vs.size), -0.000001)
    # print(arranged_data.shape)

    for i in range(u_wls.size):
        for j in range(pols.size):
            pol_i = np.where(u_pols == pols[j])
            theta_i_i = np.where(u_theta_Is == theta_Is[j])
            phi_i_i = np.where(u_phi_Is == phi_Is[j])
            wl_i = np.where(u_wls == wls[i])
            theta_v_i = np.where(u_theta_Vs == theta_Vs[j])
            phi_v_i = np.where(u_phi_Vs == phi_Vs[j])

            arranged_data[pol_i[0], theta_i_i[0], phi_i_i[0], wl_i[0], theta_v_i[0], phi_v_i[0]] = bulk_data[i, j]
            # print(arranged_data[pol_i[0], theta_i_i[0], phi_i_i[0], wl_i[0], theta_v_i[0], phi_v_i[0]])

    # print(arranged_data)

    if u_pols.shape[0] > 1:
        arranged_data = np.append(arranged_data, [np.mean(arranged_data, axis=0)], axis=0)
        u_pols = np.append(u_pols, 'average')

    processed_data = {'Wavelengths':u_wls, 'thetaIs':u_theta_Is, 'phiIs':u_phi_Is, 'thetaVs':u_theta_Vs, 'phiVs':u_phi_Vs, 'Polarization':u_pols, 'data':arranged_data}

    return processed_data

# f = open('DataTest.json', 'r')
#
# data = json.load(f)
#
# test = process_BRDF_json_new(data)
#
# print(test['thetaVs'])
# print(test['data'][0,0,0,0,2,:])


