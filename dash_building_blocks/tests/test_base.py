import unittest
from unittest import mock

from dash.dependencies import Input, Output, State
import dash_html_components as html
from dash_building_blocks.base import (
    Block, Store
)
from dash_building_blocks.error import (
    Error,
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
            except Error:
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