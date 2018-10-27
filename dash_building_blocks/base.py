"""The :mod:`~dash_building_blocks.base` module provides the virtual
:class:`~dash_building_blocks.base.Block` class used as a base class for 
"block" objects, and the :class:`~dash_building_blocks.base.Store` class,
which is a convenient adaptation of the :class:`~dash_building_blocks.base
.Store` used for client-side data storage. This module also includes the 
:class:`~dash_building_blocks.base.Data` and :class:`~dash_building_blocks
.base.Component` classes but these were not implemented with the intention 
of being relevant outside of this module.
"""


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
    r"""Convenience class that wraps a :class:`dict` object so keys may be
    accessed as attributes.

    :param \**kwargs: Keyword arguments are set as class attributes.
    """
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        

    @classmethod
    def from_dict(cls, d):
        """Create a :class:`Data` object from a :class:`dict` object ``d``.

        :param dict d: The data dictionary.
        :return: The Data object wrapping the data dictionary.
        :rtype: Data
        """
        d = d or {}
        return cls(**d)
        

    def to_dict(self):
        """Convert this to a :class:`dict` object.

        :return: The converted dictionary.
        :rtype: dict
        """
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
    """The Component class. """
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
    """The Block virtual class.
    
    :param dash.Dash app: The Dash app object.
    :param dict data: The data :class:`dict` that will be wrapped as the\
    :attr:`data` :class:`Data` attribute.
    :param str id: The id unique to the block object. If None, it will be`\
    generated internally using\
    :func:`~dash_building_blocks.util.generate_random_string`.
    :param \**kwargs: Extra keyword arguments are processed by\
    :meth:`parameters`.
    """
    sacred_attrs = ['app', 'data', 'class_id', 'ids', 'layout', '_uid']

    def __init__(self, app=None, data=None, id=None, **kwargs):

        if id is None:
            self._uid = generate_random_string(16)
        else:
            self._uid = id
        
        self.app = app
        self.data = Data.from_dict(data)
        self.class_id = self.class_id()
        self.ids = {'this': self._determine_this_id(self.class_id, self._uid)}
        
        self.parameters(**kwargs)
        self.layout = self.layout()
        
    @property
    def id(self):
        """The id representing the "namespace" of the block object. It is
        determined as follows: ``'{}-{}'.format(block.class_id, block._uid)``
        , where :attr:`_uid` is the unique block id assigned to the block
        object during initialization. 
        """
        return self.ids['this']

    def _determine_this_id(self, class_id, uid):
        if uid == '':
            return class_id
        else:
            return class_id + '-' + uid
        
    def parameters(self, **kwargs):
        """Sometimes, it may be desired to pass in arguments that are
        separate from :attr:`data`. For this, additional keyword arguments
        (``**kwargs``) passed to :meth:`~dash_building_blocks.base.Block.
        __init__` will be processed through this method. By default, it will
        simply update :attr:`__dict__` with ``kwargs``.
        
        :param \**kwargs: The keyword arguments.

        .. warning: If a core ``Block`` attribute were to be overwritten by a 
           keyword argument, a :exp:`ProhibitedParameterError` will be raised.
        """
        for key, val in kwargs.items():
            if key in self.sacred_attrs:
                raise ProhibitedParameterError(
                    'Cannot define "{}" parameter as it would'
                    ' override necessary internal attribute'
                    .format(key))
            else:
                setattr(self, key, val)
        
        
    # pylint: disable=E0202
    def class_id(self):
        """Define the id unique to the block class. By default,
        this will be the result of 
        :func:`~dash_building_blocks.util.decamelify`\ ing 
        :attr:`__class__.__name__`, so it is only optionally
        overriden if a custom class id is desired. Similar to :meth:`layout`,
        it becomes an attribute with the same name, :attr:`class_id`.

        :return: The string representing the block class id
        """
        return decamelify(self.__class__.__name__)


    # pylint: disable=E0202
    def layout(self):
        """Define the block layout. Remember, :class:`Block` is a virtual 
        class, with this being the
        one method that must be overriden when subclassing to create a
        valid block class. At initialization, the returned layout will become
        the :attr:`layout` attribute of the instantiated block.
        
        :return: The block layout, composed of Dash components.
        """
        raise NotImplementedError


    def callback(self, *args, **kwargs):
        """Convenience method that acts as an alias for :attr:`app.callback`
        """
        return self.app.callback(*args, **kwargs)
        
        
    def callbacks(self):
        pass

    
    def register(self, local_id, global_id=None, ext=''):
        """Register a *local_id* to be mapped to *global_id*. If global_id
        is not provided, it is determined internally as the following:
        ``'{}-{}-{}'.format(block.class_id, block._uid, local_id)``. If *ext*
        is is not empty, it will be appended to the global_id such that:
        ``'{}-{}'.format(global_id, ext)``.
        
        :param str local_id: The localized id that is unique in the scope of\
        the block.
        :param str global_id: The globally unique id.
        :param str ext: An extension to be appended to the end of the\
        globally unique id.
        :return: The globally unique id.
        """
        if global_id is None:
            if ext:
                ext = '-' + str(ext)
            global_id = '{}-{}{}'.format(self.ids['this'], local_id, ext)
        self.ids.update({local_id: global_id})
        return global_id
    
    
    def __getitem__(self, key):
        return Component(self.ids[key])
    
    
    def __call__(self, component_id, property_id=None):
        
        if component_id not in self.ids:
            self.register(component_id)
            
        if property_id is None:
            return self.ids[component_id]
        else:
            return self[component_id][property_id]
    
    
    def output(self, component_id, component_property='children'):
        """Create the :class:`dash.dependencies.Output` dependency with
        :attr:`component_id`
        equal to the globally unique component id mapped from the 
        *component_id* argument, and matching component property.
        
        :param str component_id: The registered component id,\
        local to the block.
        :param str component_property: The component property.
        :return: The :class:`dash.dependencies.Output` dependency object.
        """
        return self[component_id].output(component_property)
    
    
    def input(self, component_id, component_property='children'):
        """Create the :class:`dash.dependencies.Input` dependency with
        :attr:`component_id`
        equal to the globally unique component id mapped from the 
        *component_id* argument, and matching component property.
        
        :param str component_id: The registered component id,\
        local to the block.
        :param str component_property: The component property.
        :return: The :class:`dash.dependencies.Input` dependency object.
        """
        return self[component_id].input(component_property)
    
    
    def state(self, component_id, component_property='children'):
        """Create the :class:`dash.dependencies.State` dependency with
        :attr:`component_id`
        equal to the globally unique component id mapped from the 
        *component_id* argument, and matching component property.
        
        :param str component_id: The registered component id, local\
        to the block.
        :param str component_property: The component property.
        :return: The :class:`dash.dependencies.State` dependency object.
        """
        return self[component_id].state(component_property)
    
    
