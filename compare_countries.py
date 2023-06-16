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

olympic_events = pd.read_csv("./olympic_games/athlete_events.csv")
olympics_counts = olympic_events[['Team','Name', 'Year',]].drop_duplicates().sort_values('Year')
olympics_counts.loc[:, 'was_there'] = True
olympics_counts.loc[:, 'visitas_acumuladas'] = olympics_counts.groupby('Name',).was_there.cumsum()
olympics_counts.head()

olympic_results = pd.read_csv('./olympic_games/olympic_results.csv')
code_map = olympic_results[['country_name', 'country_code']].drop_duplicates().set_index('country_name').to_dict()['country_code']

olympic_events = olympic_events[olympic_events.Season == 'Summer']

for pat, country in zip(["China", 'United States\-|United States$', 'Russia'],
                        ["People's Republic of China",'United States of America', 'Russian Federation']):
    olympic_events.loc[olympic_events.Team.str.match(pat), 'Team'] = country
    olympics_counts.loc[olympics_counts.Team.str.match(pat), 'Team'] = country

y = olympic_events.groupby(['Team','NOC','Year']).agg({'Medal':'count'}).reset_index()
x = olympics_counts.groupby(['Team', 'Year']).visitas_acumuladas.mean()
df = x.reset_index().merge(y.reset_index(),on=['Team', 'Year'])



graph_layout = go.Layout(
    xaxis={'title': 'Ano'},
    yaxis={'title': f'Número de medalhas obtidas'},
    margin={'t': 20, 'b' : 5},
    )


def initialize_compare_countries():
    return [html.Div(
        style=None,
        children = [
        html.H1('Experiência dos atletas e resultados', style={'text-align': 'center', 'fontFamily': 'Open Sans, sans-serif'}),
        html.Div(
            style={'display': 'flex', 'flex-direction': 'column', 'align-items': 'center', 'height': '90vh', 'flex' : 1, 'justify-content' : '1'},
            children = [
                html.Div(
                id='row-1',
                style={'display' : 'flex', 'height' : '50%', 'width' : 'auto', },
                children=[
                    html.Div([
                        dcc.Dropdown(
                            id='country-dropdown-one',
                            value=None,
                            placeholder='Selecione um país',
                            options = [
                                {'label': html.Div([html.Img(src=f'https://raw.githubusercontent.com/hampusborgos/country-flags/main/png250px/{row.country_code.lower()}.png', 
                                                                    style={'width': '30px', 'height': 'auto', 'margin-right' : '5px'}), row.country_name],style={'display': 'flex', 'align-items': 'center'}
                                                  ), 'value': row.country_name} 
                                       for _,row in olympic_results[['country_name', 'country_code']].drop_duplicates().dropna().sort_values('country_name').iterrows()
                                      ]
                        ),
                        html.Div(
                            id='flag-container-1',
                            style={'display': 'flex', 'flex-direction': 'column', 'align-items': 'center', 'height': '100%'},
                            children =[
                                html.H2(id='country-header-one', children='Teste', style={'text-align': 'center'}),
                                html.Img(
                                    id='top-flag', 
                                    # src=f'https://raw.githubusercontent.com/hampusborgos/country-flags/main/png1000px/us.png',
                                    style={'width': '85%', 'height': 'auto', 'margin-right' : '5px'}
                                )
                                      ]
                        )
                    ], style={'margin-right': '10px', 'width' : '30%'}),
                    html.Div(
                        style={'flex' : '1',  },
                        children=[
                            dcc.Graph(
                                style={'width': '100%', 'height': '100%', 'display': 'flex', 'flex-direction': 'column', 'align-items': 'center',},
                                id='scatter-plot-one',
                            )
                        ]),
                    html.Div(
                            id='yaxis2row1',
                            children='Número médio de olimpíadas disputadas pela delegação',
                            style={
                                'writing-mode' : 'vertical-lr',
                                'height' : '90%',
                                'font-size' : '15px',
                                'margin-top' : '20px'
                            }
                    )
            ]),
            html.Div(
                id='row-2',
                style={'display' : 'flex', 'height' : '50%', 'width' : 'auto',  },
                children=[
                    html.Div([
                        dcc.Dropdown(
                            id='country-dropdown-two',
                            value=None,
                            placeholder='Selecione um país',
                            options = [
                                {'label': html.Div([html.Img(src=f'https://raw.githubusercontent.com/hampusborgos/country-flags/main/png250px/{row.country_code.lower()}.png', 
                                                                    style={'width': '30px', 'height': 'auto', 'margin-right' : '5px'}), row.country_name],style={'display': 'flex', 'align-items': 'center'}
                                                  ), 'value': row.country_name} 
                                       for _,row in olympic_results[['country_name', 'country_code']].drop_duplicates().dropna().sort_values('country_name').iterrows()
                                      ]
                        ),
                        html.Div(
                            id='flag-container-2',
                            style={'display': 'flex', 'flex-direction': 'column', 'align-items': 'center', 'height': '100%',},
                            children =[
                                html.H2(id='country-header-two', children='Teste', style={'text-align': 'center'}),
                                html.Img(
                                    id='bottom-flag', 
                                    style={'width': '85%', 'height': 'auto', 'margin-right' : '5px'}
                                )
                                      ]
                        )
                    ], style={'margin-right': '10px', 'width' : '30%'}),
                    html.Div([
                        dcc.Graph(
                            style={'width': '100%', 'height': '100%'},
                            id='scatter-plot-two',
                        )
                    ], style={'flex' : '1'}),
                    html.Div(
                            id='yaxis2row2',
                            children='Número médio de olimpíadas disputadas pela delegação',
                            style={
                                'writing-mode' : 'vertical-lr',
                                'height' : '90%',
                                'font-size' : '15px',
                                'margin-top' : '20px'
                            }
                    )
            ]),
        ])
])]


