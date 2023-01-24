import base64
import json
import dash_gif_component as gif
# import colour as clr
import dash
import dash_core_components as dcc
import dash_html_components as html
# import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, MATCH, ALL
from dash.exceptions import PreventUpdate
from parse_brdf_json import parse_brdf_json, validate_brdf_json
from jsonschema import validate, FormatChecker
# from helper_functions import *
# import colour as clr
import numpy as np
import plotly.graph_objects as go
from help_text import *
import time
import copy

#App configurations
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
#external_stylesheets = [dbc.themes.SIMPLEX]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)
server = app.server
app.config['suppress_callback_exceptions'] = True
colors = {'background': '#111111', 'text': '#000080'}

json_schema = open('BRDF_JSON_schema/brdf_json_schema_v1.0.json')
dict_from_json_schema = json.loads(json_schema.read())

# Static application page layout
def server_layout():
    layout = html.Div([
        # Triggers (to avoid work of some callbacks before dynamic content is rendered)
        # Logic: trigger is type, following words describe origin of the trigger
        dcc.Store(id={'type': 'trigger', 'index': 'menu-tabs'}, storage_type='memory', data='Triggered'),
        dcc.Store(id={'type': 'trigger', 'index': 'applet-tab'}, storage_type='memory', data='Triggered'),
        dcc.Store(id={'type': 'trigger', 'index': 'app-modes'}, storage_type='memory', data='Triggered'),
        dcc.Store(id={'type': 'trigger', 'index': 'mode-brdf-tab'}, storage_type='memory', data='Triggered'),
        dcc.Store(id={'type': 'trigger', 'index': 'file-navigator-tabs'}, storage_type='memory', data='Triggered'),
        dcc.Store(id={'type': 'trigger', 'index': 'upload-data'}, storage_type='memory', data='Triggered'),
        dcc.Store(id={'type': 'trigger', 'index': 'validator-upload-data'}, storage_type='memory', data='Triggered'),
        dcc.Store(id={'type': 'trigger', 'index': 'update-menu'}, storage_type='memory', data='Triggered'),
        dcc.Store(id={'type': 'trigger', 'index': 'modify-state'}, storage_type='memory', data='Triggered'),
        dcc.Store(id={'type': 'trigger', 'index': 'for-3d-plot'}, storage_type='memory', data='Triggered'),
        dcc.Store(id={'type': 'trigger', 'index': 'for-projection-plot'}, storage_type='memory', data='Triggered'),
        dcc.Store(id={'type': 'trigger', 'index': 'change-snap-states'}, storage_type='memory', data='Triggered'),
        dcc.Store(id={'type': 'trigger', 'index': 'for-2D-brdf-plot'}, storage_type='memory', data='Triggered'),
        dcc.Store(id={'type': 'trigger', 'index': 'for-2D-arbitrary-plot'}, storage_type='memory', data='Triggered'),


        # Memory variables
        # remember which app mode was previosly selected under Applet tab
        dcc.Store(id={'type': 'memory', 'index': 'app-modes-tab-value'}, storage_type='memory', data='BRDF'),
        # store uploaded files' data
        html.Div(id={'type': 'memory', 'index': 'browser_data_storage_update'},
                 children=dcc.Store(id={'type': 'memory', 'index': 'browser_data_storage'}, storage_type='memory', data={}),
                 style={'display': None}),
        # remember which uploaded file was previosly selected
        dcc.Store(id={'type': 'memory', 'index': 'selected_file'}, storage_type='memory', data=''),
        # remember what were were the chosen values of variables i.e. remember menu state.
        dcc.Store(id={'type': 'memory', 'index': 'previous_state'}, storage_type='memory', data={}),
        dcc.Store(id={'type': 'memory', 'index': '3d-plot-previous-state'}, storage_type='memory', data={}),
        dcc.Store(id={'type': 'memory', 'index': 'projection-plot-previous-state'}, storage_type='memory', data={}),
        dcc.Store(id={'type': 'memory', 'index': 'projection-bezel-turned'}, storage_type='memory', data=1),
        dcc.Store(id={'type': 'memory', 'index': 'projection-bezel-previous-state'}, storage_type='memory', data=1),
        dcc.Store(id={'type': 'memory', 'index': 'snaped-states'}, storage_type='memory', data={}),
        dcc.Store(id={'type': 'memory', 'index': '2D-brdf-plot-previous-state'}, storage_type='memory', data={}),
        dcc.Store(id={'type': 'memory', 'index': '2D-brdf-plot-clicked'}, storage_type='memory', data=1),
        dcc.Store(id={'type': 'memory', 'index': '2D-arbitrary-plot-previous-state'}, storage_type='memory', data=1),

        # App header
        html.Div(children=[
            html.Img(src=app.get_asset_url('BiRDlogo.png'), style={'width': '110px', 'height': '100px', 'margin-left': '100px', 'margin-right': '145px'}),
            html.H1(children='BiRD view v4.0',
                    style={'textAlign': 'center', 'color': colors['text'], 'height': '25px',
                           'line-height': '50px'}),
            html.Img(src=app.get_asset_url('Euramet_logo.jpg'), style={}),
        ],
        style={'display': 'flex', 'flex-direction': 'row', 'flex-wrap': 'nowrap', 'align-items': 'flex-end', 'justify-content': 'space-around'}),
        html.Div(children='''A web application for BRDF data visualization.''',
                 style={'textAlign': 'center', 'color': colors['text'], 'width': '100%', 'height': '25px', 'line-height':'50px'}),
        html.Hr(style={'margin-bottom':'2.5px'}),

        # App and Help tabs definition and description
        dcc.Tabs(id={'type': 'menu-tabs', 'index': 0}, value='Applet', children=[
            dcc.Tab(id={'type': 'applet-tab', 'index': 'Applet'}, label='Applet', value='Applet',
                    style={'line-height': '50px', 'padding': '0', 'height': '50px'},
                    selected_style={'line-height': '50px', 'padding': '0', 'height': '50px'}
                    ),
            dcc.Tab(id={'type': 'applet-tab', 'index': 'Validator'}, label='BRDF json validator', value='Validator',
                    style={'line-height': '50px', 'padding': '0', 'height': '50px'},
                    selected_style={'line-height': '50px', 'padding': '0', 'height': '50px'}
                    ),
            dcc.Tab(id={'type': 'applet-tab', 'index': 'Help'}, label='Help', value='Help',
                    style={'line-height': '50px', 'padding': '0', 'height': '50px'},
                    selected_style={'line-height': '50px', 'padding': '0', 'height': '50px'})],
                 style={'width': '100%', 'height': '50px', 'line-height': '50px', 'textAlign': 'top', 'margin-bottom': '2.5px', 'margin-top': '2.5px'}),

        # Container for App and Help tab's content that is rendered dynamically in the next following dedicated callback function
        html.Div(id={'type': 'menu-tabs-content', 'index': 0})
    ])
    return layout

#Callback to render contents of Application and Helb tabs. Contents are displayed in id={'type': 'menu-tabs-content', 'index': 0} Div container.
#Trigger is sent to notify about the end of content's rendering. Function is called when value of Tabs is changed.
@app.callback([Output({'type': 'menu-tabs-content', 'index': 0}, 'children'),
               Output({'type': 'trigger', 'index': 'menu-tabs'}, 'data')],
              [Input({'type': 'menu-tabs', 'index': 0}, 'value')],
              [State({'type': 'memory', 'index': 'app-modes-tab-value'}, 'data')])
