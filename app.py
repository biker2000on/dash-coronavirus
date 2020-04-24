import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import pandas as pd
import requests as r

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

data = r.get('https://corona.lmao.ninja/v2/historical', params={'lastdays': 'all'})
df = pd.read_json(data.text)
df['timeline'] = df.apply(lambda x: pd.DataFrame(x.timeline), axis=1)

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    dcc.Graph(figure={
        'data': [dict(
            x=z.timeline.index,
            y=z.timeline.cases,
            name=z.country
        ) for k,z in df.iterrows()],
        'layout': {
            'hovermode': 'closest'
        }
    })
])

if __name__ == '__main__':
    app.run_server(debug=True)
