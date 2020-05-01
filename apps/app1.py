import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import requests as r
from pandas.io.json import json_normalize
from app import app

data = r.get('https://corona.lmao.ninja/v2/historical',
             params={'lastdays': 'all'})
r2 = r.get('https://corona.lmao.ninja/v2/countries')

df = pd.read_json(data.text)
countryData = json_normalize(r2.json())
countryData['updated'] = pd.to_datetime(countryData.updated, unit='ms').dt.strftime('%m/%d/%Y %H:%M')

# app = dash.Dash(__name__)


def addcolumns(row):
    dff = pd.DataFrame(row.timeline)
    dff['country'] = row.country
    dff['province'] = row.province
    dff['dailycases'] = dff.cases.diff().fillna(0)
    dff['dailydeaths'] = dff.deaths.diff().fillna(0)
    dff['dailyrecovered'] = dff.recovered.diff().fillna(0)
    return dff


df['timeline'] = df.apply(addcolumns, axis=1)
flat = pd.concat(list(df.timeline)).reset_index()

options = list(flat.columns)
countries = list(df.country.unique())

# fig = go.Figure(data=go.Choropleth(
#     locations=countryData['countryInfo.iso3'],
#     z=countryData['casesPerOneMillion']
# ))

fig = px.choropleth(
    countryData[countryData['casesPerOneMillion'] < 8000],
    locations='countryInfo.iso3',
    color='casesPerOneMillion',
    hover_name='country',
    height=600
)

layout = html.Div([
    html.Div([
        html.Div([
            dcc.Dropdown(id='chart-type',
                         options=[{'label': i, 'value': i} for i in options],
                         value='dailycases',
                         ),
            dcc.Dropdown(
                id='chart-date',
                options=[{'label': i, 'value': i}
                         for i in flat['index'].unique()],
                value=flat['index'].unique()[-1],
            )
        ],
            style={'display': 'inline-block', 'width': '49%'}
        ),
        html.Div([
            dcc.Dropdown(id='country',
                         options=[{'label': i, 'value': i} for i in countries],
                         value="USA",
                         )],
                 style={'display': 'inline-block',
                        'width': '49%',
                        'float': 'right'}
                 )
    ]),
    html.Div([
        dcc.Graph(id='chart', style={
                  'display': 'inline-block', 'width': '49%'}),
        dcc.Graph(id='country-chart',
                  style={'display': 'inline-block', 'width': '49%', 'float': 'right'})
    ]),
    html.Div([
        dash_table.DataTable(
            id='table',
            columns=[{"name": i, "id": i} for i in countryData.columns[:6]],
            data=countryData.iloc[:, :6].to_dict('records'),
            fixed_rows={ 'headers': True, 'data': 0 },
            style_table={
                'maxHeight': '300px',
                'overflowY': 'scroll',
                'border': 'thin lightgrey solid',
            },
            # editable=True,
            filter_action="native",
            sort_action="native",
            sort_mode="multi",
            # column_selectable="single",
            # row_selectable="multi",
            # row_deletable=True,
            # selected_columns=[],
            # selected_rows=[],
            page_action="native",
            page_current= 0,
            page_size= 10,
        )
    ], className='container'),
    html.Div([
        dcc.Graph(id='map',
                  figure=fig
                  )
    ])
])


@app.callback(
    Output('chart', 'figure'),
    [Input('chart-type', 'value'),
     Input('chart-date', 'value')]
)
def changeChart(chartType, chartDate):
    top = flat[flat['index'] == chartDate]
    top10 = top.sort_values('cases', ascending=False).iloc[:10, :]
    top10chart = flat[flat['country'].isin(list(top10.country))]
    return px.line(top10chart, x='index', y=chartType, line_group='country', hover_name='country', color='country')


@app.callback(
    Output('country-chart', 'figure'),
    [Input('country', 'value')]
)
def changeCountry(country):
    c = flat[flat['country'] == country].melt(['index', 'country', 'province'])
    c = c[c['variable'].str.contains('daily')]
    return px.line(c, x='index', y='value', line_group='variable', hover_name='variable', color='variable')


if __name__ == '__main__':
    app.run_server(debug=True)
