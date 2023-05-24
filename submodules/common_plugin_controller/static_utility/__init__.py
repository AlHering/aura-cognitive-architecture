# -*- coding: utf-8 -*-
"""
****************************************************
*                CommonFlaskFrontend                 
*            (c) 2022 Alexander Hering             *
****************************************************
"""
import sys
import os


common_submodules = [os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, "common_plugin_controller")), 
                     os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir,  "common_flask_frontend")), 
                     os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, "common_data_backend")),
                     os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, "utility"))]
for folder in common_submodules:
    if folder not in sys.path:
        sys.path.append(folder)