class Store:
    """The Store class.

    :param dash.Dash app: The Dash app object.
    :param str id: The id unique to the store object.
    :param bool hide: Whether or not to hide the layout of the store object.
    """
    def __init__(self, app, id='', hide=True):
        
        self.app = app
        self._uid = id
        self.ids = {'this': self._uid}
        self.items = {}
        self.hide = hide
        
        
    @property
    def layout(self):
        """The layout containing divs for all registered data items.
        """
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
        global_id = prefix + id
        self.ids.update({id: global_id})
        return global_id

    
    def register(self, local_id, inputs=None, state=None, initially=''):
        """Register a *local_id* to be internally mapped to a globally unique
        id. If *inputs* is provided, it will return a decorator function that
        mediates the *inputs* and *state* to an :attr:`app`.:meth:`callback`
        call. For example this:
        ::

            store.register(
                'hello',
                inputs=[Input('foo', 'value')],
                state=[State('bar', 'children')]
            )
            def update_something(value, children):
                return 'some data'

        ... is a shortcut for this:
        ::

            store.register('hello')
            store.app.callback(
                store.output('hello'),
                inputs=[Input('foo', 'value')],
                state=[State('bar', 'children')]
            )
            def update_something(value, children):
                return 'some data'

        
        :param str local_id: The localized id that is unique in the scope of\
        the block. A div with this id will be created in the store object's\
        layout.
        :param list(dash.dependency.Input) inputs: The Dash input\
        dependencies to the callback that updates the div with *local_id*.
        :param list(dash.dependency.State) state: The Dash state\
        dependencies to the callback that updates the div with *local_id*.
        :param initially: The initial value in the created div with *local_id*
        """
        global_id = self._register(local_id)
        self.items[local_id] = initially
        if inputs is None:
            return global_id
        else:
            state = state or []
            def deco(cbfunc):
                self.app.callback(
                    self.output(local_id), inputs, state
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