def render_menu_tabs_content(tab, app_mode):
    # Rendering contents for Applet tab
    if tab == 'Applet':
        return html.Div(children=[
            # Container with animated upload field dash component.
            html.Div(id={'type': 'file-loading-container', 'index': 0},  children=[
                dcc.Loading(id={'type': 'file-loading', 'index': 0}, children=[
                    dcc.Upload(id={'type': 'upload-data', 'index': 0},
                               children=html.Div(id={'type': 'loading-state', 'index': 0},
                                                 children=['Drag and Drop or ', html.A('Select Files')]),
                               style={'width': '100%', 'height': '50px', 'lineHeight': '50px',
                                      'borderWidth': '1px', 'borderStyle': 'dashed', 'borderRadius': '7.5px',
                                      'textAlign': 'center', 'margin-bottom':'2.5px', 'margin-top':'2.5px',
                                      'borderColor': 'Grey'},
                               multiple=True)
                ], type='default', style={'width': '100%', 'height': '50', 'lineHeight': '50px',
                                          'borderWidth': '1px', 'borderStyle': 'dashed', 'borderRadius': '7.5px',
                                          'textAlign': 'center','margin-bottom':'2.5px', 'margin-top':'2.5px',
                                          'borderColor': 'Grey'})
            ], className="row"),

            # Container for file navigation menu as well as application mode's tabs.
            html.Div(children=[
                # File menu container
                html.Div(children=[
                    # File options container
                    html.Div(id={'type': 'file-menu-container', 'index': 0},
                             children=[
                                 html.P(children='Uploaded files',
                                        style={'textAlign': 'center', 'font-size': '20px',
                                               'line-height': '50px', 'padding': '0', 'height': '50px',
                                               'borderWidth': '1px', 'borderStyle': 'solid', 'borderRadius': '5px',
                                               'borderColor': 'LightGrey', 'background-color': '#f9f9f9'}),
                                 html.P('Select file:',
                                        style={'margin-bottom': '2.5px', 'margin-top': '2.5px'}),
                                 # File selector dropdown
                                 dcc.Dropdown(id={'type': 'options_sp', 'index': 'file-names-dropdown'},
                                              placeholder="File name", clearable=False,
                                              options=[{'label': 'no fliles', 'value': 'no_files'}],
                                              value='no files',
                                              style={'margin-bottom': '2.5px', 'margin-top': '2.5px'}),
                                 html.Hr(style={'margin-bottom': '5px', 'margin-top': '5px'}),
                                 dcc.Tabs(id={'type': 'file-navigator-tabs', 'index': 0}, value='options', children=[
                                     dcc.Tab(id={'type': 'file-navigator-tab', 'index': 'options'}, label='Options', value='options',
                                             style={'line-height': '35px', 'padding': '0', 'height': '35px'},
                                             selected_style={'line-height': '35px', 'padding': '0', 'height': '35px'}
                                             ),
                                     dcc.Tab(id={'type': 'file-navigator-tab', 'index': 'metadata'}, label='Metadata', value='metadata',
                                             style={'line-height': '35px', 'padding': '0', 'height': '35px'},
                                             selected_style={'line-height': '35px', 'padding': '0', 'height': '35px'}
                                             ),],
                                          style={'width': '100%', 'height': '35px', 'line-height': '35px',
                                                 'textAlign': 'top', 'margin-bottom': '2.5px', 'margin-top': '2.5px'}),
                                 html.P(
                                     'File menu options and metadata dependend on file contents and will appear upon first file upload',
                                     style={'textAlign': 'center', 'borderWidth': '1px', 'borderStyle': 'dashed',
                                            'borderRadius': '7.5px', 'margin-top': '2.5px', 'word-wrap': 'normal',
                                            'borderColor': 'LightGrey'})
                             ],
                        style={'textAlign': 'center', 'transform': 'rotateX(180deg)','z-index': '1500'}),
                ],
                    style={'order': '1', 'flex-grow': '1', 'resize': 'horizontal', 'overflow': 'auto',
                           'transform': 'rotateX(180deg)', 'width': '5%', 'height': '1350px',
                           'display': 'flex', 'flex-direction': 'column-reverse', 'flex-wrap': 'nowrap',
                           'align-items': 'stretch', 'margin-right': '2.5px'}),

                # Container describing Application BRDF visualization modes' tabs
                html.Div(children=[
                    # Dash Tabs component with defined tabs.
                    dcc.Tabs(id={'type': 'applet-modes', 'index': 0}, value=app_mode, children=[
                        dcc.Tab(id={'type': 'applet-BRDF', 'index': 0}, label='BRDF visualisation', value='BRDF',
                                style={'line-height': '50px', 'padding': '0', 'height': '50px'},
                                selected_style={'line-height': '50px', 'padding': '0', 'height': '50px'}),
                        dcc.Tab(id={'type': 'applet-COLOR', 'index': 0}, label='CIELAB', value='CIELAB',
                                style={'line-height': '50px', 'padding': '0', 'height': '50px'},
                                selected_style={'line-height': '50px', 'padding': '0', 'height': '50px'})
                    ],
                             style={'width': '100%', 'height': '50px', 'line-height': '50px', 'textAlign': 'top'}
                             ),
                    # Container for tabs' contents
                    html.Div(id={'type': 'applet-modes-content', 'index': 0})],
                    style={'order': '2', 'flex-grow': '6', 'overflow': 'auto', 'margin-left': '2.5px'}
                )
            ], style={'display': 'flex', 'flex-direction': 'row', 'flex-wrap': 'nowrap', 'align-items': 'stretch',
                      'margin-bottom': '2.5px', 'margin-top': '2.5px', 'height': '1500px'}),
        ]
        ), 'Triggered'
    #Rendering contents for BRDF JSON validator Tab
    elif tab == 'Validator':
        return html.Div(children=[
            html.Div(children=dcc.Markdown('Validation is conducted using following JSON Schema: [brdf_json_schema_v1.0.json](https://jsoneditoronline.org/#right=local.yutupo&left=url.https%3A%2F%2Fraw.githubusercontent.com%2FBiRD-project%2FBiRD_view%2Fmaster%2FBRDF_JSON_schema%2Fbrdf_json_schema_v1.0.json)'),
                                     style={'width': '100%', 'height': '30px', 'lineHeight': '30px',
                                            'borderWidth': '1px', 'borderStyle': 'solid', 'borderRadius': '7.5px',
                                            'textAlign': 'center', 'margin-bottom': '5px', 'margin-top': '2.5px',
                                            'borderColor': 'LightGrey'}
                     ),
            html.Div(id={'type': 'file-loading-container', 'index': 1}, children=[
                dcc.Loading(id={'type': 'file-loading', 'index': 1}, children=[
                    dcc.Upload(id={'type': 'upload-data', 'index': 1},
                               children=html.Div(id={'type': 'loading-state', 'index': 1},
                                                 children=['Drag and Drop or ', html.A('Select Files')]),
                               style={'width': '100%', 'height': '50px', 'lineHeight': '50px',
                                      'borderWidth': '1px', 'borderStyle': 'dashed', 'borderRadius': '7.5px',
                                      'textAlign': 'center', 'margin-bottom': '2.5px', 'margin-top': '2.5px',
                                      'borderColor': 'Grey'},
                               multiple=True)
                ], type='default', style={'width': '100%', 'height': '50', 'lineHeight': '50px',
                                          'borderWidth': '1px', 'borderStyle': 'dashed', 'borderRadius': '7.5px',
                                          'textAlign': 'center', 'margin-bottom': '2.5px', 'margin-top': '2.5px',
                                          'borderColor': 'Grey'})
            ], className="row"),

            html.Div(id={'type': 'validator-information-container', 'index': 0}, children=[
                html.P('List of uploaded files with their validity information will be shown here',
                       style={'width': '100%', 'height': '50', 'lineHeight': '50px',
                              'borderWidth': '1px', 'borderStyle': 'solid', 'borderRadius': '7.5px',
                              'textAlign': 'center', 'margin-bottom': '2.5px', 'margin-top': '2.5px',
                              'borderColor': 'LightGrey'})
            ])

        ]), 'Triggered'
    #Rendering contents for Help Tab
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
                          gif='assets/metadata.gif',
                          still='assets/metadata.png')],
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
                          gif='assets/multiPlot.gif',
                          still='assets/multiPlot.png')],
                          style={'width': '70%'}),
                      html.Div(children=dcc.Markdown(help_text_markdown_part_9,
                                                     style={'width': '70%'})),
                      html.Div([gif.GifPlayer(
                          gif='assets/multiData.gif',
                          still='assets/multiData.png')],
                          style={'width': '70%'}),
                      html.Div(children=dcc.Markdown(help_text_markdown_part_10,
                                                     style={'width': '70%'})),
                      html.Div([gif.GifPlayer(
                          gif='assets/interaction.gif',
                          still='assets/interaction.png')],
                          style={'width': '70%'}),
                      ]
        ), 'Triggered'

# Callback needed to check whether exactly "Applet" tab was triggered
@app.callback(Output({'type': 'trigger', 'index': 'applet-tab'}, 'data'),
              [Input({'type': 'trigger', 'index': 'menu-tabs'}, 'data')],
              [State({'type': 'menu-tabs', 'index': 0}, 'value')])
def applet_tab_selected_trigger(trigger, tab):
    if tab != 'Applet':
        raise PreventUpdate
    else:
        return 'Triggered'

@app.callback([Output({'type': 'applet-modes-content', 'index': 0}, 'children'),
               Output({'type': 'memory', 'index': 'app-modes-tab-value'}, 'data'),
               Output({'type': 'trigger', 'index': 'app-modes'}, 'data')],
              [Input({'type': 'applet-modes', 'index': 0}, 'value')])
