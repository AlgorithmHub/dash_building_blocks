import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_building_blocks as dbb
import json

from _tools import NameGenerator
    
    
class Clone(dbb.Block):
    
    def parameters(self, modal, name=None):
        self.modal = modal
        self.name = name or dbb.util.generate_random_string(8)
        
    def layout(self):
        layout = html.Div(
            children=[
                self.modal.Button(
                    'Click me!',
                    id=self.register('button')
                ),
                html.Div(
                    self.name,
                    id=self.register('name'),
                    style={'display': 'none'}
                )
            ],
            className='col'
        )
        
        return layout

    
# import os
# app = dash.Dash(assets_folder=os.path.join(os.getcwd(),'assets'))
app = dash.Dash()
app.config.suppress_callback_exceptions = True

store = dbb.Store(app, hide=False)

modal = dbb.Modal(app)

clones = []

N_ROWS = 1
N_COLS = 12

namegen = iter(NameGenerator('_names.txt'))
            
def row_of_clones():
    
    _clones = [Clone(app, modal=modal, name=next(namegen)) 
              for _ in range(N_COLS)]
    clones.extend(_clones)
    
    return html.Div(
        [clone.layout for clone in _clones], 
        className='row'
    )

clone_rows = [row_of_clones() for _ in range(N_ROWS)]


switch = dbb.Switch(
    app,
    input=[
        clone.input('button', 'n_clicks') 
        for clone in clones
    ],
    state=[
        clone.state('name', 'children') 
        for clone in clones
    ]
)


app.layout = html.Div(
    clone_rows + [
        modal.layout,
        store.layout,
        switch.layout
    ],
    className='fluid-container'
)

switch.callbacks()

@app.callback(
    modal.output('body', 'children'),
    [switch.input('current')]
)
def update_modal_body(data):
    if data:
        name, n_clicks = data
        return 'Hi, my name is {}!'.format(name)


app.css.append_css({'external_url': [
    "https://stackpath.bootstrapcdn.com/bootstrap/4.1.1/css/bootstrap.min.css"
]})

app.scripts.append_script({"external_url": [
    "https://code.jquery.com/jquery-3.3.1.slim.min.js",
    "https://stackpath.bootstrapcdn.com/bootstrap/4.1.1/js/bootstrap.min.js"
]})

app.css.config.serve_locally = False
app.scripts.config.serve_locally = False

if __name__ == '__main__':
    app.run_server(debug=True, port=5000, host='0.0.0.0')