# # Callback para atualizar o gráfico com base nas seleções dos dropdowns
@callback(
    Output('scatter-plot-one', 'figure'),
    Input('country-dropdown-one', 'value')
)
def update_function_for_country(country):
    print(country)
    subdf = df[df.Team.str.match(country)]
    print(subdf)
    return   go.Figure(
                                data=go.Bar(
                                    x=subdf['Year'],
                                    y=subdf['Medal'],
                                    # mode='markers',
                                    marker=dict(
                                        color=subdf['visitas_acumuladas'],
                                        colorscale='YlOrRd',  # Define a escala de cores
                                        showscale=True,
                                        # size=12,
                                        cmax = 4,
                                    ),
                                ),
                                
                                layout=graph_layout,
    )

@callback(
    Output('scatter-plot-two', 'figure'),
    Input('country-dropdown-two', 'value')
)
def update_function_for_country_two(country):
    subdf = df[df.Team == country]
#
    return   go.Figure(
                                data=go.Bar(
                                    x=subdf['Year'],
                                    y=subdf['Medal'],
                                    # mode='markers',
                                    marker=dict(
                                        color=subdf['visitas_acumuladas'],
                                        colorscale='YlOrRd',  # Define a escala de cores
                                        showscale=True,
                                        cmax = 4,
                                    ),
                                    
                                ),
                                layout=graph_layout
    )

@callback(
    Output('top-flag', 'src'),
    Input('country-dropdown-one', 'value')
)
def update_flag_one(country):
    code = code_map.get(country)
    if code is None:
        return f'https://freepngimg.com/save/117897-cross-mark-free-download-image/1156x614'
    else:
        return f'https://raw.githubusercontent.com/hampusborgos/country-flags/main/png1000px/{code.lower()}.png'

@callback(
    Output('bottom-flag', 'src'),
    Input('country-dropdown-two', 'value')
)
def update_flag_two(country):
    code = code_map.get(country)
    if code is None:
        return f'https://freepngimg.com/save/117897-cross-mark-free-download-image/1156x614'
    else:
        return f'https://raw.githubusercontent.com/hampusborgos/country-flags/main/png1000px/{code.lower()}.png'

@callback(
    Output('country-header-one', 'children'),
    Input('country-dropdown-one', 'value')
)
def update_header_one(country):
    return country

@callback(
    Output('country-header-two', 'children'),
    [Input('country-dropdown-two', 'value')],
    State('scatter-plot-one', 'figure')
)
def update_header_two(country, figure):
    return country

