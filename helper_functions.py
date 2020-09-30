import numpy as np
import colour as clr
from colormath.color_objects import sRGBColor
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

def select_data(Wavelengths, Theta_I, Phi_I, Polarization, Data):
    u_wls = np.array(Data['Wavelengths'])
    u_theta_Is = np.array(Data['thetaIs'])
    u_phi_Is = np.array(Data['phiIs'])
    u_pols = np.array(Data['Polarization'])
    selected_data = np.array(Data['data'])[u_pols == Polarization, u_theta_Is == Theta_I, u_phi_Is == Phi_I, u_wls == Wavelengths, :, :]
    return selected_data[0]

def select_spectrum(Theta_V, Phi_V, Theta_I, Phi_I, Polarization, Data):
    u_theta_Vs = np.array(Data['thetaVs'])
    u_phi_Vs = np.array(Data['phiVs'])
    u_theta_Is = np.array(Data['thetaIs'])
    u_phi_Is = np.array(Data['phiIs'])
    u_pols = np.array(Data['Polarization'])
    selected_spectrum = np.array(Data['data'])[u_pols == Polarization, u_theta_Is == Theta_I, u_phi_Is == Phi_I, :, u_theta_Vs == Theta_V, u_phi_Vs == Phi_V]
    # selected_spectrum = selected_spectrum/np.max(selected_spectrum)
    return selected_spectrum

def get_tristimulus_XYZs(Theta_I, Phi_I, Polarization, Data, observer, illuminant):
    u_wls = np.array(Data['Wavelengths'])
    u_theta_Is = np.array(Data['thetaIs'])
    u_phi_Is = np.array(Data['phiIs'])
    u_pols = np.array(Data['Polarization'])
    u_theta_Vs = np.array(Data['thetaVs'])
    u_phi_Vs = np.array(Data['phiVs'])
    data = np.array(Data['data'])

    cmfs = clr.STANDARD_OBSERVERS_CMFS[observer]
    illuminant = clr.ILLUMINANTS_SDS[illuminant]
    tristimulus_XYZ_values = []
    color_values = []
    for theta_V in u_theta_Vs:
        tristimulus_XYZ_row = []
        color_values_row = []
        for phi_V in u_phi_Vs:
            spectrum = data[u_pols == Polarization, u_theta_Is == Theta_I, u_phi_Is == Phi_I, :,u_theta_Vs == theta_V, u_phi_Vs == phi_V]
            # spectrum = spectrum[0]/np.max(spectrum)
            spectrum = np.array([u_wls,spectrum[0]]).T
            spectrum = spectrum.tolist()
            spectrum = {line[0] : line[1] for line in spectrum}
            sd = clr.SpectralDistribution(spectrum)
            sd = sd.interpolate(clr.SpectralShape(380, 830, 1))
            # print(sd)
            XYZ = clr.sd_to_XYZ(sd,cmfs,illuminant)
            sRGB = clr.XYZ_to_sRGB(XYZ/100)
            sRGB = sRGBColor(sRGB[0],sRGB[1],sRGB[2])
            RGB = list(sRGB.get_upscaled_value_tuple())
            for i in range(len(RGB)):
                if RGB[i] < 0:
                    RGB[i] = 0
                elif RGB[i] > 255:
                    RGB[i] = 255
            tristimulus_XYZ_row.append(XYZ)
            color_values_row.append(RGB)
        tristimulus_XYZ_values.append(tristimulus_XYZ_row)
        color_values.append(color_values_row)
    return tristimulus_XYZ_values, color_values

