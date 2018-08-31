from dash.dependencies import Output, Input, State
import dash_html_components as html
import dash_core_components as dcc
from dash_building_blocks import Block
import json


class InputForm(Block):
    
    def parameters(self, inputs, form_id=None):
        self.inputs = inputs
        self.form_id = form_id or self('form-data')
        
    def pack_inputs(self, id, input, state=None):
        state = state or []
        
        def update(*args):
            args = args[1:]
            return json.dumps({
                k: v for k, v in zip(self.inputs, args)
            })
            
        self.app.callback(
            Output(id, 'children'),
            [Input(*i) for i in input], 
            [State(*s) for s in state]
        )(update)
        
    def layout(self):
        layout = html.Div([
            html.Div([html.Div(input), 
                      dcc.Input(id=self.register(input),type='text')])
            for input in self.inputs
        ] + [
            html.Button('Submit', id=self.register('submit-button'))
        ])
        self.pack_inputs(self.form_id, 
                         input=[self('submit-button', 'n_clicks')],
                         state=[self(input, 'value') for input in self.inputs])
        
        return layout
    

class Collapsable(Block):
    
    def parameters(self, position=None, buttontext=None, children=None):
        self.position = position or 'top' # TODO: implement different positions
        self.children = children or html.Div()
        self.buttontext = buttontext or ''
    
    def layout(self):
        content = html.Div(
            children=self.children,
            id=self('content')
        )
        button = html.Button(self.buttontext, id=self('button'))
        
        togglable(self.app, self('content'), self('button'), 
                  dependency='button', init_hidden=True)
        return html.Div([content, button])
        
    
def togglable(app, 
              content_id,
              toggle_id,
              display_style={'display': 'block'},
              toggle_on=None,
              toggle_off=None,
              dependency='tabs',
              init_hidden=False):
    
    if 'tabs' in dependency:
        assert(toggle_on or toggle_off)

    dependency_output = Output(content_id, 'style')
    dependency_inputs = []
    
    if dependency == 'button':
        
        assert(isinstance(toggle_id, str))
        
        dependency_inputs.append(Input(toggle_id, 'n_clicks'))
        
        def toggle_content_display(n_clicks):
            if (n_clicks or 0) % 2 == int(init_hidden):
                return display_style
            else:
                return {'display': 'none'}
        
    elif dependency == 'tabs':

        assert(isinstance(toggle_id, str))

        dependency_inputs.append(Input(toggle_id, 'value'))

        if toggle_on:
            def toggle_content_display(value):
                if value in toggle_on:
                    return display_style
                else:
                    return {'display': 'none'}
        else:
            def toggle_content_display(value):
                if value not in toggle_off:
                    return display_style
                else:
                    return {'display': 'none'}

    elif dependency == 'tabs+button':

        assert(isinstance(toggle_id, list) and len(toggle_id) == 2)

        dependency_inputs.append(Input(toggle_id[0], 'value'))
        dependency_inputs.append(Input(toggle_id[1], 'n_clicks'))

        if toggle_on:
            def toggle_content_display(value, n_clicks):
                if value in toggle_on:
                    if n_clicks is None:
                        return display_style
                    elif n_clicks % 2 == int(init_hidden):
                            return display_style
                return {'display': 'none'}
        if toggle_off:
            def toggle_content_display(value, n_clicks):
                if value not in toggle_off:
                    if n_clicks is None:
                        return display_style
                    elif n_clicks % 2 == int(init_hidden):
                            return display_style
                return {'display': 'none'}
    else:
        raise ValueError('Unknown dependency argument: {}\nKnown values for dependency: {}'
                         .format(dependency, ['tabs', 'tabs+button', 'button']))

    app.callback(dependency_output, dependency_inputs)(toggle_content_display)