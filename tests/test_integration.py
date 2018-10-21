import unittest
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
import multiprocessing as mp
import time

import dash
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output
import dash_html_components as html
import dash_core_components as dcc

from .location import create_app
from .IntegrationTests import IntegrationTests
from .utils import assert_clean_console, invincible, wait_for

class TestLocationApp(IntegrationTests):

    def setUp(self):

        def wait_for_element_by_id(id):
            wait_for(lambda: None is not invincible(
                lambda: self.driver.find_element_by_id(id)
            ))
            return self.driver.find_element_by_id(id)
        self.wait_for_element_by_id = wait_for_element_by_id

    def test_app(self):

        app = create_app()
        self.startServer(app)

        lon = 10
        lat = 10
        form_data_exp = ('{{"longitude": "{}", "latitude": "{}"}}'
                         .format(lon, lat))

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
        self.percy_snapshot(name='location-updated')

        assert_clean_console(self)