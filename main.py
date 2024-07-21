import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px

#-------------------LOADING_AND_PREPING_TEMPERATURE_DATA------------------------#

temperature_df = pd.read_csv('https://data.giss.nasa.gov/gistemp/graphs/graph_data/Global_Mean_Estimates_based_on_Land_and_Ocean_Data/graph.txt', sep='\s+')
temperature_changes_from_1971_to_2021 = temperature_df.iloc[94:145]
temperature_changes_from_1971_to_2021.columns = ['Year', 'No_Smoothing', 'Lowess(5)', 'Uncertainty']
temperature_changes_from_1971_to_2021 = temperature_changes_from_1971_to_2021[['Year', 'No_Smoothing']]
temperature_changes_from_1971_to_2021['Year'] = temperature_changes_from_1971_to_2021['Year'].astype(int)

#-------------------LOADING_AND_PREPING_ENERGY_DATA------------------------#

energy_df = pd.read_excel("WorldEnergyBalancesHighlights2023.xlsx", sheet_name='TimeSeries_1971-2022')
world_data_from_1971_to_2021 = energy_df.iloc[6832]
data = []
for i in range(6, 57):
    data.append(world_data_from_1971_to_2021.iloc[i])
years = list(range(1971, 2022))
energy_data = pd.DataFrame({'Year': years, 'Energy_Production': data})
energy_data['Year'] = energy_data['Year'].astype(int)

#-------------------MERGING_DATA------------------------#

combined_df = pd.merge(temperature_changes_from_1971_to_2021, energy_data, on='Year')

#-------------------DASH_APP------------------------#

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Energy Production and Climate Change Analysis"),
    dcc.Graph(id='energy-production'),
    dcc.Graph(id='global-temperature'),
    dcc.Graph(id='correlation')
])


@app.callback(
    Output('energy-production', 'figure'),
    Input('energy-production', 'id')
)
def update_energy_production(id):
    fig = px.line(combined_df, x='Year', y='Energy_Production',
                  title='Energy Production Over Time')
    fig.update_layout(
        xaxis_title='Year',
        yaxis_title='Energy Production (GWh)',
        yaxis_tickformat=',.0f',
        xaxis_tickformat=',.0f',
        template='plotly_white'
    )
    return fig


@app.callback(
    Output('global-temperature', 'figure'),
    Input('global-temperature', 'id')
)
def update_global_temperature(id):
    fig = px.line(combined_df, x='Year', y='No_Smoothing',
                  title='Global Temperature Anomalies Over Time')
    fig.update_layout(
        xaxis_title='Year',
        yaxis_title='Temperature Anomaly (°C)',
        yaxis_tickformat='.2f',
        xaxis_tickformat=',.0f',
        template='plotly_white'
    )
    return fig


@app.callback(
    Output('correlation', 'figure'),
    Input('correlation', 'id')
)
def update_correlation(id):
    fig = px.scatter(combined_df, x='Energy_Production', y='No_Smoothing',
                     trendline='ols', title='Correlation between Energy Production and Temperature Anomalies')
    fig.update_traces(marker=dict(size=9, color='LightSkyBlue', line=dict(width=2, color='DarkSlateGrey')))
    fig.update_layout(
        xaxis_title='Energy Production (GWh)',
        yaxis_title='Temperature Anomaly (°C)',
        yaxis_tickformat='.2f',
        xaxis_tickformat=',.0f',
        template='plotly_white'
    )
    return fig


#-------------------AFTER_10_SEC_REFRESH_SITE------------------------#

if __name__ == '__main__':
    app.run_server()
