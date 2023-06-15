# Import packages
from dash import Dash, html, dash_table, dcc, callback, Output, Input
import plotly.graph_objects as go
import pandas as pd
import plotly.express as px
import numpy as np
from compare_medals import initialize_compare_medals
from heatmap import initialize_heatmap
from performance_evolution import initialize_performance_evolution
from compare_countries import initialize_compare_countries
from pib_vs_medals import initialize_pib
from sports_through_time import initialize_sports_per_year

# Incorporate data
df = pd.read_csv("data/medals_processed.csv")
df_pib = pd.read_parquet("data/medal_and_pib_summer.parquet")
df_sports_per_year_summer = pd.read_parquet("data/disciplines_per_year_summer.parquet")
df_sports_per_year_winter = pd.read_parquet("data/disciplines_per_year_winter.parquet")

# Initialize the app
app = Dash(__name__)


# App layout
app.layout = html.Div([
    # Sidebar menu
    html.Div(
        id='sidebar',
        className='sidebar',
        children=[
            html.H3('Graph Options'),
            dcc.Dropdown(
                options=[
                    {'label': 'Compare Medals', 'value': 'Compare Medals'},
                    {'label': 'Compare Countries', 'value': 'Compare Countries'},
                    {'label': 'Medals Heatmap', 'value': 'Heatmap'},
                    {'label': 'Performance x Time', 'value': 'Perf Evol'},
                    {'label': 'GPD x Medals Count', 'value': 'GPD vs Medals'},
                    {'label': 'Sports Through Time', 'value': 'Sports Through Time'}
                ],
                value='Compare Medals',
                id='choose-graph'
            )
        ]
    ),
    # Main content
    html.Div(
        id='content',
        className='content',
        children=[
            html.Hr()
        ],
        style={'height':'100%', 'width':'100%'}
    )
])
    
# Add controls to build the interaction
@callback(
    Output(component_id='content', component_property='children'),
    Input(component_id='choose-graph', component_property='value')
)
def update_graph(graph_type):
    if graph_type == "Compare Medals":
        return initialize_compare_medals()
    
    if graph_type == "Heatmap":
        return initialize_heatmap()
    
    if graph_type == "Perf Evol":
        return initialize_performance_evolution()
    
    if graph_type == "Compare Countries":
        return initialize_compare_countries()
    
    if graph_type == "GPD vs Medals":
        return initialize_pib()
    
    if graph_type == "Sports Through Time":
        return initialize_sports_per_year()


app.run_server()