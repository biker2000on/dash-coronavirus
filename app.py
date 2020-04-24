import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.express as px
import pandas as pd
import requests as r

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

data = r.get('https://corona.lmao.ninja/v2/historical',
             params={'lastdays': 'all'})
df = pd.read_json(data.text)

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


def addcolumns(row):
    dff = pd.DataFrame(row.timeline)
    dff = dff.assign(
        **{'dailycases': 0, 'dailydeaths': 0, 'dailyrecovered': 0})
    dff['country'] = row.country
    dff['province'] = row.province
    for i in range(1, len(dff)):
        dff.iloc[i, 3] = dff.iloc[i, 0] - dff.iloc[i-1, 0]
        dff.iloc[i, 4] = dff.iloc[i, 1] - dff.iloc[i-1, 1]
        dff.iloc[i, 5] = dff.iloc[i, 2] - dff.iloc[i-1, 2]
    return dff


df['timeline'] = df.apply(addcolumns, axis=1)
flat = pd.concat(list(df.timeline)).reset_index()

fig = px.line(flat, x='index', y='dailycases',
              line_group='country', hover_name='country')
options = list(flat.columns)

app.layout = html.Div([
    dcc.Dropdown(id='chart-type',
                 options=[{'label': i, 'value': i} for i in options],
                 value='dailycases'
                 ),
    dcc.Graph(id='chart')
])


@app.callback(
    Output('chart', 'figure'),
    [Input('chart-type', 'value')]
)
def changeChart(chartType):
    return px.line(flat, x='index', y=chartType, line_group='country', hover_name='country', color='country')


if __name__ == '__main__':
    app.run_server(debug=True)
