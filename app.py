import base64
import json
import dash_gif_component as gif
import colour as clr
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from process_BRDF_file_v5 import process_BRDF_json_new
from helper_functions import *
import colour as clr
import plotly.graph_objects as go
from help_text import *
import time


#App configurations
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
#external_stylesheets = [dbc.themes.SIMPLEX]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.config['suppress_callback_exceptions'] = True
colors = {'background': '#111111', 'text': '#000080'}

def server_layout():
    layout = html.Div([
        dcc.Store(id='files_uploaded_trigger', storage_type='memory', data='Triggered'),
        dcc.Store(id='Menu_tabs_trigger', storage_type='memory', data='Triggered'),
        dcc.Store(id='App_mode_tabs_trigger', storage_type='memory', data='Triggered'),
        dcc.Store(id='App_mode_tab_value', storage_type='memory', data='BRDF'),
        dcc.Store(id='BRDF_mode_tab_update_trigger', storage_type='memory', data='Triggered'),
        html.Div(id='browser_data_storage_2', children=dcc.Store(id='browser_data_storage_1',storage_type='memory',data={}), style={'display': None}),
        dcc.Store(id='selected_file', storage_type='memory', data=''),
        dcc.Store(id='previous_state',storage_type='memory', data=[]),
        dcc.Store(id='trigger', storage_type='memory', data='Triggered'),
        dcc.Store(id='3D_plot_previous_state', storage_type='memory', data=[]),
        dcc.Store(id='3D_trigger', storage_type='memory', data='Triggered'),
        dcc.Store(id='Projection_plot_previous_state', storage_type='memory', data=[]),
        dcc.Store(id='Projection_trigger_check', storage_type='memory', data='Triggered'),
        dcc.Store(id='Projection_trigger', storage_type='memory', data='Triggered'),
        dcc.Store(id='Projection_bezal_turned', storage_type='memory', data=1),
        dcc.Store(id='Projection_bezal_previous_state', storage_type='memory', data=1),
        dcc.Store(id='2D_brdf_plot_previous_state', storage_type='memory', data=[]),
        dcc.Store(id='2D_trigger', storage_type='memory', data='Triggered'),
        dcc.Store(id='2D_BRDF_plot_clicked', storage_type='memory', data=1),
        dcc.Store(id='Pspec_previous_state', storage_type='memory', data=[]),
        dcc.Store(id='Pspec_trigger', storage_type='memory', data='Triggered'),
        dcc.Store(id='tristimulus_XYZ_values',storage_type='memory'),
        dcc.Store(id='RGB_values',storage_type='memory'),
        #html.Div(id='browser_data_storage', style={'display': 'none'}),

        html.H1(children='BiRD view v3.0',
                style={'textAlign': 'center', 'color': colors['text'], 'width': '100%', 'height': '25px', 'line-height':'50px'}),
        html.Div(children='''A web application for BRDF data visualization.''',
                 style={'textAlign': 'center', 'color': colors['text'], 'width': '100%', 'height': '25px', 'line-height':'50px'}),
        html.Hr(style={'margin-bottom':'1px'}),

        dcc.Tabs(id="menu-tabs", value='Help', children=[
            dcc.Tab(id="applet-tab", label='Applet', value='Applet',
                    style={'line-height': '50px', 'padding': '0', 'height': '50px'},
                    selected_style={'line-height': '50px', 'padding': '0', 'height': '50px'}
                    ),
            dcc.Tab(id="help-tab", label='Help', value='Help',
                    style={'line-height': '50px', 'padding': '0', 'height': '50px'},
                    selected_style={'line-height': '50px', 'padding': '0', 'height': '50px'})],
                 style={'width': '100%', 'height': '50px', 'line-height': '50px', 'textAlign': 'top', 'margin-bottom': '0.15%', 'margin-top': '0.15%'}),
        html.Div(id='menu-tabs-content')
    ])
    return layout

@app.callback([Output('menu-tabs-content', 'children'),
               Output('Menu_tabs_trigger', 'data')],
              [Input('menu-tabs', 'value')])
