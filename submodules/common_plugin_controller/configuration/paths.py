# -*- coding: utf-8 -*-
"""
****************************************************
*                Common Plugin Controller
*            (c) 2023 Alexander Hering             *
****************************************************
"""
import os


PACKAGE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__))).split("/submodules/")[0]
PLUGIN_FOLDERS = {}
for plugin_folder in [os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "plugins"), os.path.join(PACKAGE_PATH, "plugins")]:
    if os.path.exists(plugin_folder):
        PLUGIN_FOLDERS.add(plugin_folder)
