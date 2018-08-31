from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
import plotly.graph_objs as go


SAMPLE_FIGURE = {
    'data': [{
        'x': [],
        'y': [],
        'type': 'bar'
    }],
    'layout': {}
}


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


class Data:
    
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

    def __init__(self, app=None, data=None, id='', **kwargs):
        self.parameters(**kwargs)
        self.app = app
        self.data = Data(data)
        self.base_id = self.block_id()
        self.ids = {'this': self.base_id + id}
        self.layout = self.layout()
        self._callbacks = self._set_callbacks()
        self._dependencies = self._set_deps(self._callbacks)
        
    def parameters(self, **kwargs):
        pass
        
    def block_id(self):
        return _decamelify(self.__class__.__name__)

    def layout(self):
        raise NotImplementedError
        
    def callbacks(self):
        pass
    
    def _set_callbacks(self):
        _callbacks = {}
        for attr in dir(self):
            cbstr = 'callback_'
            findcb = attr.find(cbstr)
            if findcb == 0:
                cbname = attr[len(cbstr):]
                try:
                    comp, prop = cbname.split('_')
                except:
                    raise Exception('{} does not follow expected callback'
                                    ' naming format'.format(attr))
                mod_f = getattr(self, attr)
                deps = mod_f()['deps']
                cbfunc = mod_f()['func']
                def _cbfunc(*args):
                    return cbfunc(self, *args)
                _cbfunc.__name__ = cbfunc.__name__
                print(comp, prop)
#                 print(cbfunc.__name__)
#                 print(deps)
                _callbacks[cbname] = {'input': deps['input'],
                                      'state': deps['state'],
                                      'func': _cbfunc}
        return _callbacks
                    
    def _set_deps(self, callbacks):
        _dependencies = {}
        for out, deps in (callbacks or {}).items():
            for idep in deps['input']:
                _dependencies.update({idep: None})
            for sdep in deps.get('state', []):
                _dependencies.update({sdep: None})
        return _dependencies
    
    def _extract_callback_details(self, cbitem):
        name, details = cbitem
        try:
            comp, prop = name.split('_')
        except:
            raise Exception('"callback_{}" does not follow expected'
                            ' naming format'.format(name))
        try:
            yield Output(self.ids[comp], prop)
        except KeyError:
            yield Output(self.ids[_decamelify(comp)], prop)
        yield [Input(*self._dependencies[idep]) for idep in details['input']]
        yield [State(*self._dependencies[sdep]) for sdep in details.get('state', [])]
        yield details['func']
        
    @staticmethod
    def require(input, state=None):
        if not isinstance(input, list):
            input = [input]
        if state is None:
            state = []
        elif not isinstance(state, list):
            state = [state]
            
        def decofunc(cbfunc):
            def _modified_cbfunc(self):
                return {'deps': dict(input=input, state=state), 
                        'func': cbfunc}
            return _modified_cbfunc
        return decofunc
        
    def resolve(self, deps):
        assert all([dep in self._dependencies.keys() for dep in deps.keys()])
        self._dependencies.update(deps)
        all_deps_defined = all([val is not None
                                for dep, val in self._dependencies.items()])
        if all_deps_defined:
            for cb in self._callbacks.items():
                output, input, state, func = self._extract_callback_details(cb)
                print('Defining {} callback'.format(func.__name__))
                self.app.callback(output, input, state)(func)

    def register(self, id, full_id=None):
        if full_id is None:
            full_id = '{}-{}'.format(self.ids['this'], id)
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
    
    def output(self, component_id, component_property):
        return self[component_id].output(component_property)
    
    def input(self, component_id, component_property):
        return self[component_id].input(component_property)
    
    def state(self, component_id, component_property):
        return self[component_id].state(component_property)




