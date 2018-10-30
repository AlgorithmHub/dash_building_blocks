import dash
from dash.dependencies import Input, Output, State
import dash_html_components as html
import dash_core_components as dcc
import dash_building_blocks as dbb
import json

    
class Map(dbb.Block):
    
    def layout(self):
        return dcc.Graph(
            figure=dict(data=[], layout={}),
            id=self.register('map')
        )
    
    def callbacks(self, input_location):
        
        @self.app.callback(
            self.output('map', 'figure'),
            [input_location]
        )
        def update_map(location):
            
            location = json.loads(location)
            lon = location['longitude']
            lat  = location['latitude']
            
            data = [dict(
                type = 'scattergeo',
                lon = [lon],
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

map = Map(app)

coords = ['longitude', 'latitude']

input_layout = html.Div(
    [
        html.Div([html.Div(coord), dcc.Input(id=coord, type='text')])
        for coord in coords
    ] + [
        html.Button('Submit', id='submit-button')
    ]
)

store = dbb.Store(app)

@store.register(
    'form', 
    inputs=[Input('submit-button', 'n_clicks')],
    state=[State(coord, 'value') for coord in coords]
)
def update_form(n_clicks, lon, lat):
    return json.dumps({
        'longitude': lon, 
        'latitude': lat
    })

layout = html.Div(
    children=[map.layout, input_layout, store.layout]
)

app.layout = layout

map.callbacks(store.input('form'))

if __name__ == '__main__':
    app.run_server()