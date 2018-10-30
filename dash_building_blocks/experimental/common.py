from dash.dependencies import Output, Input, State
import dash_html_components as html
import dash_core_components as dcc
from dash_building_blocks.base import Block, Store
import json


class InputForm(Block):
    
    def parameters(self, inputs, form_id=None, submit='Submit'):
        self.inputs = inputs
        if form_id is None:
            self.form_id = self.register('form')
            self._contains_form = True
        else:
            self.form_id = form_id
            self._contains_form = False
        
        self.submit = submit
        
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

    # pylint: disable=E0202    
    def layout(self):
        children = [
            html.Div([html.Div(input), 
                      dcc.Input(id=self.register(input), type='text')])
            for input in self.inputs
        ]
        
        if self.submit:
            children.append(
                html.Button(self.submit, id=self.register('submit-button'))
            )
            
            if self._contains_form:
                children.append(html.Div('',
                                         id=self('form'),
                                         style={'display': 'none'}))

            self.pack_inputs(self.form_id, 
                             input=[self('submit-button', 'n_clicks')],
                             state=[self(input, 'value') for input in self.inputs])
        
        return html.Div(children)
    
    
class Modal(Block):
    
    def parameters(self, title=None, body=None, buttons=None):
        
        if buttons is None:
            buttons = {}
            
        self.title = title or ''
        self.body = body or ''
        self.primary_button = buttons.get('primary')
        self.secondary_button = buttons.get('secondary')
    
    # pylint: disable=E0202    
    def layout(self):
        
        modal_title = html.H5(
            self.title,
            className='modal-title',
            id=self.register('label')
        )
        
        close_btn_head = html.Button(
            html.Span('×', **{'aria-hidden': 'true'}),
            **{'type':'button', 
            'className':'close', 
            'data-dismiss':'modal',
            'aria-label':'Close',
            'id': self.register('close')}
        )
        
        modal_header = html.Div(
            [ modal_title, close_btn_head ],
            className='modal-header'
        )
        
        modal_body = html.Div(
            self.body,
            className='modal-body',
            id=self.register('body')
        )
        
        footer_buttons = []
        
        if self.secondary_button:
            sec_btn = html.Button(
                self.secondary_button,
                **{'type': 'button',
                'className': 'btn btn-secondary',
                'data-dismiss': 'modal',
                'id': self.register('secondary')}
            )
            footer_buttons.append(sec_btn)
            
        if self.primary_button:
            prim_btn = html.Button(
                self.primary_button,
                **{'type': 'button',
                'className': 'btn btn-primary',
                'id': self.register('primary')}
            )
            footer_buttons.append(prim_btn)
        
        modal_footer = html.Div(
            footer_buttons,
            className='modal-footer',
        )
        
        modal_content = html.Div(
            [ modal_header, modal_body, modal_footer ],
            className='modal-content'
        )
        
        modal_dialog = html.Div(
            html.Div(
                modal_content,
                className='modal-dialog',
                role='document'
            ),
            **{'className': 'modal fade',
            'id': self.register('modal'),
            'tabIndex': '-1',
            'role': 'dialog',
            'aria-labelledby': self('label'),
            'aria-hidden': 'true'}
        )
        
        return modal_dialog
    
    def Button(self, children='', id=None):
        trigger_btn = html.Button(
            children,
            **{'type': 'button',
            'className': 'btn btn-primary',
            'data-toggle': 'modal',
            'data-target': '#{}'.format(self('modal')),
            'id': id}
        )
        return trigger_btn
    

class Switch(Block):

    def parameters(self, input, state=None):
        self.inputs = input
        self.states = state or []
        
    def layout(self):
        layout = html.Div(
            [ html.Div('', id=self.register('data')), 
              html.Div('', id=self.register('current')) ],
            style={'display': 'none'}
        )
        
        return layout
    
    def callbacks(self):
        
        if self.states:
        
            def update_data(*args):

                current_data = args[-1]

                args = args[:-1]
                n_inputs = int(len(args) / 2)
                clicks = args[:n_inputs]
                names = args[n_inputs:]

                medium_data = {n: c for n, c in zip(names, clicks)}

                if current_data:
                    current_data = json.loads(current_data)

                    diff = {k: medium_data[k] 
                            for k in medium_data
                            if k != 'updated' and medium_data[k] != current_data[k]}

                    medium_data['updated'] = diff

                return json.dumps(medium_data)

            def update_current(data):
                data = json.loads(data)
                updated = data.get('updated')
                if updated:
                    curr = list(updated.items())[0]
                    return curr
        
        else:
        
            def update_data(*args):

                current_data = args[-1]

                values = args[:-1]

                medium_data = {'values': [val for val in values]}

                if current_data:
                    current_data = json.loads(current_data)

                    diff = [val
                            for val, curr_val in zip(medium_data['values'], 
                                                     current_data['values'])
                            if val != curr_val]

                    medium_data['updated'] = diff

                return json.dumps(medium_data)

            def update_current(data):
                data = json.loads(data)
                updated = data.get('updated')
                curr = updated[0]
                return curr
            
        self.app.callback(
            self.output('data'),
            inputs=self.inputs,
            state=self.states + [self.state('data')]
        )(update_data)


        self.app.callback(
            self.output('current'),
            [self.input('data')]
        )(update_current)
    
    
class Collapsable(Block):
    
    def parameters(self, position=None, buttontext=None, children=None):
        self.position = position or 'top' # TODO: implement different positions
        self.children = children or html.Div()
        self.buttontext = buttontext or ''
    
    # pylint: disable=E0202    
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