import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objs as go
from ipywidgets import widgets
import itertools
import re
from plotly.subplots import make_subplots
import dash
from dash import dcc
from dash import html, callback
from dash.dependencies import Input, Output, State
from jupyter_dash import JupyterDash
import pandas as pd
import plotly.graph_objs as go

noc = pd.read_csv("./olympic_games/noc_regions.csv")
olympic_events = pd.read_csv("./olympic_games/athlete_events.csv")
olympic_medals = olympic_events[["Games", "Season", "Year", "Event", "Medal", "NOC"]].copy()
olympic_medals.dropna(inplace=True)
olympic_medals.drop_duplicates(keep="first", inplace=True)
olympic_medals = olympic_medals.merge(noc[["NOC", "region"]], on=["NOC"])
olympic_medals.rename(columns={"region": "Country"}, inplace=True)
summer_years = olympic_medals[olympic_medals["Season"] == "Summer"]["Year"].unique()
winter_years = olympic_medals[olympic_medals["Season"] == "Winter"]["Year"].unique()

olympic_results = pd.read_csv('./olympic_games/olympic_results.csv')
olympic_hosts = pd.read_csv('./olympic_games/olympic_hosts.csv')
olympic_results.rank_position = pd.to_numeric(olympic_results.rank_position, errors='coerce')
olympic_results = olympic_results.merge(olympic_hosts, left_on='slug_game', right_on='game_slug', how='left')
fc = ['Gymnastics Artistic', "vault men"]

events = olympic_results[['discipline_title','event_title', 'game_year', 'value_unit']]\
    .drop_duplicates()\
    .groupby(['discipline_title','event_title'])\
    .agg(
        {'game_year' : 'count', 'value_unit' : 'count'},
    )
events = events[(events.game_year >= 4)]
events = events[(events.value_unit > 0)].reset_index()

value_type_map = {
    'POINTS' : 'Pontos',
    'TIME' : 'Tempo',
    'IRM_POINTS' : 'Pontos',
    'STROKES' : 'Golpes',
    'WEIGHT' : 'Peso',
    'DISTANCE': 'Distância',
    'SCORE' : 'Pontos'    
}

regexes = {
    '\d+\.\d+$' : (lambda s : float(s)),
    '\d+\,\d+$': (lambda s : float(s.replace(',', ''))),
    '\d+$' : lambda s :  float(s),
    '\d+\:\d+.\d+$': (lambda s : pd.to_timedelta('00:' + s)),
    '\d+\:\d+\:\d+.\d+$': lambda s : pd.to_timedelta,
    '\-\d+\.\d+$' : lambda s : float(s), # equestrian event (the less the better),
    '\-\d+\,\d+$' : lambda s : float(s.replace(',', '.')), # equestrian event (the less the better),
    '\d+\ $' : lambda s : float(s), # sailing, just remove space
    '\d+.\d+w' : lambda s : float(s.replace('w', '')), # w indicates wind assist
}

check_result = re.compile('|'.join(regexes.keys()))
olympic_results.loc[:, 'result_check'] = olympic_results.value_unit.str.match(check_result, na=False)

def aux(s):
    if not isinstance(s, str):
        return
    for r in regexes.keys():
        if bool(re.compile(r).match(s)):
            return regexes[r](s)
    

olympic_results.loc[:, 'parsed_value'] = olympic_results.value_unit.apply(aux)
olympic_results.loc[:, 'parsed_value_type'] = olympic_results.value_type.apply(lambda x : value_type_map.get(x))

re.compile('|'.join(regexes.keys()))

events = olympic_results[['discipline_title','event_title', 'game_year', 'value_unit', 'value_type']]\
    .drop_duplicates()\
    .groupby(['discipline_title','event_title'])\
    .agg(
        {'game_year' : 'nunique', 'value_unit' : 'count', 'value_type' : set}
    )

