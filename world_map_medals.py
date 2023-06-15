from dash import Dash, html, dash_table, dcc, callback, Output, Input
import os
import pandas as pd
import numpy as np
import plotly.express as px

df_summer = pd.read_parquet("data/summer_world_map.parquet")
df_winter = pd.read_parquet("data/winter_world_map.parquet")

# Sidebar menu
def initialize_world_map():
    dropdown_div = html.Div(
        id='worldmap-options',
        className='worldmap-options',
        children=[
            dcc.Dropdown(
                options=[
                    {'label': 'Summer', 'value': 'Summer'},
                    {'label': 'Winter', 'value': 'Winter'}
                ],
                value='Summer',
                id='choose-worldmap-season'
            )
        ]
    )

    graph = dcc.Graph(figure={}, id='worldmap')
    return [
        html.Hr(),
        html.H3('Choose Season'),
        dropdown_div,
        graph]

@callback(
    Output(component_id='worldmap', component_property='figure'),
    Input(component_id='choose-worldmap-season', component_property='value')
)
def update_world_map(selected_option):
    if selected_option == 'Summer':
        df = df_summer.copy()
    elif selected_option == 'Winter':
        df = df_winter.copy()
    else:
        raise Exception('Option does not exist')

    df = df.sort_values(['Year'])
    color_max = df['Occurances'].max()
    fig = px.choropleth(df,
        locations='Code', 
        color = df['Occurances'].astype(float), 
        locationmode="ISO-3",
        projection='natural earth',
        scope="world", 
        color_continuous_scale = 'Emrld', 
        labels={'color':'Número de medalhas'},
        title = 'Número de medalhas por país - Olimpíada de Verão',
        hover_name='Country',
        animation_frame="Year",
        animation_group="Code",
        range_color = [0, color_max]
        )

    fig.update_layout(
        title_x =0.5,
        title_font_size=30,
        updatemenus = [
            {
                'buttons': [{'args': [None, {'frame': {'duration': 500, 'redraw': True},
                                    'mode': 'immediate', 'fromcurrent': True, 'transition':
                                    {'duration': 500, 'easing': 'linear'}}],
                            'label': '&#9654;',
                            'method': 'animate'},
                            {'args': [[None], {'frame': {'duration': 0, 'redraw': True},
                                    'mode': 'immediate', 'fromcurrent': True, 'transition':
                                    {'duration': 0, 'easing': 'linear'}}],
                            'label': '&#9724;',
                            'method': 'animate'}],
                'direction': 'left',
                'pad': {'r': 10, 't': 70},
                'showactive': False,
                'type': 'buttons',
                'x': 0.1,
                'xanchor': 'right',
                'y': 0,
                'yanchor': 'top'
            },
        ])

    fig.update_layout(
            autosize=False,
            margin = dict(
                    l=100,
                    r=40,
                    b=20,
                    t=70,
                    pad=4,
                    autoexpand=True
                ),
                width=1200,
                height=600,
        )

    fig['layout'].sliders[0].currentvalue['prefix'] = 'Ano: '
    fig.update_traces(hovertemplate='<b>%{hovertext}</b><br><br>Ano: 1896<br>Número de medalhas: %{z}<extra></extra>')
    for frame in fig.frames:
        year = frame.name
        frame.data[0].hovertemplate = f'<b>%{{hovertext}}</b><br><br>Ano: {year}<br>Número de medalhas: %{{z}}'
    
    return fig