def render_applet_modes_content(tab):
    if tab is None:
        raise PreventUpdate
    if tab == 'BRDF':
        return html.Div(
            children=[
                html.Div(children=[
                    html.Div(dcc.Loading(id='3D-plot-L',
                                         children=dcc.Graph(id={'type': 'graph', 'index': '3d-brdf'}, responsive=True),
                                         style={'height': '420px', 'line-height': '420px'}),
                             style={'width': '50%', 'height': '420px', 'order': '1'}),
                    html.Div(dcc.Loading(id='Point-spectrum-L',
                                         children=dcc.Graph(id={'type': 'graph', 'index': 'x-any-y-brdf'}, responsive=True),
                                         style={'height': '420px', 'line-height': '1000px'}),
                             style={'width': '50%', 'height': '420px', 'order': '2'}),
                    html.Div(dcc.Loading(id='Projection-plot-L',
                                         children=dcc.Graph(id={'type': 'graph', 'index': 'projection'}, responsive=True),
                                         style={'height': '420px', 'line-height': '420px'}),
                             style={'width': '50%', 'height': '420px', 'order': '3'}),
                    html.Div(dcc.Loading(id='2D-BRDF-L',
                                         children=dcc.Graph(id={'type': 'graph', 'index': '2d-brdf'}, responsive=True),
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
                    style={'display': 'flex', 'flex-wrap': 'wrap'})
            ]
        ), tab, 'Triggered'

@app.callback(Output({'type': 'trigger', 'index': 'mode-brdf-tab'}, 'data'),
              [Input({'type': 'trigger', 'index': 'app-modes'}, 'data')],
              [State({'type': 'applet-modes', 'index': 0}, 'value')])
def mode_BRDF_tab_selected_trigger(trigger, tab):
    if tab != 'BRDF':
        raise PreventUpdate
    else:
        return 'Triggered'

@app.callback([Output({'type': 'memory', 'index': 'browser_data_storage'}, 'data'),
               Output({'type': 'file-loading', 'index': 0}, 'children'),
               Output({'type': 'trigger', 'index': 'upload-data'}, 'data')],
              [Input({'type': 'upload-data', 'index': 0}, 'filename'),
               Input({'type': 'upload-data', 'index': 0}, 'contents')],
              [State({'type': 'file-loading', 'index': 0}, 'children'),
               State({'type': 'memory', 'index': 'browser_data_storage'}, 'data')])
def upload_data(filenames, contents, upload_children, data):

    if contents is None or filenames is None:
        raise PreventUpdate

    if data == {}:
        for i in range(len(filenames)):
            filename = filenames[i]
            content = contents[i]
            content_type, content_string = content.split(',')
            decoded = base64.b64decode(content_string)
            processed_data = copy.deepcopy(parse_brdf_json(json.loads(decoded.decode('utf-8'))))
            data[filename] = processed_data
            # data[filename]["data"]["variables"].append({"observer": 'CIE 1931 2 Degree Standard Observer'})
            # data[filename]["data"]["variables"].append({"illuminant": 'D65'})
    else:
        for i in range(len(filenames)):
            filename = filenames[i]
            content = contents[i]
            content_type, content_string = content.split(',')
            decoded = base64.b64decode(content_string)
            processed_data = copy.deepcopy(parse_brdf_json(json.loads(decoded.decode('utf-8'))))
            if filename in data:
                i = 1
                new_filename = filename
                while new_filename in data:
                    new_filename = filename + '_copy_' + str(i)
                    i = i + 1
                filename = new_filename
            data[filename] = processed_data
            # data[filename]["data"]["variables"].append({"observer": 'CIE 1931 2 Degree Standard Observer'})
            # data[filename]["data"]["variables"].append({"illuminant": 'D65'})
    print('upload')
    return data, upload_children, 'Triggered'

@app.callback([Output({'type': 'upload-data', 'index': 0}, 'filename'),
               Output({'type': 'upload-data', 'index': 0}, 'contents')],
              [Input({'type': 'trigger', 'index': 'upload-data'}, 'data')])
def clear_upload_component(trigger):
    print('upload cleared')
    return None, None

@app.callback([Output({'type': 'validator-information-container', 'index': 0}, 'children'),
               Output({'type': 'file-loading', 'index': 1}, 'children'),
               Output({'type': 'trigger', 'index': 'validator-upload-data'}, 'data')],
              [Input({'type': 'upload-data', 'index': 1}, 'filename'),
               Input({'type': 'upload-data', 'index': 1}, 'contents')],
              [State({'type': 'file-loading', 'index': 1}, 'children')])
def validator_upload_data(filenames, contents, upload_children):

    if contents is None or filenames is None:
        raise PreventUpdate

    children = []
    for i in range(len(filenames)):
        filename = filenames[i]
        content = contents[i]
        content_type, content_string = content.split(',')
        decoded = base64.b64decode(content_string)
        file_data = json.loads(decoded.decode('utf-8'))
        validity = str(validate_brdf_json(file_data, dict_from_json_schema))
        if validity == "File valid!":
            children.append(
                html.Div(children=[
                    html.P(filename, style={'width': '75%', 'font-size': '20px', 'textAlign': 'center', 'vertical-align': 'middle', 'margin-bottom': '2.5px', 'margin-top': '2.5px'}),
                    html.P("File valid!", style={'width': '25%', 'font-size': '24px', 'color':'green', 'textAlign': 'center', 'vertical-align': 'middle', 'margin-bottom': '2.5px', 'margin-top': '2.5px'}),
                    # html.P("",
                    #        style={'width': '20%', 'font-size': '20px', 'color': 'black', 'textAlign': 'center',
                    #               'vertical-align': 'middle', 'margin-bottom': '2.5px', 'margin-top': '2.5px'}),
                ],
                style={'display': 'flex', 'flex-direction': 'row', 'flex-wrap': 'nowrap',
                       'height': '45px', 'lineHeight': '45px', 'align-items': 'center',
                       'borderWidth': '1px', 'borderStyle': 'solid', 'borderRadius': '7.5px',
                       'margin-bottom': '2.5px', 'margin-top': '2.5px',
                       'borderColor': 'Green',  'background-color':'PaleGreen'}
                )
            )
        else:
            children.append(
                html.Div(children=[
                    html.P(filename,
                           style={'width': '75%', 'font-size': '20px', 'textAlign': 'center', 'vertical-align': 'middle', 'margin-bottom': '2.5px', 'margin-top': '2.5px'}),
                    html.P("File not valid!",
                           style={'width': '20%', 'font-size': '24px', 'textAlign': 'center', 'color':'red',
                                  'vertical-align': 'middle', 'margin-bottom': '2.5px', 'margin-top': '2.5px'}),
                    html.Button(u"\u2193", id={'type':'show-validator-error-message', 'index':filename},
                                style={'width': '5%', 'font-size': '20px', 'textAlign': 'center', 'vertical-align': 'middle', 'margin-bottom': '2.5px', 'margin-top': '2.5px',
                                       # 'box-shadow': '0 8px 16px 0 rgba(0,0,0,0.2), 0 6px 20px 0 rgba(0,0,0,0.19)',
                                       'background-color':'GhostWhite', 'borderWidth': '2px', 'borderColor': 'Grey', 'margin-left': '5px', 'margin-right': '5px', 'text-align': 'center'})
                ],
                style={'display': 'flex', 'flex-direction': 'row', 'flex-wrap': 'nowrap',
                       'height': '45px', 'lineHeight': '45px', 'align-items': 'center',
                       'borderWidth': '1px', 'borderStyle': 'solid', 'borderRadius': '7.5px',
                       'textAlign': 'center', 'margin-bottom': '2.5px', 'margin-top': '2.5px',
                       'borderColor': 'red',  'background-color':'LightPink',
                       }
                )
            )
            print(validity)
            children.append(
                html.Div(
                    children=[
                        html.P(str(validity), id={'type':'validator-error-message', 'index': filename},
                               style={'display': 'none', 'whiteSpace': 'pre-wrap', 'borderWidth': '1px', 'borderStyle': 'solid',
                                      'borderRadius': '7.5px', 'margin-bottom': '2.5px', 'margin-top': '2.5px', 'padding': '5px 5px',
                                      'borderColor': 'Grey'}
                               ),
                    ])
            )

    print('upload')
    return children, upload_children, 'Triggered'

@app.callback([Output({'type': 'upload-data', 'index': 1}, 'filename'),
               Output({'type': 'upload-data', 'index': 1}, 'contents')],
              [Input({'type': 'trigger', 'index': 'validator-upload-data'}, 'data')])
def clear_validator_upload_component(trigger):
    print('validator upload cleared')
    return None, None

@app.callback(Output({'type':'validator-error-message', 'index':MATCH}, 'style'),
              [Input({'type':'show-validator-error-message', 'index':MATCH}, 'n_clicks')],
              [State({'type':'validator-error-message', 'index':MATCH}, 'style')])
def show_validator_error_message(n_clsicks, style):
    if n_clsicks is None:
        raise PreventUpdate
    if n_clsicks % 2 != 0:
        style['display'] = 'block'
    else:
        style['display'] = 'none'
    return style

@app.callback([Output({'type': 'memory', 'index': 'selected_file'},'data'),
               Output({'type': 'file-menu-container', 'index': 0},'children'),
               Output({'type': 'trigger', 'index': 'update-menu'}, 'data')],
              [Input({'type': 'trigger', 'index': 'upload-data'}, 'data'),
               Input({'type': 'trigger', 'index': 'applet-tab'}, 'data'),
               Input({'type': 'options_sp', 'index': 'file-names-dropdown'}, 'value'),
               Input({'type': 'file-navigator-tabs', 'index': 0}, 'value')],
              [State({'type': 'memory', 'index': 'browser_data_storage'}, 'data'),
               State({'type': 'memory', 'index': 'selected_file'}, 'data'),
               State({'type': 'memory', 'index': 'snaped-states'}, 'data')])
def update_menu(trigger_upload, trigger_menu_tabs, file_name, file_navigator_state, uploaded_data, previously_selected_file, snaped_states):

    if uploaded_data == {}:
        raise PreventUpdate
    if previously_selected_file == '':
        previously_selected_file = list(uploaded_data.keys())[0]
    if file_name is None or file_name == 'no files':
        file_name = previously_selected_file

    file_menu_container_children = []

    # Create and update file selector dropdown first
    file_selection_options = []
    for key in uploaded_data:
        file_selection_options.append({'label': key, 'value': key})

    file_menu_container_children.append(
        html.P(children='Uploaded files',
               style={'textAlign': 'center', 'font-size': '20px',
                      'line-height': '50px', 'padding': '0', 'height': '50px', 'borderWidth': '1px',
                      'borderStyle': 'solid', 'borderRadius': '5px',
                      'borderColor': 'LightGrey', 'background-color': '#f9f9f9'})
    )
    file_menu_container_children.append(
        html.P('Select file:', style={'margin-bottom': '2.5px', 'margin-top': '2.5px'})
    )
    file_menu_container_children.append(
        dcc.Dropdown(id={'type': 'options_sp', 'index': 'file-names-dropdown'},
                     placeholder="File name",
                     options=file_selection_options,
                     value=file_name,
                     clearable=False,
                     style={'margin-bottom': '2.5px', 'margin-top': '2.5px'})
    )
    if uploaded_data[file_name]['validity'] is False:
        file_menu_container_children.append(
            html.P('Some file(s) are not in valid BRDF format. Use validator to check the problem.', style={'margin-bottom': '2.5px', 'margin-top': '2.5px', 'color': 'red'})
        )
    file_menu_container_children.append(
        html.Hr(style={'margin-bottom': '5px', 'margin-top': '5px'})
    )
    previously_selected_file = file_name

    file_menu_container_children.append(
        dcc.Tabs(id={'type': 'file-navigator-tabs', 'index': 0}, value=file_navigator_state, children=[
            dcc.Tab(id={'type': 'file-navigator-tab', 'index': 'options'}, label='Options', value='options',
                    style={'line-height': '35px', 'padding': '0', 'height': '35px'},
                    selected_style={'line-height': '35px', 'padding': '0', 'height': '35px'}
                    ),
            dcc.Tab(id={'type': 'file-navigator-tab', 'index': 'metadata'}, label='Metadata', value='metadata',
                    style={'line-height': '35px', 'padding': '0', 'height': '35px'},
                    selected_style={'line-height': '35px', 'padding': '0', 'height': '35px'}
                    ), ],
                 style={'width': '100%', 'height': '35px', 'line-height': '35px',
                        'textAlign': 'top', 'margin-bottom': '2.5px', 'margin-top': '2.5px'}),
    )

    if file_navigator_state == 'options':
        file_menu_container_children.append(
            html.Hr(style={'margin-bottom': '5px', 'margin-top': '5px'})
        )

        # Create and update options from variables in uploaded data
        variables_to_options = {}
        for variable in uploaded_data[file_name]['data']:
            if variable != 'BRDF' and variable != "uBRDF" and variable != "adhoc_variables":
                variables_to_options[variable] = {
                    'options': [{'label': uval, 'value': uval} for uval in uploaded_data[file_name]['data'][variable]['uvals']],
                    'value': uploaded_data[file_name]['data'][variable]['sval']
                }

        file_menu_container_children.append(
            html.P(children='Main variables',
                   style={'textAlign': 'center', 'font-size': '20px',
                          'line-height': '35px', 'padding': '0', 'height': '35px', 'borderWidth': '1px',
                          'borderStyle': 'solid', 'borderRadius': '5px',
                          'borderColor': 'LightGrey', 'background-color': '#f9f9f9',
                          'margin-bottom': '2.5px', 'margin-top': '2.5px'})
        )
        file_menu_container_children.append(
            html.P('Select Theta_i:', style={'margin-bottom': '2.5px', 'margin-top': '2.5px'}),
        )
        file_menu_container_children.append(
            dcc.Dropdown(id={'type': 'options', 'index': "theta_i"},
                         placeholder="theta_i",
                         options=variables_to_options['theta_i']['options'],
                         value=variables_to_options['theta_i']['value'],
                         clearable=False,
                         style={'margin-bottom': '2.5px', 'margin-top': '2.5px'})
        )
        file_menu_container_children.append(
            html.P('Select Phi_i:', style={'margin-bottom': '2.5px', 'margin-top': '2.5px'}),
        )
        file_menu_container_children.append(
            dcc.Dropdown(id={'type': 'options', 'index': "phi_i"},
                         placeholder="phi_i",
                         options=variables_to_options['phi_i']['options'],
                         value=variables_to_options['phi_i']['value'],
                         clearable=False,
                         style={'margin-bottom': '2.5px', 'margin-top': '2.5px'})
        )
        file_menu_container_children.append(
            html.P('Select Theta_r:', style={'margin-bottom': '2.5px', 'margin-top': '2.5px'}),
        )
        file_menu_container_children.append(
            dcc.Dropdown(id={'type': 'options', 'index': "theta_r"},
                         placeholder="theta_r",
                         options=variables_to_options['theta_r']['options'],
                         value=variables_to_options['theta_r']['value'],
                         clearable=False,
                         style={'margin-bottom': '2.5px', 'margin-top': '2.5px'})
        )
        file_menu_container_children.append(
            html.P('Select Phi_r:', style={'margin-bottom': '2.5px', 'margin-top': '2.5px'}),
        )
        file_menu_container_children.append(
            dcc.Dropdown(id={'type': 'options', 'index': "phi_r"},
                         placeholder="phi_r",
                         options=variables_to_options['phi_r']['options'],
                         value=variables_to_options['phi_r']['value'],
                         clearable=False,
                         style={'margin-bottom': '2.5px', 'margin-top': '2.5px'})
        )
        file_menu_container_children.append(
            html.Hr(style={'margin-bottom': '5px', 'margin-top': '5px'})
        )
        file_menu_container_children.append(
            html.P(children='Additional variables',
                   style={'textAlign': 'center', 'font-size': '20px',
                          'line-height': '35px', 'padding': '0', 'height': '35px', 'borderWidth': '1px',
                          'borderStyle': 'solid', 'borderRadius': '5px', 'width': '99.25%',
                          'borderColor': 'LightGrey', 'background-color': '#f9f9f9',
                          'margin-bottom': '2.5px', 'margin-top': '2.5px'})
        )
        if len(variables_to_options.keys()) > 4:
            for variable_key in variables_to_options:
                if variable_key != 'theta_i' and variable_key != 'phi_i' and variable_key != 'theta_r' and variable_key != 'phi_r' and variable_key != 'adhoc_variables':
                    file_menu_container_children.append(
                        html.P('Select ' + variable_key + ':', style={'margin-bottom': '2.5px', 'margin-top': '2.5px'}),
                    )
                    file_menu_container_children.append(
                        dcc.Dropdown(id={'type': 'options', 'index': variable_key},
                                     placeholder=variable_key,
                                     options=variables_to_options[variable_key]['options'],
                                     value=variables_to_options[variable_key]['value'],
                                     clearable=False,
                                     style={'margin-bottom': '2.5px', 'margin-top': '2.5px'})
                    )
        else:
            file_menu_container_children.append(
                html.P('No additional variables',
                       style={'margin-bottom': '2.5px', 'margin-top': '2.5px', 'line-height': '35px', 'padding': '0',
                              'height': '35px', 'borderWidth': '1px', 'borderStyle': 'dashed', 'borderRadius': '5px',
                              'borderColor': 'LightGrey'}),
            )
        file_menu_container_children.append(
            html.Hr(style={'margin-bottom': '5px', 'margin-top': '5px'})
        )
        file_menu_container_children.append(
            html.P(children='Select variable as \"X\"',
                   style={'textAlign': 'center', 'font-size': '20px',
                          'line-height': '35px', 'padding': '0', 'height': '35px', 'borderWidth': '1px',
                          'borderStyle': 'solid', 'borderRadius': '5px', 'width': '99.25%',
                          'borderColor': 'LightGrey', 'background-color': '#f9f9f9',
                          'margin-bottom': '5px', 'margin-top': '2.5px'})
        )
        variable_as_x_options = []
        for key in variables_to_options:
            variable_as_x_options.append({'label': key, 'value': key})
        variable_as_x_value = ''
        if 'variable_as_x' in uploaded_data[file_name]:
            variable_as_x_value = uploaded_data[file_name]['variable_as_x']
        else:
            variable_as_x_value = variable_as_x_options[len(variable_as_x_options) - 1]['value']
        file_menu_container_children.append(
            dcc.Dropdown(id={'type': 'options', 'index': 'variable_as_x'},
                         placeholder='variable_as_x',
                         options=variable_as_x_options,
                         value=variable_as_x_value,
                         clearable=False,
                         style={'margin-bottom': '2.5px', 'margin-top': '2.5px'})
        )
        file_menu_container_children.append(
            html.Hr(style={'margin-bottom': '5px', 'margin-top': '5px'})
        )
        file_menu_container_children.append(
            html.Button('Snap state',
                        id={'type': 'button', 'index': 'snap_state'},
                        style={'margin-bottom': '2.5px', 'margin-top': '2.5px', 'width': '100%'})
        )
        snaped_states_children = [] #needs to be checked
        for file_name in snaped_states:
            snaped_states_children.append(
                html.P(file_name+':',
                       style={'text-align': 'left'})
            )
            for selected_X in snaped_states[file_name]:
                snaped_states_children.append(
                    html.P(selected_X + ':',
                           style={'text-align': 'left','margin-left':'20px'})
                )
                for state in snaped_states[file_name][selected_X]:
                    snaped_states_children.append(html.Div(children=[
                        html.P(str(state),
                               style={'text-align': 'left', 'width': '70%'}),
                        html.Button('X',
                                    id={'type': 'snap-remove-button',
                                        'index': str(file_name) + '::' + str(selected_X) + '::' + str(state)},
                                    style={'margin-bottom': '2.5px', 'margin-top': '2.5px','width': '30%'})],
                        style={'margin-left': '40px','display': 'flex'}
                    ))
        file_menu_container_children.append(
            html.Div(children = snaped_states_children,
                     id={'type': 'container', 'index': 'snap_states'},
                     style={'margin-bottom': '2.5px', 'margin-top': '2.5px',
                            'overflow': 'auto', 'height': '500px',
                            'borderWidth': '1px', 'borderStyle': 'dashed',
                            'borderRadius': '5px', 'borderColor': 'LightGrey'
                            })
        )
    elif file_navigator_state == 'metadata':
        metadata = uploaded_data[file_name]['metadata']
        metadata_children = []
        for key in metadata:
            if isinstance(metadata[key], dict):
                metadata_children.append(html.P(key + ': ' + '\n'))
                for subkey in metadata[key]:
                    metadata_children.append(html.P(subkey + ': ' + str(metadata[key][subkey]) + '\n', style={'margin-left':'20px'}))
            else:
                metadata_children.append(html.P(key + ': ' + str(metadata[key]) + '\n'))

        file_menu_container_children.append(
            html.P(metadata_children,
                   style={'margin-bottom': '2.5px', 'margin-top': '2.5px',
                          'whiteSpace': 'pre-wrap', 'overflow': 'auto',
                          'text-align': 'left', 'height': '1150px',
                          # 'line-height': '35px', 'padding': '0', 'height': '35px',
                          'borderWidth': '1px', 'borderStyle': 'dashed',
                          'borderRadius': '5px', 'borderColor': 'LightGrey'}),
        )


    return previously_selected_file, file_menu_container_children, 'Triggered'

@app.callback([Output({'type': 'memory', 'index': 'snaped-states'}, 'data'),
               Output({'type': 'container', 'index': 'snap_states'}, 'children'),
               Output({'type': 'trigger', 'index': 'change-snap-states'}, 'data')],
              [Input({'type': 'button', 'index': 'snap_state'}, 'n_clicks'),
               Input({'type': 'snap-remove-button', 'index': ALL}, 'n_clicks')],
              [State({'type': 'memory', 'index': 'selected_file'}, 'data'),
               State({'type': 'memory', 'index': 'snaped-states'}, 'data'),
               State({'type': 'options', 'index': ALL}, 'value'),
               State({'type': 'options', 'index': ALL}, 'id')])
def take_state_snap(n_clicks, remove_clicks, file_name, snaped_states, options, ids):
    print(remove_clicks)
    if file_name == '':
        raise PreventUpdate

    # print(dash.callback_context.triggered)

    if 1 in remove_clicks:
        remove_button = json.loads(dash.callback_context.triggered[0]['prop_id'].split('.n_clicks')[0])
        remove_button = remove_button['index'].split('::')
        remove_button_file_name = remove_button[0]
        remove_button_selected_x = remove_button[1]
        remove_button_selected_state = json.loads(remove_button[2].replace("'", "\""))
        snaped_states[remove_button_file_name][remove_button_selected_x].remove(remove_button_selected_state)
        if snaped_states[remove_button_file_name][remove_button_selected_x] == []:
            del snaped_states[remove_button_file_name][remove_button_selected_x]
        if snaped_states[remove_button_file_name] == {}:
            del snaped_states[remove_button_file_name]
    else:
        if n_clicks != None:
            id_keys = []
            for id in ids:
                id_keys.append(id['index'])
            options_under_key = {}
            for i in range(len(options)):
                options_under_key[id_keys[i]] = options[i]
            i = len(options) - 1
            variable_as_x = options[i]
            if file_name not in snaped_states:
                variable_as_x_states = []
                variable_as_x_states.append(options_under_key)
                snaped_states[file_name] = {variable_as_x: variable_as_x_states}
            else:
                if variable_as_x not in snaped_states[file_name]:
                    variable_as_x_states = []
                    variable_as_x_states.append(options_under_key)
                    snaped_states[file_name][variable_as_x] = variable_as_x_states
                else:
                    if options_under_key not in snaped_states[file_name][variable_as_x]:
                        snaped_states[file_name][variable_as_x].append(options_under_key)

    snaped_states_children = []
    for file_name in snaped_states:
        snaped_states_children.append(
            html.P(file_name + ':',
                   style={'text-align': 'left'})
        )
        for selected_X in snaped_states[file_name]:
            snaped_states_children.append(
                html.P(selected_X + ':',
                       style={'text-align': 'left', 'margin-left': '20px'})
            )
            for state in snaped_states[file_name][selected_X]:
                snaped_states_children.append(html.Div(children=[
                    html.P(str(state),
                           style={'text-align': 'left', 'width': '70%'}),
                    html.Button('X',
                                id={'type': 'snap-remove-button',
                                    'index': str(file_name) + '::' + str(selected_X) + '::' + str(state)},
                                style={'margin-bottom': '2.5px', 'margin-top': '2.5px', 'width': '30%'})],
                    style={'margin-left': '40px', 'display': 'flex'}
                ))

    return snaped_states, snaped_states_children, 'Triggered'

@app.callback([Output({'type': 'memory', 'index': 'previous_state'}, 'data'),
               Output({'type': 'memory', 'index': 'browser_data_storage_update'}, 'children'),
               Output({'type': 'trigger', 'index': 'modify-state'}, 'data')],
              [Input({'type': 'trigger', 'index': 'update-menu'}, 'data'),
               Input({'type': 'options', 'index': ALL}, 'value')],
              [State({'type': 'memory', 'index': 'browser_data_storage'}, 'data'),
               State({'type': 'memory', 'index': 'previous_state'}, 'data'),
               State({'type': 'memory', 'index': 'selected_file'}, 'data')])
def modify_state(trigger, options_values, uploaded_data, previous_state, selected_file):

    if options_values == [] or uploaded_data == {}:
        raise PreventUpdate

    new_state = {'name': selected_file}
    inputs = dash.callback_context.inputs_list
    for input in inputs[1]:
        key = input['id']['index']
        new_state[key] = input['value']
    # print(new_state)
    if new_state == previous_state:
        raise PreventUpdate

    # print(previous_state)
    previous_state = new_state
    # print(previous_state)

    inputs = dash.callback_context.inputs_list
    for input in inputs[1]:
        key = input['id']['index']
        for variable in uploaded_data[selected_file]['data']:
            if key == variable:
                uploaded_data[selected_file]['data'][variable]['sval'] = input['value']
        if key == 'variable_as_x':
            uploaded_data[selected_file][key] = input['value']

    return previous_state, dcc.Store(id={'type': 'memory', 'index': 'browser_data_storage'}, storage_type='memory', data=uploaded_data), 'Triggered'

@app.callback([Output({'type': 'memory', 'index': '3d-plot-previous-state'}, 'data'),
               Output({'type': 'trigger', 'index': 'for-3d-plot'}, 'data')],
              [Input({'type': 'trigger', 'index': 'modify-state'}, 'data')],
              [State({'type': 'memory', 'index': '3d-plot-previous-state'}, 'data'),
               State({'type': 'memory', 'index': 'previous_state'}, 'data'),
               State({'type': 'memory', 'index': 'selected_file'}, 'data')])
def trigger_3D_plot(trigger, plot_previous_state, previous_state, filename):
    if filename == '':
        raise PreventUpdate

    plot_new_state = {}
    for key in previous_state:
        if key != 'theta_r' and key != 'phi_r' and key != 'variable_as_x':
            plot_new_state[key] = previous_state[key]
    if plot_new_state == plot_previous_state:
        raise PreventUpdate
    else:
        plot_previous_state = plot_new_state
    return plot_previous_state, 'Triggered'

@app.callback(Output({'type': 'graph', 'index': '3d-brdf'}, 'figure'),
              [Input({'type': 'trigger', 'index': 'for-3d-plot'}, 'data'),
               Input({'type': 'trigger', 'index': 'mode-brdf-tab'}, 'data')],
              [State({'type': 'memory', 'index': 'browser_data_storage'}, 'data'),
               State({'type': 'memory', 'index': 'selected_file'}, 'data')])
def update_3D_plot(trigger1, trigger2, uploaded_data, filename):
    if uploaded_data == {} or filename == '':
        raise PreventUpdate
    # print(time.process_time())
    degree_sign = u"\N{DEGREE SIGN}"

    data = uploaded_data[filename]['data']

    mask = np.array([])
    brdf = np.array([])
    ubrdf = np.array([])
    theta_r = np.array([])
    phi_r = np.array([])
    for variable in data:
        if variable != 'BRDF' and variable != 'uBRDF' and variable != 'theta_r' and variable != 'phi_r'  and variable != 'adhoc_variables':
            if mask.size == 0:
                mask = np.array(data[variable]['values']) == data[variable]['sval']
            else:
                mask = np.logical_and(mask, np.array(data[variable]['values']) == data[variable]['sval'])
        else:
            if variable == 'BRDF':
                brdf = np.array(data[variable]['values'])
            if variable == 'uBRDF':
                ubrdf = np.array(data[variable]['values'])
            if variable == 'theta_r':
                theta_r = np.array(data[variable]['values'])
            if variable == 'phi_r':
                phi_r = np.array(data[variable]['values'])
    brdf = brdf[mask]
    # ubrdf = ubrdf[mask]
    theta_r = theta_r[mask]
    phi_r = phi_r[mask]

    theta = theta_r
    phi = phi_r
    brdf = brdf

    figure = []
    #tristimulus_values, RGB_values = get_tristimulus_XYZs(thI, phiI, pol, data, observer, illuminant)
    #RGB_values = np.array(RGB_values).reshape((theta.shape[1]*phi.shape[1]),3)

    X = theta.T*np.cos(np.radians(phi))
    Y = theta.T*np.sin(np.radians(phi))
    Z = brdf
    # print(time.process_time())
    # X_sc = np.transpose(X).reshape((theta.shape[1]*phi.shape[1]))
    # Y_sc = np.transpose(Y).reshape((theta.shape[1]*phi.shape[1]))
    # Z_sc = np.transpose(Z).reshape((theta.shape[1]*phi.shape[1]))
    X_sc = X
    Y_sc = Y
    Z_sc = Z

    label_data = []
    for i in range(phi.shape[0]):
        label_data.append(
            'BRDF value: {:.4f}, Theta: {:.2f}, Phi: {:.2f}'.format(Z[i], theta[i], phi[i]))

    label_data = np.array(label_data)
    # label_data = label_data.reshape((theta.shape[1] * phi.shape[1]))
    label_data = label_data[Z_sc >= 0]

    # X_sc[Z_sc < 0] = None
    # Y_sc[Z_sc < 0] = None
    # Z_sc[Z_sc < 0] = None

    zmin = np.min(Z_sc[Z_sc>=0])
    zmax = np.max(Z_sc[Z_sc>=0])
    theta_span = 20+np.max(np.abs(theta[0]))
    offset = 0.1*zmin
    if zmax-zmin != 0:
        if zmin-(zmax-zmin)/5 < 0:
            offset = zmin
        else:
            offset = (zmax - zmin) / 5
    # print(time.process_time())
    x_scale = []
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
    for i in range(phi.shape[0]):
        x_scale.append(0)
        y_scale.append(0)
        x_scale.append(theta_span*np.cos(np.radians(phi[i])))
        y_scale.append(theta_span*np.sin(np.radians(phi[i])))
        x_scale.append(-theta_span*np.cos(np.radians(phi[i])))
        y_scale.append(-theta_span*np.sin(np.radians(phi[i])))
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
                               opacity=0.2,
                               mode='lines',
                               line=dict(color='black', width=3),
                               #marker=dict(color='black', size=2),
                               hoverinfo='skip'))

    x_scale_vals = []
    y_scale_vals = []
    text = []
    text_positions =[]
    x_scale_vals.append(theta_span * np.cos(np.radians(0)))
    y_scale_vals.append(theta_span * np.sin(np.radians(0)))
    x_scale_vals.append(-theta_span * np.cos(np.radians(0)))
    y_scale_vals.append(-theta_span * np.sin(np.radians(0)))
    text.append('{:.0f}'.format(0)+degree_sign)
    text_positions.append('bottom center')
    text.append('{:.0f}'.format(180)+degree_sign)
    text_positions.append('top center')
    x_scale_vals.append(theta_span * np.cos(np.radians(90)))
    y_scale_vals.append(theta_span * np.sin(np.radians(90)))
    x_scale_vals.append(-theta_span * np.cos(np.radians(90)))
    y_scale_vals.append(-theta_span * np.sin(np.radians(90)))
    text.append('{:.0f}'.format(90)+degree_sign)
    text_positions.append('middle right')
    text.append('{:.0f}'.format(270)+degree_sign)
    text_positions.append('middle left')
    for i in range(phi.shape[0]):
        x_scale_vals.append(theta_span*np.cos(np.radians(phi[i])))
        y_scale_vals.append(theta_span*np.sin(np.radians(phi[i])))
        x_scale_vals.append(-theta_span*np.cos(np.radians(phi[i])))
        y_scale_vals.append(-theta_span*np.sin(np.radians(phi[i])))
        if phi[i] <= 180:
            text.append('{:.0f}'.format(phi[i])+degree_sign)
            if phi[i] >= 0 and phi[i] < 90:
                text_positions.append('bottom center')
            elif phi[i] > 90 and phi[i] < 180:
                text_positions.append('top center')
            elif phi[i] == 90:
                text_positions.append('middle right')
            elif phi[i] == 180:
                text_positions.append('top center')
            else:
                text_positions.append('bottom center')
        if phi[i] != 0 and phi[i] < 180:
            text.append('{:.0f}'.format(phi[i]+180)+degree_sign)
            if phi[i] > 0 and phi[i] < 90:
                text_positions.append('top center')
            elif phi[i] > 90 and phi[i] < 180:
                text_positions.append('bottom center')
            elif phi[i] == 90:
                text_positions.append('middle left')
            else:
                text_positions.append('bottom center')
        else:
            text.append('')
            text_positions.append('bottom center')
    for i in range(np.abs(len(x_scale_vals)-len(text))):
        text.append('')
        text_positions.append('bottom center')
    last_i = 0
    for i in range(0,100,20):
        if i <= np.max(np.abs(theta[0])):
            x_scale_vals.append(0)
            y_scale_vals.append(i)
            text.append('{:.0f}'.format(i)+degree_sign)
            text_positions.append('bottom center')
            last_i = i
        else:
            if last_i != -1:
                x_scale_vals.append(0)
                y_scale_vals.append(last_i+10)
                text.append('{:.0f}'.format(i)+degree_sign)
                text_positions.append('bottom center')
                last_i = -1
    z_scale_vals = np.full((1, len(x_scale_vals)), zmin-offset).tolist()[0]

    figure.append(go.Scatter3d(x=x_scale_vals,
                               y=y_scale_vals,
                               z=z_scale_vals,
                               opacity=1.0,
                               mode='markers+text',
                               #line=dict(color='black', width=2),
                               marker=dict(color='black', size=3),
                               text=text,
                               textposition=text_positions,
                               textfont_size=14,
                               hoverinfo='skip'))

    hight_points = range(6)

    # figure.append(go.Scatter3d(
    #                            # x=np.full((1,len(hight_points)+1),-theta_span).tolist()[0],
    #                            # y=np.full((1,len(hight_points)+1),0).tolist()[0],
    #                            # z=[zmin-offset]+[zmin + i * (zmax - zmin) / 5 for i in hight_points],
    #                            # text=['{:.4f}'.format(zmin-offset)]+['{:.4f}'.format(zmin + i * (zmax - zmin) / 5) for i in hight_points],
    #                            x=np.full((1,len(hight_points)),-theta_span).tolist()[0],
    #                            y=np.full((1,len(hight_points)),0).tolist()[0],
    #                            z=[zmin + i * (zmax - zmin) / 5 for i in hight_points],
    #                            text=['{:.4f}'.format(zmin + i * (zmax - zmin) / 5) for i in hight_points],
    #                            textposition="middle right",
    #                            textfont_size=10,
    #                            mode='lines+markers+text',
    #                            line=dict(color='black', width=2),
    #                            marker=dict(color='black', size=2),
    #                            hoverinfo='skip'))

    colorscale_range = range(11)

    Z_sc[Z_sc < 0] = None

    figure.append(go.Mesh3d(x=X_sc, y=Y_sc, z=Z_sc,
                             color='grey',
                             opacity=1.0,
                             intensity=Z_sc,
                             colorscale='Portland',
                             hoverinfo='skip',
                             hovertext=label_data,
                             cmin=zmin,
                             cmax=zmax,
                             colorbar = dict(tickvals=[zmin + i * (zmax - zmin) / 10 for i in colorscale_range],
                                             ticktext=['{:.4f}'.format(zmin + i * (zmax - zmin) / 10) for i in colorscale_range],
                                             len=1)
                             )
                  )

    figure.append(go.Scatter3d(x=X_sc, y=Y_sc, z=Z_sc,
                               opacity=1.0,
                               mode='markers',
                               hoverinfo='text',
                               hovertext=label_data,
                               marker=dict(color='black',#Z_sc,
                                           size=2,
                                           cmin=zmin,
                                           cmax=zmax,
                                           colorscale='Portland')
                               ))
    # print(time.process_time())

    # figure.update_layout
    # camera = dict(
    #     eye=dict(x=0.000001, y=0., z=2.5)
    # )
    layout = go.Layout(title="3D BRDF plot for chosen parameters",
                       title_yanchor='top',
                       # font=dict(size=18),
                       scene=dict(
                           xaxis_title="Theta (deg)",
                           yaxis_title="Theta (deg)",
                           zaxis_title="BRDF"),
                       # scene_camera=camera,
                       scene_xaxis_visible=False,
                       scene_yaxis_visible=False,
                       scene_zaxis_visible=False,
                       scene_aspectmode='manual',
                       scene_aspectratio=dict(x=2, y=2, z=1),
                       showlegend=False,
                       scene_camera_projection_type = "orthographic",
                       height=1000,
                       width=1000
                       )
    # print(time.process_time())
    # print({'data': figure, 'layout': layout})
    return {'data': figure, 'layout': layout}

@app.callback([Output({'type': 'memory', 'index': 'projection-plot-previous-state'}, 'data'),
               Output({'type': 'trigger', 'index': 'for-projection-plot'}, 'data')],
              [Input({'type': 'trigger', 'index': 'modify-state'}, 'data')],
              [State({'type': 'memory', 'index': 'projection-plot-previous-state'}, 'data'),
               State({'type': 'memory', 'index': 'previous_state'}, 'data'),
               State({'type': 'memory', 'index': 'selected_file'}, 'data'),
               State({'type': 'memory', 'index': 'projection-bezel-turned'}, 'data'),
               State({'type': 'memory', 'index': 'projection-bezel-previous-state'}, 'data')])
def trigger_projection_plot(trigger, plot_previous_state, previous_state, filename, bezel, previous_bezel):
    if filename == '':
        raise PreventUpdate

    plot_new_state = {}
    for key in previous_state:
        if key != 'theta_r' and key != 'variable_as_x':
            plot_new_state[key] = previous_state[key]
    if plot_new_state == plot_previous_state:
        raise PreventUpdate
    else:
        plot_previous_state = plot_new_state

    # print('here')
    new_bezel = bezel
    if new_bezel > previous_bezel:
        raise PreventUpdate
    # print('now here')

    return plot_previous_state, 'Triggered'


@app.callback(Output({'type': 'graph', 'index': 'projection'}, 'figure'),
              [Input({'type': 'trigger', 'index': 'for-projection-plot'}, 'data'),
               Input({'type': 'trigger', 'index': 'mode-brdf-tab'}, 'data')],
              [State({'type': 'memory', 'index': 'browser_data_storage'}, 'data'),
               State({'type': 'memory', 'index': 'selected_file'}, 'data')])
def update_projection_plot(trigger1, trigger2, uploaded_data, filename):
    if trigger1 is None or uploaded_data == {} or filename == '':
        raise PreventUpdate

    data = uploaded_data[filename]['data']

    mask = np.array([])
    brdf = np.array([])
    ubrdf = np.array([])
    theta_r = np.array([])
    phi_r = np.array([])
    s_phi_r = 0
    for variable in data:
        if variable != 'BRDF' and variable != 'uBRDF' and variable != 'theta_r' and variable != 'phi_r':
            if mask.size == 0:
                mask = np.array(data[variable]['values']) == data[variable]['sval']
            else:
                mask = np.logical_and(mask, np.array(data[variable]['values']) == data[variable]['sval'])
        else:
            if variable == 'BRDF':
                brdf = np.array(data[variable]['values'])
            if variable == 'uBRDF':
                ubrdf = np.array(data[variable]['values'])
            if variable == 'theta_r':
                theta_r = np.array(data[variable]['values'])
            if variable == 'phi_r':
                phi_r = np.array(data[variable]['values'])
                s_phi_r = data[variable]['sval']

    brdf = brdf[mask]
    # ubrdf = ubrdf[mask]
    theta_r = theta_r[mask]
    phi_r = phi_r[mask]

    thetas = theta_r
    # arranged_thetas = np.flip(np.append(np.flip(thetas[thetas<0]),thetas[thetas>=0]))
    # print(arranged_thetas)
    phis = phi_r
    s_phi_v = s_phi_r
    z = brdf

    figure = []

    r_bp = []
    theta_bp = []
    z_bp = []
    previous_radius = 0
    for i in range(thetas.shape[0]):
        radius = np.abs(thetas[i]) #2*np.sin(np.radians(theta)/2)
        theta = thetas[i]
        phi = phis[i]
        if theta == 0:
            r_bp.append(0)
            theta_bp.append(0)
            z_bp.append(z[i])
        if theta > 0:
            r_bp.append(radius)
            theta_bp.append(phi)
            z_bp.append(z[i])
        elif theta < 0:
            r_bp.append(radius)
            theta_bp.append(180+phi)
            z_bp.append(z[i])
            previous_radius = radius

    r_bp = np.array(r_bp)
    theta_bp = np.array(theta_bp)
    z_bp = np.array(z_bp)

    # r_bp = r_bp[z_bp>=0]
    # theta_bp = theta_bp[z_bp>=0]
    # z_bp = z_bp[z_bp>=0]

    # r_bp[z_bp < 0] = None
    # theta_bp[z_bp < 0] = None
    zmax = np.max(z_bp[z_bp >= 0])
    zmin = np.min(z_bp[z_bp >= 0])
    z_bp[z_bp < 0] = None

    sorted_i = np.argsort(-r_bp)
    r_bp = r_bp[sorted_i]
    theta_bp = theta_bp[sorted_i]
    z_bp = z_bp[sorted_i]

    colorscale_range = range(11)

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
        marker_colorscale = 'Portland',
        marker_color = z_bp,
        marker_colorbar = dict(tickvals=[zmin + i * (zmax - zmin) / 10 for i in colorscale_range],
                               ticktext=['{:.4f}'.format(zmin + i * (zmax - zmin) / 10) for i in colorscale_range]),
        showlegend = False))

    layout = go.Layout(
        title="BRDF polar heatmap",
        polar_bargap=0.005,
        polar_angularaxis_rotation = -s_phi_v,
        polar_radialaxis_angle = 0,
        polar_radialaxis_ticks="outside",
    )
    # print(time.process_time())
            # if theta < 0:
            #     figure.add_trace(pgo.Barpolar(
            #     r=np.flip(np.array([2*np.cos(np.radians(theta)) for angles in thetas])),
            #     theta=180+phis))
    return {'data': figure, 'layout': layout}