def update_menu_block(filename, file_selection_options, opt_wl, opt_pols, opt_theta_Is, opt_theta_PhiIs,  opt_theta_Vs, opt_theta_PhiVs, \
                      sel_wl, sel_pol, sel_thetaI, sel_phiI, sel_thetaV, sel_phiV, sel_observer, sel_illuminant, \
                      is_visible, is_reference):
    children = [
        html.Div([html.Div(dcc.Dropdown(id="File-selector", placeholder="File name", clearable=False, options=file_selection_options, value=filename), id='File-selector-1',
                           style={'display': 'inline-block', 'width': '100%','vertical-align' : 'middle', 'text-align' : 'center'})],
                 style={'display': 'inline-block', 'width': '75.0%', 'margin-bottom':'0.15%', 'margin-top':'0.15%'}),

        html.Div(dcc.Checklist(id='is-visible', options=[{'label': 'Visible', 'value': 1}], value=is_visible),
                 style={'display': 'inline-block', 'width': '12.5%', 'vertical-align': 'middle',
                        'text-align': 'center', 'margin-bottom':'0.15%', 'margin-top':'0.15%'}),
        html.Div(dcc.Checklist(id="is-reference", options=[{'label': 'Reference', 'value': 1}], value=is_reference),
                 style={'display': 'inline-block', 'width': '12.5%', 'vertical-align': 'middle',
                        'text-align': 'center', 'margin-bottom':'0.15%', 'margin-top':'0.15%'}),

        html.Div(dcc.Dropdown(id="Wavelength", placeholder="Wavelength", clearable=False, options=opt_wl, value=sel_wl),
                 style={'display': 'inline-block', 'width': '10.457%','vertical-align' : 'middle',
                        'margin-bottom':'0.15%', 'margin-top':'0.15%', 'margin-right':'0.15%'}),
        html.Div(dcc.Dropdown(id="Polarization", placeholder="Polarization", clearable=False, options=opt_pols, value=sel_pol),
                 style={'display': 'inline-block', 'width': '10.457%', 'vertical-align': 'middle',
                        'margin-bottom':'0.15%', 'margin-top':'0.15%', 'margin-left':'0.15%', 'margin-right':'0.15%'}),
        html.Div(dcc.Dropdown(id="ThetaI", placeholder="Incidence zenith angle", clearable=False, options=opt_theta_Is, value=sel_thetaI),
                 style={'display': 'inline-block', 'width': '10.457%', 'vertical-align' : 'middle',
                        'margin-bottom':'0.15%', 'margin-top':'0.15%', 'margin-left':'0.15%', 'margin-right':'0.15%'}),
        html.Div(dcc.Dropdown(id="PhiI", placeholder="Incidence azimuthal angle", clearable=False, options=opt_theta_PhiIs, value=sel_phiI),
                 style={'display': 'inline-block', 'width': '10.457%', 'vertical-align' : 'middle',
                        'margin-bottom':'0.15%', 'margin-top':'0.15%', 'margin-left':'0.15%', 'margin-right':'0.15%'}),
        html.Div(dcc.Dropdown(id="ThetaV", placeholder="Viewing zenith angle", clearable=False, options=opt_theta_Vs, value=sel_thetaV),
                 style={'display': 'inline-block', 'width': '10.457%', 'vertical-align': 'middle',
                        'margin-bottom':'0.15%', 'margin-top':'0.15%', 'margin-left':'0.15%', 'margin-right':'0.15%'}),
        html.Div(dcc.Dropdown(id="PhiV", placeholder="Viewing azimuthal angle", clearable=False, options=opt_theta_PhiVs, value=sel_phiV),
                 style={'display': 'inline-block', 'width': '10.457%', 'vertical-align': 'middle',
                        'margin-bottom':'0.15%', 'margin-top':'0.15%', 'margin-left':'0.15%', 'margin-right':'0.15%'}),
        html.Div(dcc.Dropdown(id="Illuminant", placeholder="Illuminant", clearable=False, options=[{'label': value, 'value': value} for value in clr.ILLUMINANTS_SDS], value=sel_illuminant),
                 style={'display': 'inline-block', 'width': '10.457%', 'vertical-align': 'middle',
                        'margin-bottom':'0.15%', 'margin-top':'0.15%', 'margin-left':'0.15%', 'margin-right':'0.15%'}),
        html.Div(dcc.Dropdown(id="Observer", placeholder="Observer", clearable=False, options=[{'label':value,'value':value} for value in clr.STANDARD_OBSERVERS_CMFS], value=sel_observer),
                 style={'display': 'inline-block', 'width': '24.7%', 'vertical-align' : 'middle',
                        'margin-bottom':'0.15%', 'margin-top':'0.15%', 'margin-left':'0.15%'}),
        dbc.Tooltip("Wavelength", target="Wavelength"),
        dbc.Tooltip("Polarization", target="Polarization"),
        dbc.Tooltip("Incidence zenith angle", target="ThetaI"),
        dbc.Tooltip("Incidence azimuthal angle", target="PhiI"),
        dbc.Tooltip("Viewing zenith angle", target="ThetaV"),
        dbc.Tooltip("Viewing azimuthal angle", target="PhiV"),
        dbc.Tooltip("Illuminant", target="Illuminant"),
        dbc.Tooltip("Observer", target="Observer"),
        dbc.Tooltip("Select file", target="File-selector"),
        dbc.Tooltip("Make data visible alongside other data", target="is-visible"),
        dbc.Tooltip("Chose this file as reference", target="is-reference")
    ]
    return children
