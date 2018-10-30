import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html

import quandl

app = dash.Dash('Hello World')

app.layout = html.Div([
    dcc.Dropdown(
        id='my-dropdown',
        options=[
            {'label': 'Poxel', 'value': 'EURONEXT/POXEL'},
            {'label': 'Orange', 'value': 'EURONEXT/ORA'},
            {'label': 'TechnipFMC', 'value': 'EURONEXT/FTI'}
        ],
        value='EURONEXT/POXEL'
    ),
    dcc.Graph(id='my-graph')
], style={'width': '500'})

@app.callback(
    Output('my-graph', 'figure'), 
    [Input('my-dropdown', 'value')])
def update_graph(selected_dropdown_value):
    df = quandl.get(selected_dropdown_value)
    return {
        'data': [{
        'x': df.index,
        'y': df.Last
        }],
        'layout': {'margin': {'l': 40, 'r': 0, 't': 20, 'b': 30}}
    }

app.css.append_css({'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'})

.. image:: ../images/example-dash.gif

Multi Graph Adaptation
^^^^^^^^^^^^^^^^^^^^^^
Using ``dash_building_blocks``, we can easily adapt the above example to
create multiple graphs by defining a block that encapsulates the functionality
of a single graph.
::

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_building_blocks as dbb

import quandl

class Graph(dbb.Block):
    
    def layout(self):
        return html.Div([
            dcc.Dropdown(
                id=self.register('dropdown'),
                options=self.data.options,
                value=self.data.value
            ),
            dcc.Graph(id=self.register('graph'))
        ], style={'width': '500'})
    
    def callbacks(self):
        @self.app.callback(
            self.output('graph', 'figure'), 
            [self.input('dropdown', 'value')]
        )
        def update_graph(selected_dropdown_value):
            df = quandl.get(selected_dropdown_value)
            return {
                'data': [{
                'x': df.index,
                'y': df.Last
                }],
                'layout': {'margin': {'l': 40, 'r': 0, 't': 20, 'b': 30}}
            }
    
app = dash.Dash('Hello World')

options=[
    {'label': 'Poxel', 'value': 'EURONEXT/POXEL'},
    {'label': 'Orange', 'value': 'EURONEXT/ORA'},
    {'label': 'TechnipFMC', 'value': 'EURONEXT/FTI'}
]

data = {
    'options': options,
    'value': 'EURONEXT/POXEL'
}

n_graphs = 2
graphs = [Graph(app, data) for _ in range(n_graphs)]

app.layout = html.Div(
    [html.Div(graph.layout, className='six columns')
    for graph in graphs],
    className='container'
)

for graph in graphs:
    graph.callbacks()

app.css.append_css({'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'})

if __name__ == '__main__'
    app.run_server()