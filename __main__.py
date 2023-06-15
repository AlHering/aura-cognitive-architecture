# -*- coding: utf-8 -*-
"""
****************************************************
*           aura-cognitive-architecture            *
*            (c) 2023 Alexander Hering             *
****************************************************
"""
from configuration.common_frontend_config import global_config
from view.flask_frontend.flask_app_controller import CommonFlaskApplicationController
aura_app_controller = CommonFlaskApplicationController(global_config)


aura_app_controller.run_app()
