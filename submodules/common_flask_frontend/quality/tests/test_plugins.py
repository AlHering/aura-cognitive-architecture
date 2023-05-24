# -*- coding: utf-8 -*-
"""
****************************************************
*                ScrapingService
*            (c) 2022 Alexander Hering             *
****************************************************
"""
import os
import shutil
import unittest
from . import test_globals


class PluginsTest(unittest.TestCase):
    """
    Test class for testing the Plugin classes.
    """

    @classmethod
    def setUpClass(cls):
        """
        Class method for setting up test case.
        """
        pass

    @classmethod
    def tearDownClass(cls):
        """
        Class method for setting up test case.
        """
        pass

    @classmethod
    def setup_class(cls):
        cls.setUpClass()

    @classmethod
    def teardown_class(cls):
        cls.tearDownClass()


if __name__ == '__main__':
    unittest.main()