def render_menu_tabs_content(tab):
    if tab == 'Applet':
        return html.Div(
            children=[
                    html.Div(children=[
                        dcc.Loading(id='loading', children=[
                            dcc.Upload(id='upload-data', children=html.Div(id='loading_state', children=['Drag and Drop or ', html.A('Select Files')]),
                                       style={'width': '100%', 'height': '50px', 'lineHeight': '50px',
                                              'borderWidth': '1px', 'borderStyle': 'dashed', 'borderRadius': '10px',
                                              'textAlign': 'center', 'margin-bottom':'0.15%', 'margin-top':'0.15%'},
                                       multiple=True)
                        ], type='default', style={'width': '100%', 'height': '50', 'lineHeight': '50px',
                                                  'borderWidth': '1px', 'borderStyle': 'dashed', 'borderRadius': '1px',
                                                  'textAlign': 'center','margin-bottom':'0.15%', 'margin-top':'0.15%'})
                    ], className="row", id='upload-file'),

                    html.Div(id='menu_block', children=[
                        html.Div([
                            html.Div(
                                dcc.Dropdown(id="File-selector", placeholder="File name", clearable=False), id='File-selector-1',
                                style={'display': 'inline-block', 'width': '100%','vertical-align' : 'middle', 'text-align' : 'center'})],
                            style={'display': 'inline-block', 'width': '75.0%', 'margin-bottom':'0.15%', 'margin-top':'0.15%'}),

                        html.Div(dcc.Checklist(id='is-visible', options=[{'label': 'Visible', 'value': 1}]),
                                 style={'display': 'inline-block', 'width': '12.5%', 'vertical-align': 'middle',
                                        'text-align': 'center', 'margin-bottom':'0.15%', 'margin-top':'0.15%'}),
                        html.Div(dcc.Checklist(id="is-reference", options=[{'label': 'Reference', 'value': 1}]),
                                 style={'display': 'inline-block', 'width': '12.5%', 'vertical-align': 'middle',
                                        'text-align': 'center', 'margin-bottom':'0.15%', 'margin-top':'0.15%'}),

                        html.Div(dcc.Dropdown(id="Wavelength", placeholder="Wavelength", clearable=False),
                                 style={'display': 'inline-block', 'width': '10.457%','vertical-align' : 'middle',
                                        'margin-bottom':'0.15%', 'margin-top':'0.15%', 'margin-right':'0.15%'}),
                        html.Div(dcc.Dropdown(id="Polarization", placeholder="Polarization", clearable=False),
                                 style={'display': 'inline-block', 'width': '10.457%', 'vertical-align': 'middle',
                                        'margin-bottom':'0.15%', 'margin-top':'0.15%', 'margin-left':'0.15%', 'margin-right':'0.15%'}),
                        html.Div(dcc.Dropdown(id="ThetaI", placeholder="Incidence zenith angle", clearable=False),
                                 style={'display': 'inline-block', 'width': '10.457%', 'vertical-align' : 'middle',
                                        'margin-bottom':'0.15%', 'margin-top':'0.15%', 'margin-left':'0.15%', 'margin-right':'0.15%'}),
                        html.Div(dcc.Dropdown(id="PhiI", placeholder="Incidence azimuthal angle", clearable=False),
                                 style={'display': 'inline-block', 'width': '10.457%', 'vertical-align' : 'middle',
                                        'margin-bottom':'0.15%', 'margin-top':'0.15%', 'margin-left':'0.15%', 'margin-right':'0.15%'}),
                        html.Div(dcc.Dropdown(id="ThetaV", placeholder="Viewing zenith angle", clearable=False),
                                 style={'display': 'inline-block', 'width': '10.457%', 'vertical-align': 'middle',
                                        'margin-bottom':'0.15%', 'margin-top':'0.15%', 'margin-left':'0.15%', 'margin-right':'0.15%'}),
                        html.Div(dcc.Dropdown(id="PhiV", placeholder="Viewing azimuthal angle", clearable=False),
                                 style={'display': 'inline-block', 'width': '10.457%', 'vertical-align': 'middle',
                                        'margin-bottom':'0.15%', 'margin-top':'0.15%', 'margin-left':'0.15%', 'margin-right':'0.15%'}),
                        html.Div(dcc.Dropdown(id="Illuminant", placeholder="Illuminant", clearable=False, options=[{'label': value, 'value': value} for value in clr.ILLUMINANTS_SDS]),
                                 style={'display': 'inline-block', 'width': '10.457%', 'vertical-align': 'middle',
                                        'margin-bottom':'0.15%', 'margin-top':'0.15%', 'margin-left':'0.15%', 'margin-right':'0.15%'}),
                        html.Div(dcc.Dropdown(id="Observer", placeholder="Observer", clearable=False, options=[{'label':value,'value':value} for value in clr.STANDARD_OBSERVERS_CMFS]),
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
                    ]),


                    dcc.Tabs(id="applet-modes", value= None, children=[
                        dcc.Tab(id="applet-BRDF", label='BRDF visualisation', value='BRDF',
                                style={'line-height': '50px', 'padding': '0', 'height': '50px'},
                                selected_style={'line-height': '50px', 'padding': '0', 'height': '50px'}),
                        dcc.Tab(id="applet-COLOR", label='CIELAB', value='CIELAB',
                                style={'line-height': '50px', 'padding': '0', 'height': '50px'},
                                selected_style={'line-height': '50px', 'padding': '0', 'height': '50px'})],
                             style={'width': '100%', 'height': '50px', 'line-height': '50px', 'textAlign': 'top', 'margin-bottom': '0.15%', 'margin-top': '0.15%'}),
                    html.Div(id='applet-modes-content')
                ]
        ), 'Triggered'
    elif tab == 'Help':
        return html.Div(
            children=[html.Div(children=dcc.Markdown(help_text_markdown_part_1,
                                                    style={'width': '70%'})),
                      html.Div([gif.GifPlayer(
                          gif='assets/upload.gif',
                          still='assets/upload.png')],
                      style={'width': '70%'}),
                      html.Div(children=dcc.Markdown(help_text_markdown_part_2,
                                                     style={'width': '70%'})),
                      html.Div([gif.GifPlayer(
                          gif='assets/fileselect.gif',
                          still='assets/fileselect.png')],
                          style={'width': '70%'}),
                      html.Div(children=dcc.Markdown(help_text_markdown_part_3,
                                                     style={'width': '70%'})),
                      html.Div([gif.GifPlayer(
                          gif='assets/navparams.gif',
                          still='assets/navparams.png')],
                          style={'width': '70%'}),
                      html.Div(children=dcc.Markdown(help_text_markdown_part_4,
                                                     style={'width': '70%'})),
                      html.Div([gif.GifPlayer(
                          gif='assets/paramstips.gif',
                          still='assets/paramstips.png')],
                          style={'width': '70%'}),
                      html.Div(children=dcc.Markdown(help_text_markdown_part_5,
                                                     style={'width': '70%'})),
                      html.Div([gif.GifPlayer(
                          gif='assets/3Dplot.gif',
                          still='assets/3Dplot.png')],
                          style={'width': '70%'}),
                      html.Div(children=dcc.Markdown(help_text_markdown_part_6,
                                                     style={'width': '70%'})),
                      html.Div([gif.GifPlayer(
                          gif='assets/3Dprojection.gif',
                          still='assets/3Dprojection.png')],
                          style={'width': '70%'}),
                      html.Div(children=dcc.Markdown(help_text_markdown_part_7,
                                                     style={'width': '70%'})),
                      html.Div([gif.GifPlayer(
                          gif='assets/2Dplot.gif',
                          still='assets/2Dplot.png')],
                          style={'width': '70%'}),
                      html.Div(children=dcc.Markdown(help_text_markdown_part_8,
                                                     style={'width': '70%'})),
                      html.Div([gif.GifPlayer(
                          gif='assets/multiData.gif',
                          still='assets/multiData.png')],
                          style={'width': '70%'}),
                      html.Div(children=dcc.Markdown(help_text_markdown_part_9,
                                                     style={'width': '70%'})),
                      html.Div([gif.GifPlayer(
                          gif='assets/interaction.gif',
                          still='assets/interaction.png')],
                          style={'width': '70%'}),
                      ]
        ), 'Triggered'

@app.callback(Output('applet-modes', 'value'),
              [Input('Menu_tabs_trigger', 'data')],
              [State('App_mode_tab_value', 'data')])
def trigger_menu_tab_population(trigger, tab):
    # print(tab)
    return tab

@app.callback([Output('applet-modes-content', 'children'),
               Output('App_mode_tab_value', 'data'),
               Output('App_mode_tabs_trigger', 'data')],
              [Input('applet-modes', 'value')])
def render_applet_modes_content(tab):
    if tab is None:
        raise PreventUpdate
    if tab == 'BRDF':
        return html.Div(
            children=[
                html.Div(children=[
                    html.Div(dcc.Loading(id='3D-plot-L',
                                         children=dcc.Graph(id="3D-plot", responsive=True),
                                         style={'height': '420px', 'line-height': '420px'}),
                             style={'width': '50%', 'height': '420px', 'order': '1'}),
                    html.Div(dcc.Loading(id='Point-spectrum-L',
                                         children=dcc.Graph(id="Point-spectrum", responsive=True),
                                         style={'height': '420px', 'line-height': '420px'}),
                             style={'width': '50%', 'height': '420px', 'order': '2'}),
                    html.Div(dcc.Loading(id='Projection-plot-L',
                                         children=dcc.Graph(id="Projection-plot", responsive=True),
                                         style={'height': '420px', 'line-height': '420px'}),
                             style={'width': '50%', 'height': '420px', 'order': '3'}),
                    html.Div(dcc.Loading(id='2D-BRDF-L',
                                         children=dcc.Graph(id="2D-BRDF", responsive=True),
                                         style={'height': '420px', 'line-height': '420px'}),
                             style={'width': '50%', 'height': '420px', 'order': '4'})],
                    style={'display': 'flex', 'flex-wrap': 'wrap'})]
        ), tab, 'Triggered'
    elif tab == 'CIELAB':
        return html.Div(
            children=[
                html.Div(children=[
                    html.Div(dcc.Loading(id='CIELAB-3D-plot-L',
                                         children=dcc.Graph(id="CIELAB-3D-plot", responsive=True),
                                         style={'height': '420px', 'line-height': '420px'}),
                             style={'width': '50%', 'height': '420px', 'order': '1'}),
                    html.Div(dcc.Loading(id='CIELAB-Point-spectrum-L',
                                         children=dcc.Graph(id="CIELAB-Point-spectrum", responsive=True),
                                         style={'height': '420px', 'line-height': '420px'}),
                             style={'width': '50%', 'height': '420px', 'order': '2'}),
                    html.Div(dcc.Loading(id='CIELAB-Projection-plot-L',
                                         children=dcc.Graph(id="CIELAB-Projection-plot", responsive=True),
                                         style={'height': '420px', 'line-height': '420px'}),
                             style={'width': '50%', 'height': '420px', 'order': '3'}),
                    html.Div(dcc.Loading(id='CIELAB-2D-BRDF-L',
                                         children=dcc.Graph(id="CIELAB-2D-BRDF", responsive=True),
                                         style={'height': '420px', 'line-height': '420px'}),
                             style={'width': '50%', 'height': '420px', 'order': '4'})],
                    style={'display': 'flex', 'flex-wrap': 'wrap'})]
        ), tab, 'Triggered'

@app.callback(Output('BRDF_mode_tab_update_trigger', 'data'),
              [Input('App_mode_tabs_trigger', 'data')],
              [State('App_mode_tab_value', 'data')])
def trigger_mode_tab_population(trigger, tab):
    # print(tab)
    if tab != 'BRDF':
        raise PreventUpdate
    return 'Triggered'

@app.callback([Output('browser_data_storage_1','data'),
               Output('File-selector', 'options'),
               Output('File-selector', 'value'),
               Output('loading_state', 'children'),
               Output('files_uploaded_trigger', 'data')],
              [Input('upload-data', 'filename'),
               Input('upload-data', 'contents'),
               Input('upload-data', 'children')],
              [State('browser_data_storage_1','data'),
               State('File-selector','options'),
               State('File-selector','value')])
def upload_data(filenames, contents, value, data, options, selected_file):

    if contents is None or filenames is None:
        raise PreventUpdate

    if options is None:
        new_options = []
        for i in range(len(filenames)):
            filename = filenames[i]
            content = contents[i]
            content_type, content_string = content.split(',')
            decoded = base64.b64decode(content_string)
            processed_data = process_BRDF_json_new(json.loads(decoded.decode('utf-8')))
            data[filename] = {'measurement_data': processed_data,
                              'selected_states':
                                  {'wavelength': processed_data['Wavelengths'][0],
                                   'polarization': processed_data['Polarization'][0],
                                   'theta_I': processed_data['thetaIs'][0],
                                   'phi_I': processed_data['phiIs'][0],
                                   'theta_V': processed_data['thetaVs'][0],
                                   'phi_V': processed_data['phiVs'][0],
                                   'observer': 'CIE 1931 2 Degree Standard Observer',
                                   'illuminant': 'D65',
                                   'visible': [],
                                   'reference': []}}
            if i == 0:
                data[filename]['selected_states']['visible'] = []
                data[filename]['selected_states']['reference'] = [1]
                selected_file = filename
            new_options.append({'label': filename, 'value': filename})
        options = new_options
    else:
        for i in range(len(filenames)):
            filename = filenames[i]
            content = contents[i]
            content_type, content_string = content.split(',')
            decoded = base64.b64decode(content_string)
            processed_data = process_BRDF_json_new(json.loads(decoded.decode('utf-8')))
            if filename in data:
                i = 1
                new_filename = filename
                while new_filename in data:
                    new_filename = filename + '_copy_' + str(i)
                    i = i + 1
                filename = new_filename
            data[filename] = {'measurement_data': processed_data,
                              'selected_states':
                                  {'wavelength': processed_data['Wavelengths'][0],
                                   'polarization': processed_data['Polarization'][0],
                                   'theta_I': processed_data['thetaIs'][0],
                                   'phi_I': processed_data['phiIs'][0],
                                   'theta_V': processed_data['thetaVs'][0],
                                   'phi_V': processed_data['phiVs'][0],
                                   'observer': 'CIE 1931 2 Degree Standard Observer',
                                   'illuminant': 'D65',
                                   'visible': [],
                                   'reference': []}}
            options.append({'label':filename, 'value': filename})
    print('upload')
    return data, options, selected_file, value, 'Triggered'

@app.callback([Output('selected_file','data'),
               Output('menu_block','children')],
              [Input('File-selector', 'value'),
               Input('Menu_tabs_trigger', 'data'),
               # Input('Menu_tabs_trigger','data'),
               # Input('App_mode_tabs_trigger','data')
               ],
              [State('browser_data_storage_1', 'data'),
               State('selected_file', 'data')])
def update_menu(filename, menu_tabs_trigger, uploaded_data, previously_selected_file):

    if uploaded_data == {}:
        raise PreventUpdate
    if filename == previously_selected_file:
        raise PreventUpdate
    if filename is None:
        filename = previously_selected_file

    opt_wl = [{'label':value,'value':value} for value in uploaded_data[filename]['measurement_data']['Wavelengths']]
    opt_pols = [{'label': value, 'value': value} for value in uploaded_data[filename]['measurement_data']['Polarization']]
    opt_theta_Is = [{'label':value,'value':value} for value in uploaded_data[filename]['measurement_data']['thetaIs']]
    opt_theta_PhiIs = [{'label':value,'value':value} for value in uploaded_data[filename]['measurement_data']['phiIs']]
    opt_theta_Vs = [{'label':value,'value':value} for value in uploaded_data[filename]['measurement_data']['thetaVs']]
    opt_theta_PhiVs = [{'label': value, 'value': value} for value in uploaded_data[filename]['measurement_data']['phiVs']]
    sel_wl = uploaded_data[filename]['selected_states']['wavelength']
    sel_pol = uploaded_data[filename]['selected_states']['polarization']
    sel_thetaI = uploaded_data[filename]['selected_states']['theta_I']
    sel_phiI = uploaded_data[filename]['selected_states']['phi_I']
    sel_thetaV = uploaded_data[filename]['selected_states']['theta_V']
    sel_phiV = uploaded_data[filename]['selected_states']['phi_V']
    sel_observer = uploaded_data[filename]['selected_states']['observer']
    sel_illuminant = uploaded_data[filename]['selected_states']['illuminant']
    is_visible = uploaded_data[filename]['selected_states']['visible']
    is_reference = uploaded_data[filename]['selected_states']['reference']

    file_selection_options = []
    for key in uploaded_data:
        file_selection_options.append({'label': key, 'value': key})

    children = update_menu_block(filename, file_selection_options, opt_wl, opt_pols, opt_theta_Is, opt_theta_PhiIs,  opt_theta_Vs, opt_theta_PhiVs, \
           sel_wl, sel_pol, sel_thetaI, sel_phiI, sel_thetaV, sel_phiV, sel_observer, sel_illuminant, \
           is_visible, is_reference)

    return filename, children

@app.callback([Output('previous_state', 'data'),
               Output('browser_data_storage_2','children'),
               Output('trigger', 'data')],
              [Input('Wavelength', 'value'),
               Input('Polarization', 'value'),
               Input('ThetaI', 'value'),
               Input('PhiI', 'value'),
               Input('ThetaV', 'value'),
               Input('PhiV', 'value'),
               Input('Observer', 'value'),
               Input('Illuminant', 'value'),
               Input('is-visible', 'value'),
               Input('is-reference', 'value')],
              [State('browser_data_storage_1', 'data'),
               State('File-selector', 'value'),
               State('previous_state', 'data')])
def modify_state(sel_wl, sel_pol, sel_thetaI, sel_phiI, sel_thetaV, sel_phiV, sel_observer, sel_illuminant, is_visible, is_reference, uploaded_data, filename, previous_state):
    if filename is None or uploaded_data == {}:
        raise PreventUpdate

    new_state = [filename, sel_wl, sel_pol, sel_thetaI, sel_phiI, sel_thetaV, sel_phiV, sel_observer, sel_illuminant, is_visible, is_reference]

    if new_state == previous_state:
        raise PreventUpdate
    else:
        uploaded_data[filename]['selected_states']['wavelength'] = sel_wl
        uploaded_data[filename]['selected_states']['polarization'] = sel_pol
        uploaded_data[filename]['selected_states']['theta_I'] = sel_thetaI
        uploaded_data[filename]['selected_states']['phi_I'] = sel_phiI
        uploaded_data[filename]['selected_states']['theta_V'] = sel_thetaV
        uploaded_data[filename]['selected_states']['phi_V'] = sel_phiV
        uploaded_data[filename]['selected_states']['observer'] = sel_observer
        uploaded_data[filename]['selected_states']['illuminant'] = sel_illuminant
        uploaded_data[filename]['selected_states']['visible'] = is_visible
        if is_reference is None:
            is_reference = []
        elif not is_reference:
            is_reference = []
        elif is_reference[0] == 1:
            for file in uploaded_data:
                uploaded_data[file]['selected_states']['reference'] = []
        uploaded_data[filename]['selected_states']['reference'] = is_reference
        previous_state = new_state

    # print('fired')
    return previous_state, dcc.Store(id='browser_data_storage_1', storage_type='memory', data=uploaded_data), 'triggered'

@app.callback([Output('3D_plot_previous_state', 'data'),
               Output('3D_trigger', 'data')],
              [Input('trigger', 'data')],
              [State('3D_plot_previous_state', 'data'),
               State('previous_state', 'data'),
               State('File-selector', 'value')])
def trigger_3D_plot(trigger, plot_previous_state, previous_state, filename):
    if filename == None:
        raise PreventUpdate

    new_state = previous_state[0:5]
    if new_state == plot_previous_state:
        raise PreventUpdate
    else:
        plot_previous_state = new_state
    return plot_previous_state, 'Triggered'

@app.callback(Output('3D-plot','figure'),
              [Input('3D_trigger', 'data'),
               Input('BRDF_mode_tab_update_trigger', 'data')],
              [State('browser_data_storage_1','data'),
               State('selected_file', 'data')])
def update_3D_plot(trigger1, trigger2, uploaded_data, filename):
    if trigger1 is None or uploaded_data == {} or filename == '':
        raise PreventUpdate
    # print(time.process_time())
    theta = np.array(uploaded_data[filename]['measurement_data']['thetaVs'])[np.newaxis]
    phi = np.array(uploaded_data[filename]['measurement_data']['phiVs'])[np.newaxis]
    wl = uploaded_data[filename]['selected_states']['wavelength']
    thI = uploaded_data[filename]['selected_states']['theta_I']
    phiI = uploaded_data[filename]['selected_states']['phi_I']
    pol = uploaded_data[filename]['selected_states']['polarization']
    # observer = uploaded_data[filename]['selected_states']['observer']
    # illuminant = uploaded_data[filename]['selected_states']['illuminant']
    data = uploaded_data[filename]['measurement_data']
    # print(time.process_time())
    figure = []
    #tristimulus_values, RGB_values = get_tristimulus_XYZs(thI, phiI, pol, data, observer, illuminant)
    #RGB_values = np.array(RGB_values).reshape((theta.shape[1]*phi.shape[1]),3)

    X = theta.T*np.cos(np.radians(phi))
    Y = theta.T*np.sin(np.radians(phi))
    Z = select_data(wl, thI, phiI, pol, data)
    # print(time.process_time())
    X_sc = np.transpose(X).reshape((theta.shape[1]*phi.shape[1]))
    Y_sc = np.transpose(Y).reshape((theta.shape[1]*phi.shape[1]))
    Z_sc = np.transpose(Z).reshape((theta.shape[1]*phi.shape[1]))

    label_data = []
    for i in range(phi.shape[1]):
        for j in range(theta.shape[1]):
            label_data.append(
                'BRDF value: {:.4f}, Theta: {:.2f}, Phi: {:.2f}'.format(Z[j, i], theta[0, j], phi[0, i]))

    label_data = np.array(label_data)
    label_data = label_data.reshape((theta.shape[1] * phi.shape[1]))
    label_data = label_data[Z_sc >= 0]

    X_sc = X_sc[Z_sc>=0]
    Y_sc = Y_sc[Z_sc>=0]
    Z_sc = Z_sc[Z_sc>=0]

    zmin = np.min(Z_sc)
    zmax = np.max(Z_sc)
    theta_span = 30+np.max(np.abs(theta[0]))
    offset = 0.1*zmin
    if zmax-zmin != 0:
        if zmin-(zmax-zmin)/5 < 0:
            offset = zmin
        else:
            (zmax - zmin) / 5
    # print(time.process_time())
    x_scale =[]
    y_scale = []
    x_scale.append(0)
    y_scale.append(0)
    x_scale.append(theta_span * np.cos(np.radians(0)))
    y_scale.append(theta_span * np.sin(np.radians(0)))
    x_scale.append(-theta_span * np.cos(np.radians(0)))
    y_scale.append(-theta_span * np.sin(np.radians(0)))
    x_scale.append(0)
    y_scale.append(0)
    x_scale.append(theta_span * np.cos(np.radians(90)))
    y_scale.append(theta_span * np.sin(np.radians(90)))
    x_scale.append(-theta_span * np.cos(np.radians(90)))
    y_scale.append(-theta_span * np.sin(np.radians(90)))
    for i in range(phi.shape[1]):
        x_scale.append(0)
        y_scale.append(0)
        x_scale.append(theta_span*np.cos(np.radians(phi[0,i])))
        y_scale.append(theta_span*np.sin(np.radians(phi[0,i])))
        x_scale.append(-theta_span*np.cos(np.radians(phi[0,i])))
        y_scale.append(-theta_span*np.sin(np.radians(phi[0,i])))
    x_scale.append(0)
    y_scale.append(0)
    circle_points = range(0, 370, 10)
    last_i = 0
    for i in range(0,100,10):
        if i <= np.max(np.abs(theta[0])):
            for point in circle_points:
                x_scale.append(i*np.cos(np.radians(point)))
                y_scale.append(i*np.sin(np.radians(point)))
            last_i = i
        else:
            if last_i != -1:
                for point in circle_points:
                    x_scale.append((last_i+10)*np.cos(np.radians(point)))
                    y_scale.append((last_i+10)*np.sin(np.radians(point)))
                last_i = -1
    z_scale = np.full((1, len(x_scale)), zmin-offset).tolist()[0]

    figure.append(go.Scatter3d(x=x_scale,
                               y=y_scale,
                               z=z_scale,
                               mode='lines',
                               line=dict(color='black', width=2),
                               #marker=dict(color='black', size=2),
                               hoverinfo='skip'))

    x_scale_vals = []
    y_scale_vals = []
    text = []
    x_scale_vals.append(theta_span * np.cos(np.radians(0)))
    y_scale_vals.append(theta_span * np.sin(np.radians(0)))
    x_scale_vals.append(-theta_span * np.cos(np.radians(0)))
    y_scale_vals.append(-theta_span * np.sin(np.radians(0)))
    text.append('{:.2f}'.format(0))
    text.append('{:.2f}'.format(180))
    x_scale_vals.append(theta_span * np.cos(np.radians(90)))
    y_scale_vals.append(theta_span * np.sin(np.radians(90)))
    x_scale_vals.append(-theta_span * np.cos(np.radians(90)))
    y_scale_vals.append(-theta_span * np.sin(np.radians(90)))
    text.append('{:.2f}'.format(90))
    text.append('{:.2f}'.format(270))
    for i in range(phi.shape[1]):
        x_scale_vals.append(theta_span*np.cos(np.radians(phi[0,i])))
        y_scale_vals.append(theta_span*np.sin(np.radians(phi[0,i])))
        x_scale_vals.append(-theta_span*np.cos(np.radians(phi[0,i])))
        y_scale_vals.append(-theta_span*np.sin(np.radians(phi[0,i])))
        if phi[0, i] <= 180:
            text.append('{:.2f}'.format(phi[0,i]))
        if phi[0,i] != 0 and phi[0,i] < 180:
            text.append('{:.2f}'.format(phi[0,i]+180))
        else:
            text.append('')
    for i in range(np.abs(len(x_scale_vals)-len(text))):
        text.append('')
    last_i = 0
    for i in range(0,100,10):
        if i <= np.max(np.abs(theta[0])):
            x_scale_vals.append(0)
            y_scale_vals.append(i)
            text.append('{:.0f}'.format(i))
            last_i = i
        else:
            if last_i != -1:
                x_scale_vals.append(0)
                y_scale_vals.append(last_i+10)
                text.append('{:.0f}'.format(i))
                last_i = -1
    z_scale_vals = np.full((1, len(x_scale_vals)), zmin-offset).tolist()[0]

    figure.append(go.Scatter3d(x=x_scale_vals,
                               y=y_scale_vals,
                               z=z_scale_vals,
                               mode='markers+text',
                               #line=dict(color='black', width=2),
                               marker=dict(color='black', size=2),
                               text=text,
                               textposition="bottom center",
                               textfont_size=10,
                               hoverinfo='skip'))

    hight_points = range(6)

    figure.append(go.Scatter3d(x=np.full((1,len(hight_points)+1),-theta_span).tolist()[0],
                               y=np.full((1,len(hight_points)+1),0).tolist()[0],
                               z=[zmin-offset]+[zmin + i * (zmax - zmin) / 5 for i in hight_points],
                               text=['{:.4f}'.format(zmin-offset)]+['{:.4f}'.format(zmin + i * (zmax - zmin) / 5) for i in hight_points],
                               textposition="middle right",
                               textfont_size=10,
                               mode='lines+markers+text',
                               line=dict(color='black', width=2),
                               marker=dict(color='black', size=2),
                               hoverinfo='skip'))

    colorscale_range = range(11)
    # print(time.process_time())
    figure.append(go.Mesh3d(x=X_sc, y=Y_sc, z=Z_sc, color='grey', opacity=0.9, intensity=Z_sc, colorscale='Inferno',
                               hoverinfo='text',
                               hovertext=label_data,
                               cmin=zmin,
                               cmax=zmax,
                               colorbar = dict(tickvals=[zmin + i * (zmax - zmin) / 10 for i in colorscale_range],
                                               ticktext=['{:.4f}'.format(zmin + i * (zmax - zmin) / 10) for i in colorscale_range])))

    figure.append(go.Scatter3d(x=X_sc, y=Y_sc, z=Z_sc,
                               opacity=1,
                               mode='markers',
                               hoverinfo='skip',
                               marker=dict(color='black',#Z_sc,
                                           size=3,
                                           cmin=zmin,
                                           cmax=zmax,
                                           colorscale='Inferno')
                               ))
    # print(time.process_time())

    # figure.update_layout
    layout = go.Layout(title="BRDF 3D plot",
                       scene=dict(
                           xaxis_title="Theta (deg)",
                           yaxis_title="Theta (deg)",
                           zaxis_title="BRDF"),
                       scene_xaxis_visible=False,
                       scene_yaxis_visible=False,
                       scene_zaxis_visible=False,
                       scene_aspectmode='manual',
                       scene_aspectratio=dict(x=2, y=2, z=1),
                       showlegend=False,
                       scene_camera_projection_type = "orthographic")
    # print(time.process_time())
    # print({'data': figure, 'layout': layout})
    return {'data': figure, 'layout': layout}

@app.callback([Output('Projection_plot_previous_state', 'data'),
               Output('Projection_trigger_check', 'data')],
              [Input('trigger', 'data')],
              [State('Projection_plot_previous_state', 'data'),
               State('previous_state', 'data'),
               State('File-selector', 'value')])
def trigger_Projection_plot_update_check(trigger, plot_previous_state, previous_state, filename):
    if filename == None:
        raise PreventUpdate

    new_state = [previous_state[0],previous_state[1],previous_state[2],previous_state[3],previous_state[4], previous_state[6]]

    if new_state == plot_previous_state:
        raise PreventUpdate
    else:
        plot_previous_state = new_state

    return plot_previous_state, 'Triggered'

@app.callback(Output('Projection_trigger', 'data'),
              [Input('Projection_trigger_check', 'data')],
              [State('File-selector', 'value'),
               State('Projection_bezal_turned', 'data'),
               State('Projection_bezal_previous_state', 'data')])
def trigger_Projection_plot_update(trigger, filename, bezel, previous_bezel):
    if filename == None:
        raise PreventUpdate
    new_bezel = bezel
    if new_bezel > previous_bezel:
        raise PreventUpdate
    return 'Triggered'

@app.callback(Output('Projection_bezal_previous_state', 'data'),
              [Input('Projection_bezal_turned', 'data')])
def update_bezel_previous_state(bezel_new):
    time.sleep(0.5)
    return bezel_new

@app.callback(Output('Projection-plot','figure'),
              [Input('Projection_trigger', 'data'),
               Input('BRDF_mode_tab_update_trigger', 'data')],
              [State('browser_data_storage_1','data'),
               State('selected_file', 'data')])
def update_projection_plot(trigger1, trigger2, uploaded_data, filename):
    if trigger1 is None or uploaded_data == {} or filename == '':
        raise PreventUpdate

    thetas = np.array(uploaded_data[filename]['measurement_data']['thetaVs'])
    arranged_thetas = np.flip(np.append(np.flip(thetas[thetas<0]),thetas[thetas>=0]))
    phis = np.array(uploaded_data[filename]['measurement_data']['phiVs'])
    s_phi_v = uploaded_data[filename]['selected_states']['phi_V']

    thI = uploaded_data[filename]['selected_states']['theta_I']
    phiI = uploaded_data[filename]['selected_states']['phi_I']
    pol = uploaded_data[filename]['selected_states']['polarization']
    wl = uploaded_data[filename]['selected_states']['wavelength']
    # observer = uploaded_data[filename]['selected_states']['observer']
    # illuminant = uploaded_data[filename]['selected_states']['illuminant']
    data = uploaded_data[filename]['measurement_data']

    # tristimulus_values, RGB_values = get_tristimulus_XYZs(thI, phiI, pol, data, observer, illuminant)
    # RGB_values = np.array(RGB_values)

    z = np.array(select_data(wl, thI, phiI, pol, data))
    # print(time.process_time())
    # figure = go.Figure()
    figure = []

    r_bp = []
    theta_bp = []
    z_bp = []
    previous_radius = 0
    for theta in arranged_thetas:
        # scale = np.max(np.abs(arranged_thetas))
        radius = np.abs(theta) #2*np.sin(np.radians(theta)/2)
        #delta_r = np.abs(previous_radius-radius) #np.abs(scale*(previous_radius-radius)/np.sqrt(2))
        for phi in phis:
            # RGB_color = RGB_values[thetas == theta, phis == phi][0]
            if theta == 0:
                r_bp.append(0)
                theta_bp.append(0)
                z_bp.append(z[thetas == theta, phis == phi][0])
            if theta > 0:
                r_bp.append(radius)
                theta_bp.append(phi)
                z_bp.append(z[thetas == theta, phis == phi][0])
            elif theta < 0:
                r_bp.append(radius)
                theta_bp.append(180+phi)
                z_bp.append(z[thetas == theta, phis == phi][0])
                previous_radius = radius

    r_bp = np.array(r_bp)
    theta_bp = np.array(theta_bp)
    z_bp = np.array(z_bp)

    r_bp = r_bp[z_bp>=0]
    theta_bp = theta_bp[z_bp>=0]
    z_bp = z_bp[z_bp>=0]

    sorted_i = np.argsort(-r_bp)
    r_bp = r_bp[sorted_i]
    theta_bp = theta_bp[sorted_i]
    z_bp = z_bp[sorted_i]

    colorscale_range = range(11)
    zmax = np.max(z_bp)
    zmin = np.min(z_bp)

    figure.append(go.Barpolar(
        name = '',
        r = r_bp,
        theta = theta_bp,
        opacity = 1,
        base = 0,
        hovertemplate='\u03B8: %{r}' + '<br>\u03C6: %{theta}<br>',
        # marker_color='rgb('+str(RGB_color[0])+','+str(RGB_color[1])+','+str(RGB_color[2])+')',
        marker_cmin = zmin,
        marker_cmax = zmax,
        marker_colorscale = 'inferno',
        marker_color = z_bp,
        marker_colorbar = dict(tickvals=[zmin + i * (zmax - zmin) / 10 for i in colorscale_range],
                               ticktext=['{:.4f}'.format(zmin + i * (zmax - zmin) / 10) for i in colorscale_range]),
        showlegend = False))

    layout = go.Layout(
        title="BRDF polar heatmap",
        polar_bargap=0.005,
        polar_angularaxis_rotation = -s_phi_v
    )
    # print(time.process_time())
            # if theta < 0:
            #     figure.add_trace(pgo.Barpolar(
            #     r=np.flip(np.array([2*np.cos(np.radians(theta)) for angles in thetas])),
            #     theta=180+phis))
    return {'data': figure, 'layout': layout}

@app.callback([Output('Projection_bezal_turned', 'data'),
               Output('PhiV','value')],
              [Input('Projection-plot', 'relayoutData')],
              [State('browser_data_storage_1', 'data'),
               State('selected_file', 'data'),
               State('Projection_bezal_turned', 'data')])
def bezel_select_PhiV(relayoutData, uploaded_data, filename, bezel):
    if uploaded_data == {} or filename == '':
        raise PreventUpdate

    relayoutData = relayoutData
    # print(relayoutData)
    if relayoutData is None:
        #relayoutData = {'polar.angularaxis.rotation': 0}
        raise PreventUpdate
    if not 'polar.angularaxis.rotation' in relayoutData:
        #relayoutData['polar.angularaxis.rotation'] = 0
        raise PreventUpdate

    phis = np.array(uploaded_data[filename]['measurement_data']['phiVs'])

    selected_angle = [0]
    if 'polar.angularaxis.rotation' in relayoutData:
        angle = relayoutData['polar.angularaxis.rotation']
        if np.abs(angle) > 180:
            raise PreventUpdate
        else:
            if angle > 0:
                angle = np.abs(angle)
                d = np.abs(phis - angle)
                min_d = np.min(d)
                selected_angle = 360 - phis[d == min_d]
                if selected_angle[0] == 360:
                    selected_angle[0] = 0
            elif angle <= 0:
                angle = np.abs(angle)
                d = np.abs(phis - angle)
                min_d = np.min(d)
                selected_angle = phis[d == min_d]
    else:
        raise PreventUpdate

    # print(selected_angle)

    return bezel+1,selected_angle[0]

@app.callback([Output('2D_brdf_plot_previous_state', 'data'),
               Output('2D_trigger', 'data')],
              [Input('trigger', 'data')],
              [State('2D_brdf_plot_previous_state', 'data'),
               State('previous_state', 'data'),
               State('File-selector', 'value')])
def trigger_2D_brdf_plot(trigger, plot_previous_state, previous_state, filename):
    if filename == None:
        raise PreventUpdate

    new_state = [previous_state[0],previous_state[1],previous_state[2],previous_state[3],previous_state[4], previous_state[6]]
    if new_state == plot_previous_state:
        raise PreventUpdate
    else:
        plot_previous_state = new_state
    return plot_previous_state, 'Triggered'

@app.callback(Output('2D-BRDF','figure'),
              [Input('2D_trigger','data'),
               Input('BRDF_mode_tab_update_trigger', 'data')],
              [State('browser_data_storage_1','data'),
               State('selected_file', 'data')])
def update_2D_brdf_plot(trigger1, trigger2, uploaded_data, selected_filename):
    if trigger1 is None or uploaded_data == {} or selected_filename == '':
        raise PreventUpdate

    figure = go.Figure()

    for filename in uploaded_data:
        if uploaded_data[filename]['selected_states']['visible'] == [1] and filename != selected_filename:
            phis = np.array(uploaded_data[filename]['measurement_data']['phiVs'])
            thetas = np.array(uploaded_data[filename]['measurement_data']['thetaVs'])
            thI = uploaded_data[filename]['selected_states']['theta_I']
            phiI = uploaded_data[filename]['selected_states']['phi_I']
            pol = uploaded_data[filename]['selected_states']['polarization']
            wl = uploaded_data[filename]['selected_states']['wavelength']
            selected_angle = uploaded_data[filename]['selected_states']['phi_V']
            data = uploaded_data[filename]['measurement_data']
            selected_data = np.array(select_data(wl, thI, phiI, pol, data))

            if selected_angle == 180:
                phi_mask = np.logical_or(phis == 180, phis == 0)
            elif selected_angle == 360:
                phi_mask = np.logical_or(phis == 0, phis == 180)
            elif selected_angle < 180:
                phi_mask = np.logical_or(phis == selected_angle, phis == (selected_angle + 180))
            elif selected_angle > 180:
                phi_mask = np.logical_or(phis == selected_angle, phis == (selected_angle - 180))

            x = thetas
            y = selected_data[:, phi_mask].T

            selected_phiVs = phis[phi_mask]
            # print(selected_phiVs)

            if phis[phi_mask].shape[0] == 1:
                x = x
                y = y[0]
                x = x[y >= 0]
                y = y[y >= 0]
                figure.add_trace(go.Scatter(name='BRDF', x=x, y=y, mode='lines+markers'))
            elif phis[phi_mask].shape[0] == 2:
                y = np.concatenate((y[1][np.argsort(-x)], y[0]))
                x = np.concatenate((np.sort(-x), x))
                x = x[y >= 0]
                y = y[y >= 0]
                figure.add_trace(go.Scatter(name='BRDF',
                                            x=x,
                                            y=y,
                                            mode='lines+markers'))
                # figure.add_trace(go.Scatter(name='BRDF -90 to 0', x=-x, y=y[1], mode='lines+markers'))
            else:
                raise PreventUpdate

    phis = np.array(uploaded_data[selected_filename]['measurement_data']['phiVs'])
    thetas = np.array(uploaded_data[selected_filename]['measurement_data']['thetaVs'])
    thI = uploaded_data[selected_filename]['selected_states']['theta_I']
    phiI = uploaded_data[selected_filename]['selected_states']['phi_I']
    pol = uploaded_data[selected_filename]['selected_states']['polarization']
    wl = uploaded_data[selected_filename]['selected_states']['wavelength']
    selected_angle = uploaded_data[selected_filename]['selected_states']['phi_V']
    data = uploaded_data[selected_filename]['measurement_data']
    selected_data = np.array(select_data(wl, thI, phiI, pol, data))

    if selected_angle == 180:
        phi_mask = np.logical_or(phis == 180, phis == 0)
    elif selected_angle == 360:
        phi_mask = np.logical_or(phis == 0, phis == 180)
    elif selected_angle < 180:
        phi_mask = np.logical_or(phis == selected_angle, phis == (selected_angle + 180))
    elif selected_angle > 180:
        phi_mask = np.logical_or(phis == selected_angle, phis == (selected_angle - 180))

    x = thetas
    y = selected_data[:, phi_mask].T

    selected_phiVs = phis[phi_mask]
    # print(selected_phiVs)

    if phis[phi_mask].shape[0] == 1:
        x = x
        y = y[0]
        x = x[y >= 0]
        y = y[y >= 0]
        figure.add_trace(go.Scatter(name='BRDF', x=x, y=y, mode='lines+markers'))
    elif phis[phi_mask].shape[0] == 2:
        print(phis[phi_mask])
        y = np.concatenate((y[1][np.argsort(-x)], y[0]))
        x = np.concatenate((np.sort(-x), x))
        x = x[y >= 0]
        y = y[y >= 0]
        figure.add_trace(go.Scatter(name='BRDF',
                                    x=x,
                                    y=y,
                                    mode='lines+markers'))
        # figure.add_trace(go.Scatter(name='BRDF -90 to 0', x=-x, y=y[1], mode='lines+markers'))
    else:
        raise PreventUpdate


    figure.update_layout(
        title="BRDF 2D plot at selected viewing azimuth",
        xaxis_title='Viewing zenith angle Theta (deg)',
        xaxis_nticks=15,
        xaxis_gridcolor='rgb(112,112,112)',
        xaxis_zerolinecolor='rgb(0,0,0)',
        yaxis_title='Radiance factor',
        yaxis_nticks=10,
        yaxis_gridcolor='rgb(112,112,112)',
        yaxis_zerolinecolor='rgb(0,0,0)',
        plot_bgcolor='rgb(255,255,255)'
    )

    return figure

@app.callback([Output('2D_BRDF_plot_clicked', 'data'),
               Output('ThetaV','value')],
              [Input('2D-BRDF', 'clickData')],
              [State('browser_data_storage_1', 'data'),
               State('selected_file', 'data'),
               State('2D_BRDF_plot_clicked', 'data')])
def plot_2D_select_ThetaV(clickData, uploaded_data, filename, clicks):
    if uploaded_data == {} or filename == '':
        raise PreventUpdate

    thetas = np.array(uploaded_data[filename]['measurement_data']['thetaVs'])

    if clickData is not None:
        selected_theta = clickData['points'][0]['x']
    else:
        raise PreventUpdate
    return clicks+1, selected_theta

@app.callback([Output('Pspec_previous_state', 'data'),
               Output('Pspec_trigger', 'data')],
              [Input('trigger', 'data')],
              [State('Pspec_previous_state', 'data'),
               State('previous_state', 'data'),
               State('File-selector', 'value')])
def trigger_Pspec_plot(trigger, plot_previous_state, previous_state, filename):
    if filename == None:
        raise PreventUpdate

    new_state = [previous_state[0], previous_state[2], previous_state[3], previous_state[4], previous_state[5],
                 previous_state[6]]
    if new_state == plot_previous_state:
        raise PreventUpdate
    else:
        plot_previous_state = new_state
    return plot_previous_state, 'Triggered'

@app.callback(Output('Point-spectrum','figure'),
              [Input('Pspec_trigger','data'),
               Input('BRDF_mode_tab_update_trigger', 'data')],
              [State('browser_data_storage_1', 'data'),
               State('selected_file', 'data')])
def update_Spectrum_plot(trigger1, trigger2, uploaded_data, selected_filename):
    if selected_filename is None or uploaded_data == {}:
        raise PreventUpdate

    figure = go.Figure()

    for filename in uploaded_data:
        if uploaded_data[filename]['selected_states']['visible'] == [1] and filename != selected_filename:
            thI = uploaded_data[filename]['selected_states']['theta_I']
            phiI = uploaded_data[filename]['selected_states']['phi_I']
            thV = uploaded_data[filename]['selected_states']['theta_V']
            phiV = uploaded_data[filename]['selected_states']['phi_V']
            pol = uploaded_data[filename]['selected_states']['polarization']
            wls = uploaded_data[filename]['measurement_data']['Wavelengths']
            data = uploaded_data[filename]['measurement_data']

            x = wls
            y = select_spectrum(thV, phiV, thI, phiI, pol, data)

            figure.add_trace(go.Scatter(x=x, y=y[0], mode='lines+markers'))


    thI = uploaded_data[selected_filename]['selected_states']['theta_I']
    phiI = uploaded_data[selected_filename]['selected_states']['phi_I']
    thV = uploaded_data[selected_filename]['selected_states']['theta_V']
    phiV = uploaded_data[selected_filename]['selected_states']['phi_V']
    pol = uploaded_data[selected_filename]['selected_states']['polarization']
    wls = uploaded_data[selected_filename]['measurement_data']['Wavelengths']
    data = uploaded_data[selected_filename]['measurement_data']

    x = wls
    y = select_spectrum(thV,phiV,thI,phiI,pol,data)


    figure.add_trace(go.Scatter(x = x, y = y[0], mode='lines+markers'))

    figure.update_layout(
        title="Reflectance spectrum at selected viewing zenith and azimuth",
        xaxis_title='Wavelength (nm)',
        yaxis_title='Radiance factor',
        xaxis_nticks=15,
        xaxis_gridcolor='rgb(112,112,112)',
        xaxis_zerolinecolor='rgb(0,0,0)',
        yaxis_nticks=10,
        yaxis_gridcolor='rgb(112,112,112)',
        yaxis_zerolinecolor='rgb(0,0,0)',
        plot_bgcolor='rgb(255,255,255)'
    )
    # print('ok')
    return figure

# @app.callback([Output('2D-BRDF','figure'),
#                Output('selected_phiv','data')],
#               [Input('Projection-plot','figure'),
#                Input('Projection-plot','relayoutData')],
#               [State('browser_data_storage','data'),
#                State('selected_data','data')])
# def update_2D_brdf_plot(fig, relayoutData, data, selected_data):
#     if fig is None:
#         raise PreventUpdate
#
#     figure = go.Figure()
#     phis = np.array(data['phiVs'])
#     thetas = np.array(data['thetaVs'])
#     data = np.array(data['data'])
#     selected_data = np.array(selected_data)
#     relayoutData = relayoutData
#
#     if relayoutData is None:
#         relayoutData = {'polar.angularaxis.rotation': 0}
#     if not 'polar.angularaxis.rotation' in relayoutData:
#         relayoutData['polar.angularaxis.rotation'] = 0
#
#     selected_angle = [0]
#     if 'polar.angularaxis.rotation' in relayoutData:
#         angle = relayoutData['polar.angularaxis.rotation']
#         if np.abs(angle) > 180:
#             raise PreventUpdate
#         else:
#             if angle > 0:
#                 angle = np.abs(angle)
#                 d = np.abs(phis-angle)
#                 min_d = np.min(d)
#                 selected_angle = 360-phis[d == min_d]
#             elif angle <= 0:
#                 angle = np.abs(angle)
#                 d = np.abs(phis-angle)
#                 min_d = np.min(d)
#                 selected_angle = phis[d == min_d]
#     else:
#         raise PreventUpdate
#
#     selected_angle = selected_angle[0]
#     if selected_angle == 180:
#         phi_mask = np.logical_or(phis == 180, phis == 0)
#     elif selected_angle == 360:
#         phi_mask = np.logical_or(phis == 0,phis == 180)
#     elif selected_angle < 180:
#         phi_mask = np.logical_or(phis == selected_angle, phis == (selected_angle+180))
#     elif selected_angle > 180:
#         phi_mask = np.logical_or(phis == selected_angle, phis == (selected_angle-180))
#
#     print(phi_mask)
#
#     x = thetas
#     y = selected_data[:,phi_mask].T
#
#     selected_phiVs = phis[phi_mask]
#     print(selected_phiVs)
#
#     if phis[phi_mask].shape[0] == 1:
#         figure.add_trace(go.Scatter(name='BRDF',x = x, y = y[0], mode='lines+markers'))
#     elif phis[phi_mask].shape[0] == 2:
#         figure.add_trace(go.Scatter(name='BRDF 0 to 90',x = x, y = y[0], mode='lines+markers'))
#         figure.add_trace(go.Scatter(name='BRDF -90 to 0',x = -x, y = y[1], mode='lines+markers'))
#     else:
#         raise PreventUpdate
#
#     figure.update_layout(
#         title="BRDF 2D plot at selected viewing azimuth",
#         xaxis_title='Viewing zenith angle Theta (deg)',
#         yaxis_title='Radiance factor'
#     )
#
#     return figure, selected_phiVs
#
# @app.callback(Output('Point-spectrum','figure'),
#               [Input('2D-BRDF','clickData'),
#                Input('2D-BRDF','figure')],
#               [State('browser_data_storage','data'),
#                State('ThetaI','value'),
#                State('PhiI','value'),
#                State('Polarization','value'),
#                State('selected_phiv','data')])
# def update_Spectrum_plot(clickData, fig, data, ThetaI, PhiI, Polarization, selected_phiVs):
#     if fig is None:
#         raise PreventUpdate
#
#     thetaVs = np.array(data['thetaVs'])
#     phiVs = np.array(data['phiVs'])
#     selected_phiVs = np.array(selected_phiVs)
#     if clickData is not None:
#         selected_theta = clickData['points'][0]['x']
#     else:
#         selected_theta = None
#
#     x = np.array(data['Wavelengths'])
#     y = np.empty(1)
#     if selected_theta is None:
#         y = select_spectrum(thetaVs[0], phiVs[0], ThetaI, PhiI, Polarization, data)
#     else:
#         if selected_phiVs.shape[0] == 1:
#             y = select_spectrum(selected_theta,selected_phiVs[0], ThetaI, PhiI, Polarization, data)
#         elif selected_phiVs.shape[0] == 2:
#             if clickData['points'][0]['curveNumber'] == 0:
#                 y = select_spectrum(selected_theta,selected_phiVs[0], ThetaI, PhiI, Polarization, data)
#             elif clickData['points'][0]['curveNumber'] == 1:
#                 y = select_spectrum(-selected_theta,selected_phiVs[1], ThetaI, PhiI, Polarization, data)
#     if y.shape[0] == 0:
#         y = select_spectrum(thetaVs[0], phiVs[0], ThetaI, PhiI, Polarization, data)
#
#     figure = go.Figure()
#     figure.add_trace(go.Scatter(x = x, y = y[0], mode='lines+markers'))
#
#     figure.update_layout(
#         title="Reflectance spectrum at selected viewing zenith and azimuth",
#         xaxis_title='Wavelength (nm)',
#         yaxis_title='Radiance factor'
#     )
#     return figure
#
# @app.callback(Output('CIELAB-3Dplot','figure'),
#               [Input('Point-spectrum','figure')],
#               [State('tristimulus_XYZ_values','data'),
#                State('selected_phiv','data'),
#                State('browser_data_storage','data')])
# def update_CIELAB_3Dplot(fig, tristimulus_XYZ, selected_phi, data):
#     if fig is None or tristimulus_XYZ is None or selected_phi is None:
#         raise PreventUpdate
#
#     selected_phi = np.array(selected_phi)
#     phiVs = np.array(data['phiVs'])
#     tristimulus_XYZ = np.array(tristimulus_XYZ)
#
#     figure = go.Figure()
#
#     if selected_phi.shape[0] == 1:
#         selected_XYZ = tristimulus_XYZ[:, phiVs == selected_phi[0]][:,0,:]
#         selected_LAB = np.array([clr.XYZ_to_Lab(selected_XYZ[i]/100) for i in range(selected_XYZ.shape[0])])
#         figure.add_trace(go.Scatter3d(x=selected_LAB[:,1], y=selected_LAB[:,2], z=selected_LAB[:,0], mode='lines+markers'))
#     elif selected_phi.shape[0] == 2:
#         selected_XYZ_pos = tristimulus_XYZ[:, phiVs == selected_phi[0]][:,0,:]
#         selected_LAB_pos = np.array([clr.XYZ_to_Lab(selected_XYZ_pos[i]/100) for i in range(selected_XYZ_pos.shape[0])])
#         figure.add_trace(go.Scatter3d(x=selected_LAB_pos[:, 1], y=selected_LAB_pos[:, 2], z=selected_LAB_pos[:, 0], mode='lines+markers'))
#         selected_XYZ_neg = tristimulus_XYZ[:, phiVs == selected_phi[1]][:,0,:]
#         selected_XYZ_neg = np.array([clr.XYZ_to_Lab(selected_XYZ_neg[i]/100) for i in range(selected_XYZ_neg.shape[0])])
#         figure.add_trace(go.Scatter3d(x=selected_XYZ_neg[:, 1], y=selected_XYZ_neg[:, 2], z=selected_XYZ_neg[:, 0], mode='lines+markers'))
#     else:
#         raise PreventUpdate
#
#     figure.update_layout(title="Color travel 3D plot in CIELab space",
#                          scene=dict(
#                              xaxis_title="a*",
#                              yaxis_title="b*",
#                              zaxis_title="L*"
#                          )
#                     )
#
#     return figure
#
# @app.callback(Output('CIEAB-plot','figure'),
#               [Input('CIELAB-3Dplot','figure')],
#               [State('tristimulus_XYZ_values','data'),
#                State('selected_phiv','data'),
#                State('browser_data_storage','data')])
# def update_CIELAB_3Dplot(fig, tristimulus_XYZ, selected_phi, data):
#     if fig is None or tristimulus_XYZ is None or selected_phi is None:
#         raise PreventUpdate
#
#     selected_phi = np.array(selected_phi)
#     phiVs = np.array(data['phiVs'])
#     tristimulus_XYZ = np.array(tristimulus_XYZ)
#
#     figure = go.Figure()
#
#     if selected_phi.shape[0] == 1:
#         selected_XYZ = tristimulus_XYZ[:, phiVs == selected_phi[0]][:,0,:]
#         selected_LAB = np.array([clr.XYZ_to_Lab(selected_XYZ[i]/100) for i in range(selected_XYZ.shape[0])])
#         figure.add_trace(go.Scatter(name='projection',x=selected_LAB[:,1], y=selected_LAB[:,2], mode='lines+markers'))
#     elif selected_phi.shape[0] == 2:
#         selected_XYZ_pos = tristimulus_XYZ[:, phiVs == selected_phi[0]][:,0,:]
#         selected_LAB_pos = np.array([clr.XYZ_to_Lab(selected_XYZ_pos[i]/100) for i in range(selected_XYZ_pos.shape[0])])
#         figure.add_trace(go.Scatter(name='projection 0 to 90',x=selected_LAB_pos[:, 1], y=selected_LAB_pos[:, 2], mode='lines+markers'))
#         selected_XYZ_neg = tristimulus_XYZ[:, phiVs == selected_phi[1]][:,0,:]
#         selected_XYZ_neg = np.array([clr.XYZ_to_Lab(selected_XYZ_neg[i]/100) for i in range(selected_XYZ_neg.shape[0])])
#         figure.add_trace(go.Scatter(name='projection -90 to 0',x=selected_XYZ_neg[:, 1], y=selected_XYZ_neg[:, 2], mode='lines+markers'))
#     else:
#         raise PreventUpdate
#
#     figure.update_layout(
#         title="CIELab colorspace projection to a*b* plane",
#         xaxis_title='a*',
#         yaxis_title='b*'
#     )
#
#     return figure
#
# @app.callback(Output('CIELAB-plot','figure'),
#               [Input('CIEAB-plot','figure')],
#               [State('tristimulus_XYZ_values','data'),
#                State('selected_phiv','data'),
#                State('browser_data_storage','data')])
# def update_CIELAB_3Dplot(fig, tristimulus_XYZ, selected_phi, data):
#     if fig is None or tristimulus_XYZ is None or selected_phi is None:
#         raise PreventUpdate
#
#     selected_phi = np.array(selected_phi)
#     phiVs = np.array(data['phiVs'])
#     thetaVs = np.array(data['thetaVs'])
#     tristimulus_XYZ = np.array(tristimulus_XYZ)
#
#     figure = go.Figure()
#
#     if selected_phi.shape[0] == 1:
#         selected_XYZ = tristimulus_XYZ[:, phiVs == selected_phi[0]][:,0,:]
#         selected_LAB = np.array([clr.XYZ_to_Lab(selected_XYZ[i]/100) for i in range(selected_XYZ.shape[0])])
#         figure.add_trace(go.Scatter(name='L*',y=selected_LAB[:,0], x=thetaVs, mode='lines+markers',marker=dict(color='yellow'),line=dict(color='yellow')))
#         figure.add_trace(go.Scatter(name='a*',y=selected_LAB[:, 1], x=thetaVs, mode='lines+markers',marker=dict(color='red'),line=dict(color='red')))
#         figure.add_trace(go.Scatter(name='b*',y=selected_LAB[:, 2], x=thetaVs, mode='lines+markers',marker=dict(color='blue'),line=dict(color='blue')))
#     elif selected_phi.shape[0] == 2:
#         selected_XYZ_pos = tristimulus_XYZ[:, phiVs == selected_phi[0]][:,0,:]
#         selected_LAB_pos = np.array([clr.XYZ_to_Lab(selected_XYZ_pos[i]/100) for i in range(selected_XYZ_pos.shape[0])])
#         figure.add_trace(go.Scatter(name='L* 0 to 90',y=selected_LAB_pos[:, 0], x=thetaVs, mode='lines+markers', marker=dict(color='yellow'),line=dict(color='yellow')))
#         figure.add_trace(go.Scatter(name='a* 0 to 90',y=selected_LAB_pos[:, 1], x=thetaVs, mode='lines+markers', marker=dict(color='red'),line=dict(color='red')))
#         figure.add_trace(go.Scatter(name='b* 0 to 90',y=selected_LAB_pos[:, 2], x=thetaVs, mode='lines+markers', marker=dict(color='blue'),line=dict(color='blue')))
#         selected_XYZ_neg = tristimulus_XYZ[:, phiVs == selected_phi[1]][:,0,:]
#         selected_XYZ_neg = np.array([clr.XYZ_to_Lab(selected_XYZ_neg[i]/100) for i in range(selected_XYZ_neg.shape[0])])
#         figure.add_trace(go.Scatter(name='L* -90 to 0',y=selected_XYZ_neg[:, 0], x=-thetaVs, mode='lines+markers',marker=dict(color='yellow'),line=dict(color='yellow')))
#         figure.add_trace(go.Scatter(name='a* -90 to 0',y=selected_XYZ_neg[:, 1], x=-thetaVs, mode='lines+markers',marker=dict(color='red'),line=dict(color='red')))
#         figure.add_trace(go.Scatter(name='b* -90 to 0',y=selected_XYZ_neg[:, 2], x=-thetaVs, mode='lines+markers',marker=dict(color='blue'),line=dict(color='blue')))
#     else:
#         raise PreventUpdate
#
#     figure.update_layout(
#         title="CIELab values dependence on viewing zenith angle",
#         xaxis_title='CIELab units',
#         yaxis_title='Viewing zenith angle Theta (deg)'
#     )
#
#     return figure

app.layout = server_layout()

if __name__ == '__main__':
    app.run_server(debug=False)
