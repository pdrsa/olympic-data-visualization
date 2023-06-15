from dash import Dash, html, dash_table, dcc, callback, Output, Input
import pandas as pd
import numpy as np
import plotly.graph_objs as go
import plotly.graph_objects as go
from sklearn.preprocessing import MinMaxScaler
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

# Incorporate data
df_pib = pd.read_parquet("data/medal_and_pib_summer.parquet")
print("loaded df")

def get_trendline(df1, year):
    yearly_df = df1[df1['Year'] == year]
    x = yearly_df['GDP (constant 2015 US$)'].dropna().to_numpy().reshape(-1, 1)
    y = yearly_df['Medals'].dropna().to_numpy().reshape(-1, 1)

    scaler_x = MinMaxScaler()
    scaler_y = MinMaxScaler()
    x_scaled = scaler_x.fit_transform(x)
    y_scaled = scaler_y.fit_transform(y)

    model = LinearRegression()
    model.fit(x_scaled, y_scaled)

    y_pred = model.predict(x_scaled)
    r2 = r2_score(y_scaled, y_pred)

    trendline_x = np.linspace(min(x_scaled), max(x_scaled), num=500).reshape(-1, 1)
    trendline_y = scaler_y.inverse_transform(model.predict(trendline_x)).flatten()
    trendline_x = scaler_x.inverse_transform(trendline_x).flatten()

    return trendline_x, trendline_y, r2

# Defining plot
def initialize_pib():
    graph = dcc.Graph(figure=update_pib(), id='pib')
    return [
        html.Hr(),
        graph]

def update_pib():
    # Create a new Plotly figure
    fig = go.Figure()

    # First trendline
    trendline_x, trendline_y, r2 = get_trendline(df_pib, df_pib['Year'].min())
    fig.add_trace(go.Scatter(x=trendline_x, y=trendline_y, mode='lines', name='Trendline'))

    annotation_text = f"R2: {r2:.2f}"  # Format the r2 value as desired
    fig.add_annotation(
        text=annotation_text,
        xref="paper",
        yref="paper",
        x=0.02,
        y=0.95,
        showarrow=False,
        font=dict(size=14, color="black"),
    )

    # For each country in the dataframe, create a separate trace
    for country in df_pib['Country NOC'].unique():
        country_df = df_pib[df_pib['Country NOC'] == country]
        fig.add_trace(go.Scatter(
            x=country_df[country_df['Year'] == df_pib['Year'].min()]['GDP (constant 2015 US$)'],
            y=country_df[country_df['Year'] == df_pib['Year'].min()]['Medals'],
            mode='markers',
            marker=dict(size=12, line=dict(width=2, color='DarkSlateGrey')),
            name=country,
            legendgroup=country,  # this ensures the legend behaves correctly
            hovertemplate='GDP: %{x} <br>Medals: %{y}',
        ))

    # Create frames for each year
    frames = []
    for k in df_pib['Year'].unique():
        trendline_x, trendline_y, r2 = get_trendline(df_pib, k)

        # Add trendline annotation for each frame
        annotation_text = f"R2: {r2:.2f}"  # Format the r2 value as desired
        layout = go.Layout(
            annotations = [
                go.layout.Annotation(
                    text=annotation_text,
                    xref="paper",
                    yref="paper",
                    x=0.02,
                    y=0.95,
                    showarrow=False,
                    font=dict(size=14, color="black"),
                    visible=True  # Set the annotation to be hidden initially
                )
            ]
        )

        frame = go.Frame(name=f'frame_{k}',
                         layout=layout,
                         data=([go.Scatter(x=trendline_x, y=trendline_y, mode='lines', name='Trendline')] + 
                               [go.Scatter(x=df_pib[(df_pib['Year']==k) & (df_pib['Country NOC']==country)]['GDP (constant 2015 US$)'],
                                          y=df_pib[(df_pib['Year']==k) & (df_pib['Country NOC']==country)]['Medals'],
                                          mode='markers') for country in df_pib['Country NOC'].unique()]))
        frames.append(frame)

    fig.frames = frames

    # Configure the figure layout, including the animation slider
    fig.update_layout(
        title="Countries' GDP (in 2015 US$) versus Number of Medals",
        xaxis=dict(constrain='domain', type='log', title='Log10 of GDP (in 2015 US$)', tickfont=dict(color='red'), range=[np.log10(df_pib['GDP (constant 2015 US$)'].min()), np.log10(df_pib['GDP (constant 2015 US$)'].max() * 1.05)]),
        yaxis=dict(scaleanchor='x', scaleratio=1, title='Medals', range=[-5, df_pib['Medals'].max() + 5]),
        height=800,
        width=1100,
        margin=dict(l=50, r=50, b=50, t=50),
        autosize=False,
        updatemenus=[
            dict(
                type="buttons",
                showactive=False,
                buttons=[
                    dict(label="Play",
                         method="animate",
                         args=[None,
                               dict(frame=dict(duration=500, redraw=True),
                                    fromcurrent=True,
                                    transition=dict(duration=0))]),
                    dict(label="Pause",
                         method="animate",
                         args=[[None],  # Note the list
                               dict(frame=dict(duration=0, redraw=True),
                                    mode="immediate")])
                ],
            )
        ],
        sliders=[dict(steps=[dict(method='animate',
                                  args=[[f'frame_{k}'],
                                        dict(mode='immediate',
                                             frame=dict(duration=500, redraw=True),
                                             transition=dict(duration=0))],
                                  label=str(k)) for k in df_pib['Year'].unique()])],
        )
    
    # Show the figure
    return fig
