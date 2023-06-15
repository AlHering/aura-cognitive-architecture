# -*- coding: utf-8 -*-
"""
****************************************************
*           aura-cognitive-architecture            *
*            (c) 2023 Alexander Hering             *
****************************************************
"""
import sys
import os
package_root = os.path.abspath(os.path.dirname(__file__))
cpc_root = os.path.join(package_root, "submodules", "common_plugin_controller")
for root in [package_root, cpc_root]:
    if root not in sys.path:
        sys.path.append(root)

if __name__ == "__main__":
    print(sys.path)
    from configuration.common_frontend_config import global_config
    from view.flask_frontend.flask_app_controller import CommonFlaskApplicationController

    aura_app_controller = CommonFlaskApplicationController(global_config)

    aura_app_controller.run_app(global_config)
