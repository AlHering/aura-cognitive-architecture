# -*- coding: utf-8 -*-
"""
****************************************************
*           aura-cognitive-architecture            *
*            (c) 2023 Alexander Hering             *
****************************************************
"""
from configuration.common_frontend_config import global_config
from submodules.common_flask_frontend.control.common_flask_application_controller import CommonFlaskApplicationController
aura_app_controller = CommonFlaskApplicationController(global_config)


aura_app_controller.run_app()
