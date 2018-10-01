import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_building_blocks as dbb
import json
# import numpy as np
        
    
class MultiSelect(dbb.Block):
    
    def parameters(self, options):
        self.options = options
        self.sat_idx = 0
    
    def layout(self):
        return dcc.Dropdown(
            options=self.options,
            multi=True,
            id=self.register('selection')
        )
    
    # observer
    def Satellite(self):
        
        sat_idx = self.sat_idx
        sat_id = 'sat-{}'.format(sat_idx)
        sat = html.Div('', id=self.register(sat_id))
        
        @self.app.callback(
            self.output(sat_id),
            [self.input('selection', 'value')]
        )
        def update_sat(selection):
            if selection and sat_idx < len(selection):
                return selection[sat_idx]
            
        self.sat_idx += 1
        
        return sat

    
    
app = dash.Dash()
app.config.suppress_callback_exceptions = True


# store = dbb.Store(app, hide=True)

# opts = ['Hello', 'World', 'Goodbye']
opts = [
    'lambda: np.random.beta(10, 10, size=N)',
    'lambda: np.random.lognormal(size=N)',
    'lambda: np.random.chisquare(10, size=N)',
    'lambda: np.random.geometric(0.5, size=N)',
    'lambda: np.random.gumbel(size=N)',
    'lambda: np.random.normal(size=N)',
    'lambda: np.random.pareto(2, size=N)',
    'lambda: np.random.laplace(size=N)'
]

options = [{'label': l, 'value': v}
           for l, v in zip(opts, opts)]

select = MultiSelect(app, options=options)

app.layout = html.Div(
    [
        select.layout
    ] + [
        select.Satellite() for opt in opts
    ]
)

if __name__ == '__main__':
    app.run_server(debug=True, port=5000, host='0.0.0.0')