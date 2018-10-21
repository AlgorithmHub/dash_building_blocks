import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash_building_blocks.util import (
    generate_random_string,
    decamelify
)

from dash_building_blocks.error import (
    ProhibitedParameterError
)

class Data:
    
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        

    @classmethod
    def from_dict(cls, d):
        d = d or {}
        return cls(**d)
        

    def to_dict(self):
        return self.__dict__
        

    def __getitem__(self, key):
        return getattr(self, key)
    

    def __setitem(self, key, val):
        setattr(self, key, val)
    

    def __repr__(self):
        return repr(self.to_dict())
    

    def __bool__(self):
        return bool(self.__dict__)

        
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

    sacred_attrs = ['app', 'data', 'base_id', 'ids', 'layout', '_uid']

    def __init__(self, app=None, data=None, id=None, **kwargs):

        if id is None:
            self._uid = generate_random_string(16)
        else:
            self._uid = id
        
        self.app = app
        self.data = Data.from_dict(data)
        self.base_id = self.block_id()
        self.ids = {'this': self._determine_this_id(self.base_id, self._uid)}
        
        self.parameters(**kwargs)
        self.layout = self.layout()
        
    def _determine_this_id(self, base_id, uid):
        if uid == '':
            return base_id
        else:
            return base_id + '-' + uid
        
    def parameters(self, **kwargs):
        for key, val in kwargs.items():
            if key in self.sacred_attrs:
                raise ProhibitedParameterError(
                    'Cannot define "{}" parameter as it would'
                    ' override necessary internal attribute'
                    .format(key))
            else:
                setattr(self, key, val)
        
        
    def block_id(self):
        return decamelify(self.__class__.__name__)

    # pylint: disable=E0202
    def layout(self):
        raise NotImplementedError


    def callback(self, *args, **kwargs):
        return self.app.callback(*args, **kwargs)
        
        
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
        self._uid = id
        self.ids = {'this': self._uid}
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