@app.callback([Output({'type': 'memory', 'index': 'projection-bezel-turned'}, 'data'),
               Output({'type': 'options', 'index': 'phi_r'}, 'value')],
              [Input({'type': 'graph', 'index': 'projection'}, 'relayoutData')],
              [State({'type': 'memory', 'index': 'browser_data_storage'}, 'data'),
               State({'type': 'memory', 'index': 'selected_file'}, 'data'),
               State({'type': 'memory', 'index': 'projection-bezel-turned'}, 'data')])
def bezel_select_phi_r(relayoutData, uploaded_data, filename, bezel):
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

    data = uploaded_data[filename]['data']
    phis = []
    for variable in data:
        if variable == 'phi_r':
            phis = np.array(data[variable]['uvals'])

    selected_angle = [0]
    if 'polar.angularaxis.rotation' in relayoutData:
        angle = relayoutData['polar.angularaxis.rotation']
        # print(angle)
        if np.abs(angle) > 180:
            raise PreventUpdate
        else:
            if angle > 0:
                angle = np.abs(angle)
                d = np.abs(phis - angle)
                min_d = np.min(d)
                selected_angle = 360 - phis[d == min_d]
                if selected_angle[0] not in phis:
                    selected_angle[0] = selected_angle[0]-180
                    if 180 not in phis:
                        d180 = np.abs(180 - angle)
                        if d180 < min_d:
                            selected_angle[0] = 0
                if selected_angle[0] == 360:
                    selected_angle[0] = 0
            elif angle <= 0:
                angle = np.abs(angle)
                d = np.abs(phis - angle)
                min_d = np.min(d)
                selected_angle = phis[d == min_d]
                if 180 not in phis:
                    d180 = np.abs(180 - angle)
                    if d180 < min_d:
                        selected_angle[0] = 0
    else:
        raise PreventUpdate

    # print(selected_angle)

    return bezel+1, selected_angle[0]

