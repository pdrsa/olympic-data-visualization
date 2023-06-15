from dash import Dash, html, dash_table, dcc, callback, Output, Input
import plotly.graph_objects as go
import pandas as pd
import plotly.express as px
import numpy as np

# Incorporate data
df = pd.read_csv("data/medals_processed.csv")

# Defining Heatmap
def initialize_heatmap():
    dropdown_div = html.Div(
        id='heatmap-options',
        children=[
            dcc.Dropdown(
                options=[
                    {'label': edition, 'value': edition}
                    for edition in df["Year"].unique()
                ],
                value=df["Year"][0],
                id='heatmap-dropdown'
            )
        ]
    )

    graph = dcc.Graph(figure={}, id='heatmap')
    return [
        html.Hr(),
        html.H3('Choose Edition'),
        dropdown_div,
        graph]
    
# Updating the heatmap
@callback(
    Output(component_id='heatmap', component_property='figure'),
    Input(component_id='heatmap-dropdown', component_property='value')
)
def update_heatmap(selected_option):
    df_filtered = df[df["Year"]==selected_option].sort_values(by="Year", key=lambda col: col.str[-4:])

    fig = px.density_heatmap(df_filtered, x='Country', y='Category',
                             z='Medals',
                             color_continuous_scale='burgyl',
                             text_auto = True)
    width = len(np.unique(fig.data[0].x)) * 20 + 200
    height = len(np.unique(fig.data[0].y)) * 20 + 200
    
    fig.update_layout({
        'xaxis': {
            'showgrid': True,  # thin lines in the background
            'zeroline': True,  # bold line at x=0
            'visible': True,  # numbers below
        },
        'yaxis': {
            'showgrid': True,  # thin lines in the background
            'zeroline': True,  # bold line at y=0
            'visible': True,  # numbers to the left
        }
    })
    fig.update_layout(title='Heatmap of Medals per Country in each Category',
                      xaxis_title='Country', yaxis_title='Category',
                      width=width,
                      height=height)
    return fig