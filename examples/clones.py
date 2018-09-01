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