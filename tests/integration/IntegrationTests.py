# Original: https://github.com/plotly/dash/blob/master/tests/IntegrationTests.py

import multiprocessing
import sys
import time
import unittest
from selenium import webdriver
import percy
from .utils import invincible, wait_for


class IntegrationTests(unittest.TestCase):

    def percy_snapshot(self, name=''):
        snapshot_name = '{} - {}'.format(name, sys.version_info)
        print(snapshot_name)
        self.percy_runner.snapshot(
            name=snapshot_name
        )
    
    def wait_for_element_by_id(self, id):
        wait_for(lambda: None is not invincible(
            lambda: self.driver.find_element_by_id(id)
        ))
        return self.driver.find_element_by_id(id)

    def wait_for_element_by(self, by, key, *args, **kwargs):
        wait_for(lambda: None is not invincible(
            lambda: getattr(self.driver, 'find_element_by_'+by)(key)
        ), *args, **kwargs)
        return getattr(self.driver, 'find_element_by_'+by)(key)

    def wait_for_elements_by(self, by, key, *args, **kwargs):
        wait_for(lambda: None is not invincible(
            lambda: getattr(self.driver, 'find_elements_by_'+by)(key)
        ), *args, **kwargs)
        return getattr(self.driver, 'find_elements_by_'+by)(key)

    @classmethod
    def setUpClass(cls):
        super(IntegrationTests, cls).setUpClass()
        cls.driver = webdriver.Chrome()

        loader = percy.ResourceLoader(
            webdriver=cls.driver
        )
        cls.percy_runner = percy.Runner(loader=loader)

        cls.percy_runner.initialize_build()

    @classmethod
    def tearDownClass(cls):
        super(IntegrationTests, cls).tearDownClass()
        cls.driver.quit()
        cls.percy_runner.finalize_build()

    def setUp(self):
        pass

    def tearDown(self):
        time.sleep(2)
        self.server_process.terminate()
        time.sleep(2)

    def startServer(self, dash):
        def run():
            dash.scripts.config.serve_locally = True
            dash.run_server(
                port=8050,
                debug=False,
                processes=4,
                threaded=False
            )

        # Run on a separate process so that it doesn't block
        self.server_process = multiprocessing.Process(target=run)
        self.server_process.start()
        time.sleep(0.5)

        # Visit the dash page
        self.driver.get('http://localhost:8050')
        time.sleep(0.5)

        # Inject an error and warning logger
        logger = '''
        window.tests = {};
        window.tests.console = {error: [], warn: [], log: []};
        var _log = console.log;
        var _warn = console.warn;
        var _error = console.error;
        console.log = function() {
            window.tests.console.log.push({method: 'log', arguments: arguments});
            return _log.apply(console, arguments);
        };
        console.warn = function() {
            window.tests.console.warn.push({method: 'warn', arguments: arguments});
            return _warn.apply(console, arguments);
        };
        console.error = function() {
            window.tests.console.error.push({method: 'error', arguments: arguments});
            return _error.apply(console, arguments);
        };
        '''
        self.driver.execute_script(logger)