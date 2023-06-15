from dash import Dash, html, dash_table, dcc, callback, Output, Input
import plotly.graph_objects as go
import pandas as pd
import plotly.express as px
import numpy as np

# Incorporate data
df = pd.read_csv("data/medals_processed.csv")

# Useful for Medal Comparison
DUMMY = {
    'Year': [],
    'Medals': []
}
for year in df["Year"].unique():
        DUMMY['Year'].append(year)
        DUMMY['Medals'].append(0)
DUMMY_DF = pd.DataFrame(DUMMY)
DUMMY_DF = DUMMY_DF.set_index("Year")

# Defining medal comparison
def initialize_compare_medals():
    dropdown_div = html.Div(
        id='compare-medals-options',
        children=[
            dcc.Dropdown([country for country in sorted(df["Country"].unique())],
                multi=True,
                id='compare-dropdown'
            )
        ]
    )

    graph = dcc.Graph(figure={}, id='compare-medals')
    return [
        html.Hr(),
        html.H3('Choose Participants'),
        dropdown_div,
        graph]

# Updating the medals comparison
@callback(
    Output(component_id='compare-medals', component_property='figure'),
    Input(component_id='compare-dropdown', component_property='value')
)
def update_compare_medals(selected_options):
    fig = go.Figure()

    for option in selected_options:
        df_filtered = df[df["Country"] == option].groupby(by="Year").sum()
        df_filtered = pd.concat([df_filtered, DUMMY_DF]).groupby(by="Year").sum().sort_values(by="Year", key=lambda col: col.str[-4:])

        fig.add_trace(go.Scatter(x=df_filtered.index, y=df_filtered.Medals,
                                 mode='lines+markers', name=option))

    fig.update_layout(title='Medal Comparison per Edition',
                      xaxis_title='Editions', yaxis_title='Sum of Medals',
                      height=800)
    return fig