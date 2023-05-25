# -*- coding: utf-8 -*-
"""
****************************************************
*                ScrapingService                 
*            (c) 2022 Alexander Hering             *
****************************************************
"""
import logging
from common_flask_frontend.configuration import configuration as cfg
from common_flask_frontend.utility import json_utility

LOGGER = logging.Logger("[QUALITY]")
TEST_PATH = f"{cfg.PATHS.PACKAGE_PATH}/quality/tests"
TEST_DATA_PATH = f"{TEST_PATH}/testdata"
TEST_WORKSPACE_PATH = f"{TEST_PATH}/test_workspace"

COMMON_FLASK_FRONTEND_TEST_CONFIG = json_utility.load(
    f"{TEST_DATA_PATH}/test_configurations/COMMON_FLASK_FRONTEND_TEST_CONFIG.json")
