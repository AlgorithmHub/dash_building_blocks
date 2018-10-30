import dash
from dash.dependencies import Output, Input, State
import dash_html_components as html
import dash_core_components as dcc
import dash_building_blocks as dbb
import dash_building_blocks.experimental.common as dec
import json


EMPTY_MAP = {
    'data': [{
        'lon': [],
        'lat': [],
        'type': 'scattergeo'
    }],
    'layout': {}
}


def create_clones_app():

    N_CLONES = 10

    class Clone(dbb.Block):
        
        #pylint: disable=E0202
        def layout(self):
            return html.Div([
                html.Div('I am a clone.', self.register('div')),
                html.Button('Click Me!', self.register('button'))
            ])
        
        def callbacks(self, state_n_clones):
            
            #pylint: disable=W0612
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

    return app 


def create_location_app():

    class Map(dbb.Block):
        
        #pylint: disable=E0202
        def layout(self):
            return dcc.Graph(
                figure=EMPTY_MAP,
                id=self.register('map')
            )
        
        def callbacks(self, input_location):
            
            #pylint: disable=W0612
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

    store = dbb.Store(app, hide=False)

    map = Map(app)

    userinput = dec.InputForm(app, 
                            id='',
                            inputs=['longitude', 'latitude'],
                            form_id=store.register('user-input'))

    layout = html.Div(
        children=[map.layout, userinput.layout, store.layout]
    )

    app.layout = layout

    map.callbacks(store.input('user-input'))

    return app

apps = {
    'clones': create_clones_app,
    'location': create_location_app
}

if __name__ == '__main__':
    import sys

    app_name = None
    host = None
    port = None

    if len(sys.argv) == 1:
        raise Exception('Specify an app name: {}'.format(list(apps.keys())))
    if len(sys.argv) > 1:
        app_name = sys.argv[1]
    if len(sys.argv) > 2:
        host = sys.argv[2]
    if len(sys.argv) > 3:
        port = sys.argv[3]

    app = apps[app_name]()
    app.run_server(debug=True, port=port, host=host)

