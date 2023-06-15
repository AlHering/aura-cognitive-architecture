# -*- coding: utf-8 -*-
"""
****************************************************
*           aura-cognitive-architecture
*            (c) 2023 Alexander Hering             *
****************************************************
"""
import os


PACKAGE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SUBMODULE_PATH = os.path.join(PACKAGE_PATH, "submodules")
DATA_PATH = os.path.join(PACKAGE_PATH, "data")
PLUGIN_PATH = os.path.join(PACKAGE_PATH, "plugins")
FLASK_COMMON_STATIC = os.path.join(
    PACKAGE_PATH, "view", "flask_frontend", "common_static")
FLASK_COMMON_TEMPLATES = os.path.join(
    PACKAGE_PATH, "view", "flask_frontend", "common_templates")