events.loc[:,'valid_value_type'] = events.value_type.apply(lambda t : bool(sum([value_type_map.get(t_) is not None for t_ in t])))
events = events[(events.game_year >= 4)]
events = events[(events.value_unit > 0)]
events = events[(events.valid_value_type)]
events = events.reset_index()

def initialize_performance_evolution():
    return [html.Div([
        html.H1('Evolução da performance ao longo do tempo', style={'text-align': 'center', 'fontFamily': 'Open Sans, sans-serif'}),
        html.Div(style={'display': 'flex', 'justify-content': 'space-between'},
                children=[
            html.Div([
                dcc.Dropdown(
                    id='discipline-dropdown',
                    options=[{'label': discipline, 'value': discipline} for discipline in discipline_options],
                    value='Athletics',
                    placeholder='Selecione uma disciplina'
                )
            ], style={'flex': '1'}),
            
            html.Div([
                dcc.Dropdown(
                    id='event-dropdown',
                    value='5000m men',
                    placeholder='Selecione um evento'
                )
            ], style={'flex': '1' }),
        ]),
        # Gráfico de linha
        dcc.Graph(id='line-chart')
    ])]

# events.sort_values('game_year', ascending=False).head(50)
discipline_options = events['discipline_title'].unique()
event_options = events['event_title'].unique()


@callback(
    Output('event-dropdown', 'options'),
    Input('discipline-dropdown', 'value')
)
def update_dropdown_event(discipline):
    if discipline:
        event_options = [{'label': event, 'value': event} for event in events[events['discipline_title'] == discipline]['event_title'].unique()]
    else:
        event_options = []
    return event_options

    
# Callback para atualizar o gráfico com base nas seleções dos dropdowns
@callback(
    Output('line-chart', 'figure'),
    [
        Input('event-dropdown', 'value'),
    ],
     State('discipline-dropdown', 'value'))
def update_chart(event, discipline):
    filtered_df = olympic_results[(olympic_results.game_year > 1923) ].copy()
    # Filtrando por discipline_title, se selecionado
    if discipline:
        filtered_df = filtered_df[filtered_df['discipline_title'] == discipline]
    # Filtrando por event_title, se selecionado
    if event:
        filtered_df = filtered_df[filtered_df['event_title'] == event]
    
    data = filtered_df.groupby('game_year').agg(
        avg = ('parsed_value', 'mean'),
        std = ('parsed_value', np.std)
    ).reset_index()

    data.sort_values('game_year', ascending=False, inplace=True)
    data = data[data.avg.notna()]


    band_lower =    go.Scatter(
        name='Lower Bound',
        x=data['game_year'],
        y=np.where(data['std'].notna(), data['avg'] - data['std'], data['avg']),
        marker=dict(color="#444"),
        line=dict(width=0),
        mode='lines',
        fillcolor='rgba(220, 220, 220, 0.6)',
        fill='tonexty',
        showlegend=False,
    )

    band_upper =    go.Scatter(
        name='Upper Bound',
        x=data['game_year'],
        y=np.where(data['std'].notna(), data['avg'] + data['std'], data['avg']),
        marker=dict(color="#444"),
        line=dict(width=0),
        mode='lines',
        fillcolor='rgba(220, 220, 220, 0.6)',
        showlegend=False,
        # fill='tonexty',
    )

    trace1 = go.Scatter(
        x=data['game_year'],
        y=pd.to_numeric(data['avg'], errors='coerce'),
        mode='lines+markers',
        name=f'Média',
        line=dict(width=6),
        marker=dict(size=10)
    )

    type = filtered_df.parsed_value_type.values[0]
    layout = go.Layout(
        xaxis={'title': 'Ano'},
        yaxis={'title': f'Resultado ({type})'},
        margin={'t':10},
        showlegend=False,
        height=800,
        font=dict(size=18)
    )
    traces = [trace1, band_upper, band_lower]
    fig = go.Figure(data=traces, layout=layout)
    return fig