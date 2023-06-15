from dash import Dash, html, dash_table, dcc, callback, Output, Input
import pandas as pd
import numpy as np
import colorcet as cc
import bisect
import plotly.graph_objs as go
import plotly.graph_objects as go

# Incorporate data
df_sports_per_year_summer = pd.read_parquet("data/disciplines_per_year_summer.parquet")
df_sports_per_year_winter = pd.read_parquet("data/disciplines_per_year_winter.parquet")

# Defining plot
def initialize_sports_per_year():
    dropdown_div = html.Div(
        id='season-options',
        children=[
            dcc.Dropdown(["Summer", "Winter"],
                multi=False,
                id='season-dropdown',
                value="Summer"
            )
        ]
    )
    graph = dcc.Graph(figure={}, id='sports-per-year')
    return [
        html.Hr(),
        html.H3('Choose Season of Games'),
        dropdown_div,
        graph]

# Updating the medals comparison
@callback(
    Output(component_id='sports-per-year', component_property='figure'),
    Input(component_id='season-dropdown', component_property='value')
)
def update_sports_per_year(season):
    if season == "Summer":
        disciplines_per_year = df_sports_per_year_summer
        title = "Sports per Year in Summer Games"
        height_per_event = 20
        x_axis_top_height = 1.025
        color = "hot"
    else:
        disciplines_per_year = df_sports_per_year_winter
        title = "Sports per Year in Winter Games"
        height_per_event = 30
        x_axis_top_height = 1.1
        color = "cold"

    # Sort the data
    disciplines_per_year = disciplines_per_year.sort_values(by=['game_year', 'discipline_title'], ascending=True)
    years = sorted(disciplines_per_year["game_year"].unique())

    # Create a list to hold the traces
    data = []

    # Get a unique list of discipline_title
    disciplines = np.flip(disciplines_per_year['discipline_title'].unique())

    # Generate a gradient color scale
    if color == "cold":
        original_colors = cc.bmy
        original_colors = original_colors[:100]
    else:
        original_colors = cc.CET_L4
        original_colors = original_colors[100:180]

    # Specify the number of colors you want
    num_colors = len(disciplines)  # adjust this value to get the desired length of the gradient

    # Generate equally spaced indices
    indices = np.linspace(0, len(original_colors) - 1, num_colors, dtype=int)

    # Select colors using the generated indices
    colors = [original_colors[i] for i in indices]

    # Since glasbey color maps may not contain enough colors, we repeat the color list to ensure all disciplines have a color
    colors = colors * (len(disciplines) // len(colors) + 1)

    # Create a scatter plot for each discipline
    for i, discipline in enumerate(disciplines):
        df = disciplines_per_year[disciplines_per_year['discipline_title'] == discipline]
        
        x_values = []
        y_values = []
        previous_year = None

        for _, row in df.iterrows():
            # If the previous year is not None and the difference between the current year and the previous year is not 4
            # add a None value to the x and y lists to break the line
            if previous_year is not None and previous_year != years[bisect.bisect_left(years, row['game_year']) - 1]:
                x_values.append(None)
                y_values.append(None)
            
            # Always add the year and discipline to the list of x and y values
            x_values.append(row['game_year'])
            y_values.append(row['discipline_title'])

            # Set the current year as the previous year for the next iteration
            previous_year = row['game_year']

        trace = go.Scatter(
            x = x_values, 
            y = y_values, 
            mode = 'lines+markers', 
            name = discipline, 
            line = dict(color = colors[i], width=9),
            marker = dict(size = 13)
        )
        data.append(trace)

    # Define layout
    layout = go.Layout(
        title=title,
        margin=dict(l=200, r=250, t=100, b=20),
        xaxis=dict(
            title='Year',
            tickvals=disciplines_per_year['game_year'].unique(),
            ticktext=disciplines_per_year['game_year'].unique(),
            tickangle=45,
        ), 
        yaxis=dict(title='Sport'), 
        height = len(disciplines)*height_per_event, # adjust this number to get an appropriate plot height
        showlegend=False,
        annotations=[
            # X-axis labels on top
            dict(
                x=x,
                y=x_axis_top_height,
                xref='x',
                yref='paper',
                text=str(x),
                showarrow=False,
                textangle=45,
            ) for x in disciplines_per_year['game_year'].unique()
        ] + [
            # Y-axis labels on right
            dict(
                x=1.00,
                y=discipline,
                xref='paper',
                yref='y',
                text=discipline,
                xanchor='left',
                showarrow=False
            ) for discipline in disciplines
        ]
    )

    # Create the figure
    fig = go.Figure(data=data, layout=layout)

    # Show the figure
    return fig