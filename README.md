# Dash Building Blocks

## Getting Started
#### examples/clones.py
The following example contains a Clone class that encapsulates the layout and callback of a "clone", inheriting the base class Block.
This allows the user to easily create as many "clones" as desired and resolve the many callbacks without having to wrestle with the long and mandatorily unique Dash component ids. The Block class does all the dirty work behind the scenes, mapping the registered ids to the respective global Dash component ids.
~~~python
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Output, Input, State
from dash_building_blocks import Block

N_CLONES = 10

class Clone(Block):
    
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
