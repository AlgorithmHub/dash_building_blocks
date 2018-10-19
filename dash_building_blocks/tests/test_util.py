import unittest

from dash_building_blocks.util import (
    camelify,
    decamelify
)

class TestCamelify(unittest.TestCase):

    def test_camelify_default_delims(self):
        origs = ['this-is-a-test', '_this-is_a-test_']
        camels = ['thisIsATest', 'ThisIsATest']
        
        for orig, camel in zip(origs, camels):
            self.assertEqual(camelify(orig), camel)

    def test_camelify_custom_delims(self):
        origs = ['this*is*a*test', 'thisaisatest']
        camels = ['thisIsATest', 'thisIsTest']
        delims = [['*'], ['a']]
        
        for orig, camel, delim in zip(origs, camels, delims):
            self.assertEqual(camelify(orig, delims=delim), camel)

class TestDeCamelify(unittest.TestCase):

    def test_decamelify_default_delim(self):
        camels = ['thisIsATest', 'ThisIsATest']
        decamels = ['this-is-a-test', 'this-is-a-test']
        
        for camel, decam in zip(camels, decamels):
            self.assertEqual(decamelify(camel), decam)

    def test_decamelify_custom_delim(self):
        camels = ['thisIsATest', 'ThisIsTest']
        decamels = ['this*is*a*test', 'thisaisatest']
        delims = ['*', 'a']
        
        for camel, decam, delim in zip(camels, decamels, delims):
            self.assertEqual(decamelify(camel, delim=delim), decam)