@app.callback(Output({'type': 'memory', 'index': 'projection-bezel-previous-state'}, 'data'),
              [Input({'type': 'memory', 'index': 'projection-bezel-turned'}, 'data')])
def update_bezel_previous_state(bezel_new):
    time.sleep(0.5)
    return bezel_new

@app.callback([Output({'type': 'memory', 'index': '2D-brdf-plot-previous-state'}, 'data'),
               Output({'type': 'trigger', 'index': 'for-2D-brdf-plot'}, 'data')],
              [Input({'type': 'trigger', 'index': 'modify-state'}, 'data')],
              [State({'type': 'memory', 'index': '2D-brdf-plot-previous-state'}, 'data'),
               State({'type': 'memory', 'index': 'previous_state'}, 'data'),
               State({'type': 'memory', 'index': 'selected_file'}, 'data')])
def trigger_2D_brdf_plot(trigger, plot_previous_state, previous_state, filename):
    if filename == '':
        raise PreventUpdate

    plot_new_state = {}
    for key in previous_state:
        if key != 'theta_r' and key != 'variable_as_x':
            plot_new_state[key] = previous_state[key]
    if plot_new_state == plot_previous_state:
        raise PreventUpdate
    else:
        plot_previous_state = plot_new_state

    return plot_previous_state, 'Triggered'

