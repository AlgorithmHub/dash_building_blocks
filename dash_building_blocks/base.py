import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash_building_blocks.util import generate_random_string

def _camelify(name, delims=None):
    
    delims = delims or ['-', '_']
    chars = []
    headsup = False
    
    for c in name:
        if headsup:
            chars.append(c.upper())
            headsup = False
        elif c in delims:
            headsup = True
        else:
            chars.append(c)
            
    return ''.join(chars)

            
def _decamelify(name, delim='-'):
    
    chars = [name[0].lower()]
    
    for c in name[1:]:
        if c == c.upper():
            chars.append(delim)
            chars.append(c.lower())
        else:
            chars.append(c)
            
    return ''.join(chars)


class DataWrapper:
    
    def __init__(self, data=None):
        self.data = data or {}
        
        
    def __getitem__(self, key):
        return self.data[key]
        
        
    def __getattr__(self, key):
        if key == 'data':
            return self.data
        else:
            return self.data[key]

        
class Component:
    
    def __init__(self, id):
        self.id = id
        
        
    def output(self, key):
        return Output(self.id, key)
    
    
    def input(self, key):
        return Input(self.id, key)
    
    
    def state(self, key):
        return State(self.id, key)
        
        
    def __getitem__(self, key):
        return (self.id, key)
    
    
class Block:

    def __init__(self, app=None, data=None, id=None, **kwargs):
        
        if id is None:
            id = generate_random_string(16)
        
        self.app = app
        self.data = DataWrapper(data)
        self.base_id = self.block_id()
        self.ids = {'this': self.base_id + id}
        
        self.parameters(**kwargs)
        self.layout = self.layout()
        
        
    def parameters(self, **kwargs):
        pass
        
        
    def block_id(self):
        return _decamelify(self.__class__.__name__)

    
    def layout(self):
        raise NotImplementedError
        
        
    def callbacks(self):
        pass

    
    def register(self, id, full_id=None, ext=''):
        if full_id is None:
            if ext:
                ext = '-' + str(ext)
            full_id = '{}-{}{}'.format(self.ids['this'], id, ext)
        self.ids.update({id: full_id})
        return full_id
    
    
    def __getitem__(self, key):
        return Component(self.ids[key])
    
    
    def __call__(self, component_id, property_id=None):
        
        if component_id not in self.ids:
            self.register(component_id)
            
        if property_id is None:
            return self.ids[component_id]
        else:
            return self[component_id][property_id]
    
    
    def output(self, component_id, component_property=None):
        component_property = component_property or 'children'
        return self[component_id].output(component_property)
    
    
    def input(self, component_id, component_property=None):
        component_property = component_property or 'children'
        return self[component_id].input(component_property)
    
    
    def state(self, component_id, component_property=None):
        component_property = component_property or 'children'
        return self[component_id].state(component_property)
    
    
class Store:
    
    def __init__(self, app, id='', hide=True):
        
        self.app = app
        self.ids = {'this': id}
        self.items = {}
        self.hide = hide
        
        
    @property
    def layout(self):
        style = {'display': 'none'} if self.hide else None
        return html.Div([
            html.Div([html.Div('{}: '.format(id),
                               style={'fontWeight': 'bold'}),
                      html.Div(initially, id=self.ids[id])])
            for id, initially in self.items.items()
        ], style=style)
        
        
    def _register(self, id):
        prefix = self.ids['this']
        prefix = (prefix + '-') if prefix else prefix
        full_id = prefix + id
        self.ids.update({id: full_id})
        return full_id

    
    def register(self, id, input=None, state=None, initially=''):
        full_id = self._register(id)
        print('{} -> {}'.format(id, full_id))
        self.items[id] = initially
        if input is None:
            return full_id
        else:
            state = state or []
            def deco(cbfunc):
                self.app.callback(
                    self.output(id), input, state
                )(cbfunc)

            return deco
    
    
    def get(self, key):
        return self.ids[key], 'children'
    
    
    def __getitem__(self, key):
        return self.get(key)
    
    
    def output(self, key):
        return Output(*self.get(key))
    
    
    def input(self, key):
        return Input(*self.get(key))
    
    
    def state(self, key):
        return State(*self.get(key))