import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_building_blocks as dbb
import json
import numpy as np


EMPTY_FIGURE = {'data':[], 'layout':{}}


class Graph(dbb.Block):
    
    def layout(self):
        
        return dcc.Graph(
            id=self.register('graph'),
            config={
                'displayModeBar': False
            },
            figure=EMPTY_FIGURE
        )
    
    
    def callbacks(self, input_new_data):
        
        @self.app.callback(
            self.output('graph', 'figure'),
            [input_new_data]#, input_new_layout]
        )
        def update_graph_figure(new_data):
            
            new_data = json.loads(new_data)
            
            data = [{
                'x': new_data['x'],
                'y': new_data['y'],
                'mode': 'markers'
            }]
            
            fig = dict(data=data, layout={})
            
            return fig
      
    
class NumberGenerator(dbb.Block):
    
    def parameters(self, generate_numbers, data_id=None, button=None):
        
        self.genf = generate_numbers
        self.data_id = data_id or 'data'
        self.buttontext = button or 'Generate New Data'
    
    
    def layout(self):
        
        layout = html.Div([
            html.Button(
                self.buttontext,
                id=self.register('button')
            ),
            html.Div(
                id=self.register(self.data_id),
                style={'display': 'none'}
            )
        ])
        
        @self.app.callback(
            self.output(self.data_id, 'children'),
            [self.input('button', 'n_clicks')]
        )
        def generate_new_numbers(n_clicks):
            return list(self.genf())
        
        return layout
    
    
class RatingForm(dbb.Block):
    
    def layout(self):
        
        avail_ratings = [1, 2, 3, 4, 5]
        
        options = [
            {'label': r, 'value': r}
            for r in avail_ratings
        ]
        
        return dcc.Dropdown(options=options, 
                            id=self.register('rating'))
    

class Feedback(dbb.Block):
    
    def layout(self):
        
        return html.Div([
            html.H5('Rating:'),
            html.Div('', id=self.register('rating')),
            html.H5('Comments:'),
            html.Div('', id=self.register('comments'))
        ])
    
    
    def callbacks(self, input_button, state_rating, state_comments):
        
        @self.app.callback(
            self.output('rating', 'children'),
            [input_button], [state_rating]
        )
        def update_current_rating(n_clicks, rating):
            return rating
        
        @self.app.callback(
            self.output('comments', 'children'),
            [input_button], [state_comments]
        )
        def update_current_comments(n_clicks, comments):
            return comments
        
        
def make_graph_section(app, fx, fy=None, modal_title='Rate This Graph'):
    
    if fy is None:
        fy = fx
    
    store = dbb.Store(app, id=dbb.util.generate_random_string(8))
    
    graph = Graph(app)
    
    xgen = NumberGenerator(app,
                           data_id='numbers',
                           button='Generate X Data',
                           generate_numbers=fx)

    ygen = NumberGenerator(app,
                           data_id='numbers',
                           button='Generate Y Data',
                           generate_numbers=fy)
    
    ratingform = RatingForm(app)
    
    # TODO: make defining inputs like defining dcc.Dropdown options
    ratingcomment = dbb.InputForm(app, inputs=['Comments'], submit=None)
    
    modal = dbb.Modal(app, 
                      title=modal_title, 
                      body=[ratingform.layout, 
                            ratingcomment.layout],
                      buttons=dict(primary='Save Changes',
                                   secondary='Close'))
    
    feedback = Feedback(app)
    
    @store.register(
        'plot-data',
        [xgen.input('numbers'), # == xgen.input('numbers', 'children')
         ygen.input('numbers')] # == ygen.input('numbers', 'children')
    )
    def update_data(x, y):
        return json.dumps(dict(x=x, y=y))
    
    graph.callbacks(store.input('plot-data'))

    feedback.callbacks(
        input_button=modal.input('primary', 'n_clicks'),
        state_rating=ratingform.state('rating', 'value'),
        state_comments=ratingcomment.state('Comments', 'value')
    )
    
    return html.Div(
        [
            html.Div(
                [
                    html.Div(modal.Button('Rate'), className='col-3'),
                    html.Div(ygen.layout, className='col-3'), 
                    html.Div(xgen.layout, className='col-3'),
                    html.Div('', className='col-3')
                ], className='row'),
            
            modal.layout,
            graph.layout,
            feedback.layout,
            store.layout
        ]
    )
    

    
app = dash.Dash()
app.config.suppress_callback_exceptions = True


store = dbb.Store(app, hide=True)

N = 100

functions = [
    lambda: np.random.beta(10, 10, size=N),
    lambda: np.random.lognormal(size=N),
    lambda: np.random.chisquare(10, size=N),
    lambda: np.random.geometric(0.5, size=N),
    lambda: np.random.gumbel(size=N),
    lambda: np.random.normal(size=N),
    lambda: np.random.pareto(2, size=N),
    lambda: np.random.laplace(size=N)
]


def make_graphs_row(functions):
    
    graph_sections = [
        html.Div(
            make_graph_section(app, f),
            className='col'
        )
        for f in functions
    ]

    return html.Div(graph_sections, className='row')
    

app.layout = html.Div([make_graphs_row(functions[:4]),
                       html.Hr(),
                       make_graphs_row(functions[4:])],
                      className='container-fluid')


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
            