@app.callback(Output({'type': 'graph', 'index': '2d-brdf'},'figure'),
              [Input({'type': 'trigger', 'index': 'for-2D-brdf-plot'}, 'data'),
               Input({'type': 'trigger', 'index': 'mode-brdf-tab'}, 'data'),
               Input({'type': 'trigger', 'index': 'change-snap-states'}, 'data')],
              [State({'type': 'memory', 'index': 'browser_data_storage'}, 'data'),
               State({'type': 'memory', 'index': 'selected_file'}, 'data'),
               State({'type': 'memory', 'index': 'snaped-states'}, 'data')])
def update_2D_brdf_plot(trigger1, trigger2, trigger3, uploaded_data, filename, snaped_states):
    if uploaded_data == {} or filename == '':
        raise PreventUpdate

    data = uploaded_data[filename]['data']

    mask = np.array([])
    brdf = np.array([])
    # ubrdf = np.array([])
    theta_r = np.array([])
    phi_r = np.array([])
    s_phi_r = 0
    for variable in data:
        if variable != 'BRDF' and variable != 'uBRDF' and variable != 'theta_r' and variable != 'phi_r':
            if mask.size == 0:
                mask = np.array(data[variable]['values']) == data[variable]['sval']
            else:
                mask = np.logical_and(mask, np.array(data[variable]['values']) == data[variable]['sval'])
        else:
            if variable == 'BRDF':
                brdf = np.array(data[variable]['values'])
            if variable == 'uBRDF':
                ubrdf = np.array(data[variable]['values'])
            if variable == 'theta_r':
                theta_r = np.array(data[variable]['values'])
            if variable == 'phi_r':
                phi_r = np.array(data[variable]['values'])
                s_phi_r = data[variable]['sval']

    brdf = brdf[mask]
    # ubrdf = ubrdf[mask]
    theta_r = theta_r[mask]
    phi_r = phi_r[mask]

    figure = go.Figure()

    # for filename in uploaded_data:
    #     if uploaded_data[filename]['selected_states']['visible'] == [1] and filename != selected_filename:
    #         phis = np.array(uploaded_data[filename]['measurement_data']['phiVs'])
    #         thetas = np.array(uploaded_data[filename]['measurement_data']['thetaVs'])
    #         thI = uploaded_data[filename]['selected_states']['theta_I']
    #         phiI = uploaded_data[filename]['selected_states']['phi_I']
    #         pol = uploaded_data[filename]['selected_states']['polarization']
    #         wl = uploaded_data[filename]['selected_states']['wavelength']
    #         selected_angle = uploaded_data[filename]['selected_states']['phi_V']
    #         data = uploaded_data[filename]['measurement_data']
    #         selected_data = np.array(select_data(wl, thI, phiI, pol, data))
    #
    #         if selected_angle == 180:
    #             phi_mask = np.logical_or(phis == 180, phis == 0)
    #         elif selected_angle == 360:
    #             phi_mask = np.logical_or(phis == 0, phis == 180)
    #         elif selected_angle < 180:
    #             phi_mask = np.logical_or(phis == selected_angle, phis == (selected_angle + 180))
    #         elif selected_angle > 180:
    #             phi_mask = np.logical_or(phis == selected_angle, phis == (selected_angle - 180))
    #
    #         x = thetas
    #         y = selected_data[:, phi_mask].T
    #
    #         selected_phiVs = phis[phi_mask]
    #         # print(selected_phiVs)
    #
    #         if phis[phi_mask].shape[0] == 1:
    #             x = x
    #             y = y[0]
    #             x = x[y >= 0]
    #             y = y[y >= 0]
    #             figure.add_trace(go.Scatter(name='BRDF', x=x, y=y, mode='lines+markers'))
    #         elif phis[phi_mask].shape[0] == 2:
    #             y = np.concatenate((y[1][np.argsort(-x)], y[0]))
    #             x = np.concatenate((np.sort(-x), x))
    #             x = x[y >= 0]
    #             y = y[y >= 0]
    #             figure.add_trace(go.Scatter(name='BRDF',
    #                                         x=x,
    #                                         y=y,
    #                                         mode='lines+markers'))
    #             # figure.add_trace(go.Scatter(name='BRDF -90 to 0', x=-x, y=y[1], mode='lines+markers'))
    #         else:
    #             raise PreventUpdate

    phis = phi_r
    thetas = theta_r
    selected_angle = s_phi_r
    selected_data = brdf

    if selected_angle == 180:
        phi_mask = np.logical_or(phis == 180, phis == 0)
    elif selected_angle == 360:
        phi_mask = np.logical_or(phis == 0, phis == 180)
    elif selected_angle < 180:
        phi_mask = np.logical_or(phis == selected_angle, phis == (selected_angle + 180))
    elif selected_angle > 180:
        phi_mask = np.logical_or(phis == selected_angle, phis == (selected_angle - 180))

    x = thetas[phi_mask]
    y = selected_data[phi_mask]

    selected_phiVs = phis[phi_mask]
    selected_phiVs = np.unique(selected_phiVs)

    if selected_phiVs.shape[0] == 1:
        x = np.sort(x)
        y = y[np.argsort(x)]
        # x[y < 0] = None
        y[y < 0] = None
        figure.add_trace(go.Scatter(name='BRDF', x=x, y=y, mode='lines+markers'))
    elif selected_phiVs.shape[0] == 2:
        y_1 = y[phis[phi_mask] == selected_phiVs[0]]
        y_2 = y[phis[phi_mask] == selected_phiVs[1]]
        if selected_phiVs[0] < 180:
            y_1 = y_1[np.argsort(-x)]
            y_2 = y_2[np.argsort(x)]
            y = np.concatenate((y_1, y_2))
            x = np.concatenate((np.sort(-x), np.sort(x)))
        else:
            y_1 = y_1[np.argsort(x)]
            y_2 = y_2[np.argsort(-x)]
            y = np.concatenate((y_1, y_2))
            x = np.concatenate((np.sort(-x), np.sort(x)))
        # x[y < 0] = None
        y[y < 0] = None
        figure.add_trace(go.Scatter(name='BRDF',
                                    x=x,
                                    y=y,
                                    mode='lines+markers'))
        # figure.add_trace(go.Scatter(name='BRDF -90 to 0', x=-x, y=y[1], mode='lines+markers'))
    else:
        raise PreventUpdate

    if snaped_states != {}:
        for file_name in snaped_states:
            for selected_x in snaped_states[file_name]:
                if selected_x == 'theta_r':
                    for state in snaped_states[file_name][selected_x]:
                        data = uploaded_data[file_name]['data']
                        mask = np.array([])
                        brdf = np.array([])
                        # ubrdf = np.array([])
                        theta_r = np.array([])
                        phi_r = np.array([])
                        s_phi_r = 0
                        for variable in data:
                            if variable != 'BRDF' and variable != 'uBRDF' and variable != 'theta_r' and variable != 'phi_r':
                                if mask.size == 0:
                                    mask = np.array(data[variable]['values']) == state[variable]
                                else:
                                    mask = np.logical_and(mask, np.array(data[variable]['values']) == state[variable])
                            else:
                                if variable == 'BRDF':
                                    brdf = np.array(data[variable]['values'])
                                if variable == 'uBRDF':
                                    ubrdf = np.array(data[variable]['values'])
                                if variable == 'theta_r':
                                    theta_r = np.array(data[variable]['values'])
                                if variable == 'phi_r':
                                    phi_r = np.array(data[variable]['values'])
                                    s_phi_r = state[variable]

                        brdf = brdf[mask]
                        # ubrdf = ubrdf[mask]
                        theta_r = theta_r[mask]
                        phi_r = phi_r[mask]

                        phis = phi_r
                        thetas = theta_r
                        selected_angle = s_phi_r
                        selected_data = brdf

                        if selected_angle == 180:
                            phi_mask = np.logical_or(phis == 180, phis == 0)
                        elif selected_angle == 360:
                            phi_mask = np.logical_or(phis == 0, phis == 180)
                        elif selected_angle < 180:
                            phi_mask = np.logical_or(phis == selected_angle, phis == (selected_angle + 180))
                        elif selected_angle > 180:
                            phi_mask = np.logical_or(phis == selected_angle, phis == (selected_angle - 180))

                        x = thetas[phi_mask]
                        y = selected_data[phi_mask]

                        selected_phiVs = phis[phi_mask]
                        selected_phiVs = np.unique(selected_phiVs)

                        if selected_phiVs.shape[0] == 1:
                            x = np.sort(x)
                            y = y[np.argsort(x)]
                            # x[y < 0] = None
                            y[y < 0] = None
                            figure.add_trace(go.Scatter(name='BRDF', x=x, y=y, mode='lines+markers'))
                        elif selected_phiVs.shape[0] == 2:
                            y_1 = y[phis[phi_mask] == selected_phiVs[0]]
                            y_2 = y[phis[phi_mask] == selected_phiVs[1]]
                            if selected_phiVs[0] < 180:
                                y_1 = y_1[np.argsort(-x)]
                                y_2 = y_2[np.argsort(x)]
                                y = np.concatenate((y_1, y_2))
                                x = np.concatenate((np.sort(-x), np.sort(x)))
                            else:
                                y_1 = y_1[np.argsort(x)]
                                y_2 = y_2[np.argsort(-x)]
                                y = np.concatenate((y_1, y_2))
                                x = np.concatenate((np.sort(-x), np.sort(x)))
                            # x[y < 0] = None
                            y[y < 0] = None
                            figure.add_trace(go.Scatter(name='BRDF',
                                                        x=x,
                                                        y=y,
                                                        mode='lines+markers'))

    figure.update_layout(
        title="BRDF 2D plot at selected viewing azimuth",
        xaxis_title='Viewing zenith angle Theta (deg)',
        xaxis_nticks=15,
        xaxis_gridcolor='rgb(112,112,112)',
        xaxis_zerolinecolor='rgb(0,0,0)',
        yaxis_title='BRDF values (sr \u207B\u00B9)',
        yaxis_nticks=10,
        yaxis_gridcolor='rgb(112,112,112)',
        yaxis_zerolinecolor='rgb(0,0,0)',
        plot_bgcolor='rgb(255,255,255)'
    )

    return figure

