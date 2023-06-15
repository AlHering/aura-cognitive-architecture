# -*- coding: utf-8 -*-
"""
****************************************************
*           aura-cognitive-architecture            *
*            (c) 2023 Alexander Hering             *
****************************************************
"""
import os
import sys
from src.control.flask_frontend_controller import FlaskFrontendController
from src.configuration.flask_frontend_config import global_config


if __name__ == "__main__":
    aura_app_controller = FlaskFrontendController(global_config)
    aura_app_controller.run_app()
