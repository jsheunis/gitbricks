# -*- coding: utf-8 -*-

import dash
from dash import dcc
from dash import html
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from dash.dependencies import Input, Output
import numpy as np
import dash
import dash_bootstrap_components as dbc
from gitbricks import gitbricks

##################
# INITIALIZE APP #
##################

# External CSS stylesheets
external_stylesheets = [
    'https://codepen.io/chriddyp/pen/bWLwgP.css',
    {
        'href': 'https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css',
        'rel': 'stylesheet',
        'integrity': 'sha384-MCw98/SFnGE8fJT3GXwEOngsV7Zt27NXFoaoApmYm81iuXoPkFOJwJ8ERdknLPMO',
        'crossorigin': 'anonymous'
    }
]

# Create app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME],
                meta_tags=[
                    {"name": "viewport", "content": "width=device-width, initial-scale=1"}
                ])

# Set server (needed as variable in case of multi-page app)
# server = app.server

# Suppress callback exceptions
app.config.suppress_callback_exceptions = True

##############
# APP LAYOUT #
##############

asciiart="""
          _ _   _          _      _        
         (_) | | |        (_)    | |       
     __ _ _| |_| |__  _ __ _  ___| | _____ 
    / _` | | __| '_ \| '__| |/ __| |/ / __|
   | (_| | | |_| |_) | |  | | (__|   <\__ \\
    \__, |_|\__|_.__/|_|  |_|\___|_|\_\___/
    __/ |                                 
   |___/  Let's plot some colorful bricks!
    
    A GitHub-inspired calendar heatmap of the 1-year commit history of a git repository.
    """




fig = go.Figure(
    layout=go.Layout(
        margin=dict(
            l=10,
            r=10,
            b=10,
            t=50,
            pad=0
        ),
        height=175, width=1000
    )
)

form = dbc.Form(
    dbc.Row(
        [
            dbc.Col( [
                dbc.Label("Repository name", width="auto"),
                dbc.Input(type="text", placeholder="Enter: 'org-or-user-name/repo-name'", id="repo_name")
                ],
                className="me-3",
                width={"size": 2, "offset": 3}
            ),
            dbc.Col( [
                dbc.Label("Start year", width="auto"),
                dbc.Select(
                    id="select",
                    options=[
                        {"label": "2020", "value": 2020},
                        {"label": "2019", "value": 2019},
                        {"label": "2018", "value": 2018},
                    ],
                )
                ],
                className="me-3",
                width={"size": 2, "offset": 0}
            ),
            dbc.Col(
                dbc.Button([html.I(className="fas fa-th-large"), " Plot bricks!"], id="plotbricks", color="dark"),
                width={"size": 2, "offset": 0},
                style={'marginTop': '45px'}
            ),
        ],
        className="g-2",
    ),
    style={'marginTop': '0'}
)

app.layout = html.Div(
    children=[
        html.Pre(asciiart,
            style={
                'fontWeight': 'bold',
                'fontSize': '16px',
                'textAlign': 'center',
                'backgroundColor': 'black',
                'color': '#55ff55',
                'marginBottom': '0'
            }
        ),
        html.Br(),
        form,
        html.Div(
            dbc.Spinner(
                dcc.Graph(id='bricks', figure=fig),
            ),
            style={'textAlign': 'center', 'position': 'flex',
            'justifyContent': 'center',
            'justifyItems': 'center', 'paddingLeft': '10vw'
            }
        ),
    ],
    style={
        'marginBottom': 25,
        'marginTop': 25,
        'marginLeft': '5%',
        'maxWidth': '90%',
        'textAlign': 'center'
    }
)

#################
# APP CALLBACKS #
#################

@app.callback(
    Output("bricks", "figure"),
    Output("plotbricks", "n_clicks"),
    Input("plotbricks", "n_clicks"),
    Input("repo_name", "value"),
    Input("select", "value"),
    prevent_initial_call=True
)
def on_button_click(n, repo_name, start_year):
    if n is not None:
        print(repo_name)
        print(start_year)
        return gitbricks(repo_name, int(start_year), start_month=1, start_day=1, colormap=None, title=None, showfig=False, savefig=False), None
    else:
        raise dash.exceptions.PreventUpdate()

# gitbricks(repo_name, start_year, start_month=1, start_day=1):

##############
# RUN SERVER #
##############

if __name__ == '__main__':
    app.run_server(debug=True)