@app.callback([Output({'type': 'memory', 'index': '2D-brdf-plot-clicked'}, 'data'),
               Output({'type': 'options', 'index': 'theta_r'}, 'value'),
               Output({'type': 'graph', 'index': '2d-brdf'}, 'clickData')],
              [Input({'type': 'graph', 'index': '2d-brdf'}, 'clickData')],
              [State({'type': 'memory', 'index': 'browser_data_storage'}, 'data'),
               State({'type': 'memory', 'index': 'selected_file'}, 'data'),
               State({'type': 'memory', 'index': '2D-brdf-plot-clicked'}, 'data'),
               State({'type': 'options', 'index': 'theta_r'}, 'options')])
def plot_2D_select_ThetaV(clickData, uploaded_data, filename, clicks, current_options):
    if uploaded_data == {} or filename == '':
        raise PreventUpdate
    # print(current_options)
    if clickData is not None:
        selected_theta = clickData['points'][0]['x']
        if {'label': selected_theta, 'value': selected_theta} not in current_options:
            raise PreventUpdate
    else:
        raise PreventUpdate
    return clicks+1, selected_theta, None

@app.callback([Output({'type': 'memory', 'index': '2D-arbitrary-plot-previous-state'}, 'data'),
               Output({'type': 'trigger', 'index': 'for-2D-arbitrary-plot'}, 'data')],
              [Input({'type': 'trigger', 'index': 'modify-state'}, 'data')],
              [State({'type': 'memory', 'index': '2D-arbitrary-plot-previous-state'}, 'data'),
               State({'type': 'memory', 'index': 'previous_state'}, 'data'),
               State({'type': 'memory', 'index': 'selected_file'}, 'data')])
