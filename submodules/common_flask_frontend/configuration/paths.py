# -*- coding: utf-8 -*-
"""
****************************************************
*                CommonFlaskFrontend                 
*            (c) 2022 Alexander Hering             *
****************************************************
"""
import os


SUBPACKAGE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SUBPACKAGE_DATA = os.path.join(SUBPACKAGE_PATH, "data")
SUBPACKAGE_PLUGINS = os.path.join(SUBPACKAGE_PATH, "plugins")
