# -*- coding: utf-8 -*-
"""
****************************************************
*           aura-cognitive-architecture
*            (c) 2023 Alexander Hering             *
****************************************************
"""
import os

PACKAGE_PATH = os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))
SOURCE_PATH = os.path.join(PACKAGE_PATH, "src")
DOCS_PATH = s.path.join(PACKAGE_PATH, "docs")
SUBMODULE_PATH = os.path.join(SOURCE_PATH, "submodules")
DATA_PATH = os.path.join(PACKAGE_PATH, "data")
PLUGIN_PATH = os.path.join(SOURCE_PATH, "plugins")
FLASK_COMMON_STATIC = os.path.join(
    SOURCE_PATH, "view", "flask_frontend", "common_static")
FLASK_COMMON_TEMPLATES = os.path.join(
    SOURCE_PATH, "view", "flask_frontend", "common_templates")