def trigger_2D_arbtrary_plot(trigger, plot_previous_state, previous_state, filename):
    if filename == '':
        raise PreventUpdate

    plot_new_state = {}
    for key in previous_state:
        if key != previous_state['variable_as_x']:
            plot_new_state[key] = previous_state[key]
    if plot_new_state == plot_previous_state:
        raise PreventUpdate
    else:
        plot_previous_state = plot_new_state

    return plot_previous_state, 'Triggered'

@app.callback(Output({'type': 'graph', 'index': 'x-any-y-brdf'},'figure'),
              [Input({'type': 'trigger', 'index': 'mode-brdf-tab'}, 'data'),
               Input({'type': 'trigger', 'index': 'for-2D-arbitrary-plot'}, 'data'),
               Input({'type': 'trigger', 'index': 'change-snap-states'}, 'data')],
              [State({'type': 'memory', 'index': 'browser_data_storage'}, 'data'),
               State({'type': 'memory', 'index': 'selected_file'}, 'data'),
               State({'type': 'memory', 'index': 'snaped-states'}, 'data')])
def update_2D_arbitrary_plot(trigger1, trigger2, trigger3, uploaded_data, selected_filename, snaped_states):

    if selected_filename == '' or uploaded_data == {}:
        raise PreventUpdate
    if 'variable_as_x' not in uploaded_data[selected_filename]:
        raise PreventUpdate

    data = uploaded_data[selected_filename]['data']
    variable_selected_as_x = uploaded_data[selected_filename]['variable_as_x']
    variable_selected_as_x_unit = ''
    for variable in data:
        if variable == variable_selected_as_x:
            variable_selected_as_x_unit = str(data[variable]['unit'])
    # variables_to_options = {}
    # for variable in uploaded_data[selected_filename]['data']['variables']:
    #     if variable['name'] != 'BRDF' and variable['name'] != "uBRDF":
    #         variables_to_options[variable['name']] = {
    #             'options': [{'label': uval, 'value': uval} for uval in variable['uvals']],
    #             'value': variable['sval']
    #         }
    # variable_as_x_options = [{'label': key, 'value': key} for key in variables_to_options]
    # variable_selected_as_x = ''
    # if 'variable_as_x' in uploaded_data[selected_filename]:
    #     variable_selected_as_x = uploaded_data[selected_filename]['variable_as_x']
    # else:
    #     variable_selected_as_x = variable_as_x_options[len(variable_as_x_options) - 1]['value']
    figure = go.Figure()

    if variable_selected_as_x != 'theta_r':
        mask = np.array([])
        brdf = np.array([])
        # ubrdf = np.array([])
        x_variable = np.array([])
        for variable in data:
            if variable != 'BRDF' and variable != 'uBRDF' and variable != variable_selected_as_x:
                if mask.size == 0:
                    mask = np.array(data[variable]['values']) == data[variable]['sval']
                else:
                    mask = np.logical_and(mask, np.array(data[variable]['values']) == data[variable]['sval'])
            else:
                if variable == 'BRDF':
                    brdf = np.array(data[variable]['values'])
                if variable == 'uBRDF':
                    ubrdf = np.array(data[variable]['values'])
                if variable == variable_selected_as_x:
                    x_variable = np.array(data[variable]['values'])

        brdf = brdf[mask]
        # ubrdf = ubrdf[mask]
        x_variable = x_variable[mask]

        x = np.sort(x_variable)
        y = brdf[np.argsort(x_variable)]

        figure.add_trace(go.Scatter(x=x, y=y, mode='lines+markers'))

        if snaped_states != {}:
            for file_name in snaped_states:
                for selected_x in snaped_states[file_name]:
                    if selected_x != 'theta_r':
                        for state in snaped_states[file_name][selected_x]:
                            data = uploaded_data[file_name]['data']
                            mask = np.array([])
                            brdf = np.array([])
                            # ubrdf = np.array([])
                            x_variable = np.array([])
                            for variable in data:
                                if variable != 'BRDF' and variable != 'uBRDF' and variable != selected_x:
                                    if mask.size == 0:
                                        mask = np.array(data[variable]['values']) == state[variable]
                                    else:
                                        mask = np.logical_and(mask, np.array(data[variable]['values']) == state[variable])
                                else:
                                    if variable == 'BRDF':
                                        brdf = np.array(data[variable]['values'])
                                    if variable == 'uBRDF':
                                        ubrdf = np.array(data[variable]['values'])
                                    if variable == selected_x:
                                        x_variable = np.array(data[variable]['values'])

                            brdf = brdf[mask]
                            # ubrdf = ubrdf[mask]
                            x_variable = x_variable[mask]

                            x = np.sort(x_variable)
                            y = brdf[np.argsort(x_variable)]

                            figure.add_trace(go.Scatter(x=x, y=y, mode='lines+markers'))
    else:
        figure.add_trace(go.Scatter(x=[0, 1, 0.5, 0.5, -0.5, -0.5, -1, 0], y=[0, 1, 1, 3, 3, 1, 1, 0], mode='lines+markers'))

    figure.update_layout(
        title="BRDF dependence on parameter selected as X",
        xaxis_title= variable_selected_as_x + ' (' + variable_selected_as_x_unit + ')',
        yaxis_title='BRDF values (sr \u207B\u00B9)',
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

app.layout = server_layout()
app.title = "BiRDview"

#Run application code
if __name__ == '__main__':
    app.run_server(debug=False, dev_tools_ui=False, dev_tools_props_check=False)
    # app.run_server(debug=False)