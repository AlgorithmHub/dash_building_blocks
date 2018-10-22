import unittest
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
import multiprocessing as mp
import time

import dash
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output
import dash_html_components as html
import dash_core_components as dcc

from . import apps
from .IntegrationTests import IntegrationTests
from .utils import assert_clean_console, invincible, wait_for

class TestLocationApp(IntegrationTests):

    def test_app(self):

        app = apps.create_location_app()
        self.startServer(app)

        lon = 10
        lat = 10
        form_data_exp = ('{{"longitude": "{}", "latitude": "{}"}}'
                         .format(lon, lat))

        points = lambda: self.wait_for_elements_by(
            'xpath', '//*[@class="trace scattergeo"]/*')
        self.assertEqual(len(points()), 0)

        input_lon = self.wait_for_element_by_id('input-form-longitude')
        input_lat = self.wait_for_element_by_id('input-form-latitude')
        input_btn = self.wait_for_element_by_id('input-form-submit-button')

        input_lon.clear()
        input_lat.clear()

        input_lon.send_keys('10')
        input_lat.send_keys('10')
        input_btn.click()

        form_data = lambda: (self.wait_for_element_by_id('user-input')
                                 .get_attribute('innerHTML'))
        wait_for(lambda: form_data() == form_data_exp)

        wait_for(lambda: len(points()) == 1)
        self.assertTrue(points()[0].is_displayed())

        self.percy_snapshot(name='location-map-updated')

        assert_clean_console(self)

class TestClonesApp(IntegrationTests):

    def test_app(self):
        
        n_clones = 10

        app = apps.create_clones_app()
        self.startServer(app)
    
        how_many = (self.wait_for_element_by_id('how-many-clones')
                        .get_attribute('innerHTML'))
        self.assertEqual(how_many, '10')

        clone_div = lambda i: self.wait_for_element_by_id('clone-{}-div'.format(i))
        clone_btn = lambda i: self.wait_for_element_by_id('clone-{}-button'.format(i))
        
        for i in range(n_clones):
            div = clone_div(i)
            self.assertTrue(div.is_displayed())
            self.assertTrue(div.is_enabled())
            self.assertEqual(div.text, 'There are 10 of us.')

            btn = clone_btn(i)
            self.assertTrue(btn.is_displayed())
            self.assertTrue(btn.is_enabled())
            self.assertEqual(btn.text, 'Click Me!')

            btn.click()
            wait_for(lambda: clone_div(i).text == 'I am a clone.')

        self.percy_snapshot(name='clones-clicked')

        assert_clean_console(self)

if __name__ == '__main__':
    unittest.main()