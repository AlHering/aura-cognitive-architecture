# -*- coding: utf-8 -*-
"""
****************************************************
*           aura-cognitive-architecture            *
*            (c) 2023 Alexander Hering             *
****************************************************
"""
import sys
import os


common_submodules = [os.path.abspath(os.path.join(os.path.dirname(__file__), "common_plugin_controller")), 
                     os.path.abspath(os.path.join(os.path.dirname(__file__), "common_flask_frontend")), 
                     os.path.abspath(os.path.join(os.path.dirname(__file__), "common_data_controller")), 
                     os.path.abspath(os.path.join(os.path.dirname(__file__), "common_scheduler"))]
for folder in common_submodules:
    if folder not in sys.path:
        sys.path.append(folder)
        
