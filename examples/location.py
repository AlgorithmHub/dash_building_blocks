import sys
sys.path.append('/workspace/dash_building_blocks')

import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Output, Input, State
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

datastore = dbb.DataBlock(app, hide=False)

map = Map(app)

userinput = dbb.InputForm(app,
                          inputs=['longitude', 'latitude'],
                          form_id=datastore.add('user-input'))

layout = html.Div(
    children=[map.layout, userinput.layout, datastore.layout]
)

app.layout = layout

map.callbacks(datastore.input('user-input'))


if __name__ == '__main__':
    app.run_server(debug=True, port=5000, host='0.0.0.0')