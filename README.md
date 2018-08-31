# Dash Building Blocks

## Getting Started
#### examples/clones.py
The following example contains a Clone class that encapsulates the layout and callback of a "clone", inheriting the base class Block.
This allows the user to easily create as many "clones" as desired and resolve the many callbacks without having to wrestle with the long and mandatorily unique Dash component ids. The Block class does the dirty work behind the scenes, mapping the registered ids to the respective global Dash component ids.
~~~python
import dash
from dash.dependencies import Output, Input, State
import dash_html_components as html
import dash_core_components as dcc
import dash_building_blocks as dbb

N_CLONES = 10

class Clone(dbb.Block):
    
    def layout(self):
        return html.Div([
            html.Div('I am a clone.', self.register('div')),
            html.Button('Click Me!', self.register('button'))
        ])
    
    def callbacks(self, state_n_clones):
        
        @self.app.callback(
            self.output('div', 'children'),
            [self.input('button', 'n_clicks')],
            [self.state('div', 'children'),
             state_n_clones]
        )
        def update_clone_message(n_clicks, children, n_clones):
            if children == 'I am a clone.':
                return 'There are {} of us.'.format(n_clones)
            else:
                return 'I am a clone.'
            
app = dash.Dash()

clones = [Clone(app, id=str(i)) for i in range(N_CLONES)]

layout = html.Div(
    children=[
        html.Div(N_CLONES,
                 id='how-many-clones', 
                 style={'display': 'none'})
    ] + [
        clone.layout for clone in clones
    ]
)

app.layout = layout

for clone in clones:
    clone.callbacks(State('how-many-clones', 'children'))


if __name__ == '__main__':
    app.run_server(debug=True, port=5000, host='0.0.0.0')
~~~

#### examples/location.py
~~~python
import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_building_blocks as dbb
import json


EMPTY_MAP = {
    'data': [{
        'long': [],
        'lat': [],
        'type': 'scattergeo'
    }],
    'layout': {}
}


class Map(dbb.Block):
    
    def layout(self):
        return dcc.Graph(
            figure=EMPTY_MAP,
            id=self.register('map')
        )
    
    def callbacks(self, input_location):
        
        @self.app.callback(
            self.output('map', 'figure'),
            [input_location]
        )
        def update_map(location):
            
            location = json.loads(location)
            long = location['longitude']
            lat  = location['latitude']
            
            data = [dict(
                type = 'scattergeo',
                lon = [long],
                lat = [lat],
                text = 'Here!',
                mode = 'markers',
                marker = dict(
                    size = 8,
                    opacity = 0.8,
                    symbol = 'x',
                    line = dict(
                        width=1,
                        color='rgba(102, 102, 102)'
                    ),
                    color = 'red',
                )
            )]
            
            layout = dict(title='World Map')
                
            return dict(data=data, layout=layout)
        

app = dash.Dash()
app.config.suppress_callback_exceptions = True

datastore = dbb.DataBlock(app, hide=True)

map = Map(app)

userinput = dbb.InputForm(app, 
                          id='location', 
                          inputs=['longitude', 'latitude'],
                          form_id='user-input',
                          db=datastore)

layout = html.Div(
    children=[map.layout, userinput.layout, datastore.layout]
)

app.layout = layout

map.callbacks(datastore.input('user-input'))


if __name__ == '__main__':
    app.run_server(debug=True, port=5000, host='0.0.0.0')
~~~
