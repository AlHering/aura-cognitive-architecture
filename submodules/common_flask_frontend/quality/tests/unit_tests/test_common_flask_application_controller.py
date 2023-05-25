# -*- coding: utf-8 -*-
"""
****************************************************
*                ScrapingService
*            (c) 2022 Alexander Hering             *
****************************************************
"""
import copy
import os
import gc
import shutil
import unittest
from .. import test_globals

from common_flask_frontend.control.common_flask_application_controller import CommonFlaskApplicationController


class PluginControllerTest(unittest.TestCase):
    """
    Test class for testing the Plugin Controller class.
    """
    controller: CommonFlaskApplicationController = None

    @classmethod
    def setUpClass(cls):
        """
        Class method for setting up test case.
        """
        cls.controller = CommonFlaskApplicationController(app_config=copy.deepcopy(test_globals.COMMON_FLASK_FRONTEND_TEST_CONFIG))

    @classmethod
    def tearDownClass(cls):
        """
        Class method for setting up test case.
        """
        if hasattr(cls, "controller"):
            del cls.controller
        gc.collect()

    @classmethod
    def setup_class(cls):
        cls.setUpClass()

    @classmethod
    def teardown_class(cls):
        cls.tearDownClass()

    def test_controller_initiation(self):
        """
        Testmethod for testing controller initiation.
        """
        self.assertTrue(self.controller.plugin_controller is not None)
        self.assertTrue(self.controller.app is not None)
        self.assertTrue(self.controller.process is not None)

    def test_config_checking_dropdown_href_hashtag(self):
        """
        Testmethod for testing controller initiation.
        """
        self.controller.config["menus"]["MAIN"]["My Dropdown"]["href"] = "test"
        self.assertFalse(self.controller.check_config())
        self.controller.config = copy.deepcopy(test_globals.COMMON_FLASK_FRONTEND_TEST_CONFIG)

    def test_config_checking_dropdown_duplicate_hrefs(self):
        """
        Testmethod for testing controller initiation.
        """
        self.controller.config["menus"]["SECOND MENU"]["My Dropdown"]["href"] = "#drop"
        self.assertFalse(self.controller.check_config())
        self.controller.config = copy.deepcopy(test_globals.COMMON_FLASK_FRONTEND_TEST_CONFIG)


if __name__ == '__main__':
    unittest.main()