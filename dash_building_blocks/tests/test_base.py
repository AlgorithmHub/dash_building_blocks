import unittest
from unittest import mock

from dash.dependencies import Input, Output, State
import dash_html_components as html
from dash_building_blocks.base import (
    Block, Store, Data, Component
)
from dash_building_blocks.error import (
    ProhibitedParameterError
)

class Minimal(Block):

    def layout(self):
        return None


class HelloWorld(Block):

    def layout(self):
        return html.Div('hello world', id=self.register('div'))

    def callbacks(self, input_value):
        @self.callback(
            self.output('div'), inputs=[input_value]
        )
        def update_div(value):
            return value

class TestData(unittest.TestCase):

    def setUp(self):
        self.kwargs = {
            'str': 'hello',
            'int': 10,
            'float': 1.5,
            'dict': {'answer': 42},
            'list': [0, 1, 2, 3]
        }

    def test_init_default(self):
        data = Data()
        self.assertEqual(data.__dict__, {})
        self.assertFalse(data)

    def test_death_init_args(self):
        try:
            Data('kill me')
        except:
            self.assertRaises(TypeError)
        
    def test_init_kwargs(self):
        data = Data(**self.kwargs)
        self.assertTrue(data)

        for key, val in self.kwargs.items():
            self.assertEqual(getattr(data, key), val)
            self.assertEqual(data[key], val)

        self.assertEqual(repr(self.kwargs), repr(data))
        self.assertEqual(str(self.kwargs), str(data))

    def test_from_dict_to_dict(self):
        data = Data.from_dict(self.kwargs)
        self.assertEqual(data.to_dict(), self.kwargs)


class TestComponent(unittest.TestCase):

    def setUp(self):
        self.id = 'test-component'
        self.comp = Component(self.id)
        self.assertEqual(self.comp.id, self.id)

    def test_death_init_default(self):
        try:
            Component()
        except:
            self.assertRaises(TypeError)

    def assertEqualDependencies(self, dep1, dep2):
        self.assertEqual(type(dep1), type(dep2))
        self.assertEqual(dep1.component_id, dep2.component_id)
        self.assertEqual(dep1.component_property, dep2.component_property)

    def test_getitem(self):
        self.assertEqual(self.comp['prop'], (self.id, 'prop'))

    def test_input(self):
        self.assertEqualDependencies(
            self.comp.input('prop'), Input(self.id, 'prop'))

    def test_state(self):
        self.assertEqualDependencies(
            self.comp.state('prop'), State(self.id, 'prop'))

    def test_output(self):
        self.assertEqualDependencies(
            self.comp.output('prop'), Output(self.id, 'prop'))


class TestBaseBlock(unittest.TestCase):

    def test_death_instantiate(self):
        try:
            Block()
        except:
            self.assertRaises(NotImplementedError)


class TestBlockMinimal(unittest.TestCase):

    def test_default_bid_and_register(self):

        block = Minimal()
        bid = block.ids['this']
        self.assertEqual(bid, '{}.{}'.format(block.base_id, block._uid))

        test_ext = 'test'
        test_id = block.register(test_ext)
        self.assertEqual(test_id, '{}-{}'.format(bid, test_ext))

    def test_blank_bid_and_register(self):

        block = Minimal(id='')
        bid = block.ids['this']
        self.assertEqual(bid, block.base_id)

        test_ext = 'test'
        test_id = block.register(test_ext)
        self.assertEqual(test_id, '{}-{}'.format(bid, test_ext))

    def test_custom_bid_and_register(self):
        custom = 'custom'
        block = Minimal(id=custom)
        bid = block.ids['this']
        self.assertEqual(block._uid, custom)
        self.assertEqual(bid, '{}.{}'.format(block.base_id, block._uid))

        test_ext = 'test'
        test_id = block.register(test_ext)
        self.assertEqual(test_id, '{}-{}'.format(bid, test_ext))
        
    def test_callback(self):
        
        app = mock.Mock()
        block = Minimal(app)

        args = [1, 2, 3]
        kwargs = {'a': 0, 'b': 1}
        block.callback(*args, **kwargs)

        app.callback.assert_called_once_with(*args, **kwargs)

    def test_init_id_blank(self):

        block = Minimal(id='')

        self.assertEqual(block.base_id, 'minimal')
        self.assertEqual(block.ids['this'], 'minimal')

    def test_death_param(self):

        for param in Block.sacred_attrs:
            try:
                Minimal().parameters(**{param:'killme'})
            except:
                self.assertRaises(ProhibitedParameterError)


class TestHelloWorld(unittest.TestCase):

    def test_init_default(self):

        block = HelloWorld()
        layout = block.layout

        self.assertEqual(block.app, None)
        self.assertFalse(block.data)
        self.assertEqual(block.base_id, 'hello-world')
        self.assertEqual(block.ids['this'].find('hello-world'), 0)
        div_id = block.ids['div']
        self.assertEqual(div_id.find('hello-world'), 0)
        self.assertEqual(div_id.find('-div'), len(div_id) - len('-div'))

        self.assertIsInstance(layout, html.Div)
        self.assertEqual(layout.children, 'hello world')
        self.assertEqual(layout.id, div_id)

    def test_init_custom(self):
        
        app = mock.Mock()
        data = {'answer': 42}
        block_id = 'hi'
        extra_parameters = dict(key='word', arg='ument')
        
        block = HelloWorld(app, data, id=block_id, **extra_parameters)
        layout = block.layout

        self.assertIsNotNone(block.app)
        self.assertTrue(block.data)
        self.assertEqual(block.data.to_dict(), data)
        self.assertEqual(block.key, 'word')
        self.assertEqual(block.arg, 'ument')

        self.assertEqual(block.base_id, 'hello-world')
        self.assertEqual(block.ids['this'], 'hello-world.hi')
        div_id = block.ids['div']
        self.assertEqual(div_id, 'hello-world.hi-div')

        self.assertIsInstance(layout, html.Div)
        self.assertEqual(layout.children, 'hello world')
        self.assertEqual(layout.id, div_id)

        input_component = mock.Mock()
        input_component.component_id = 'component'
        input_component.property_id = 'property'
        input_value = Input(input_component.component_id, 
                            input_component.property_id)

        block.callbacks(input_value)

        app.callback.assert_called_once()

class TestStore(unittest.TestCase):

    def setUp(self):
        pass