# -*- coding: utf-8 -*-
"""
****************************************************
*                CommonFlaskFrontend
*            (c) 2023 Alexander Hering             *
****************************************************
"""
import os
import sys
PACKAGE_PARENT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PACKAGE_PARENT_PATH not in sys.path:
    sys.path.append(PACKAGE_PARENT_PATH)

from common_flask_frontend.control.common_flask_application_controller import CommonFlaskApplicationController



# Note that all file paths need to be given relative to the static folder.
global_config = {
    "page_title": "My Service Title",
    "page_icon_path": "img/icons/favicon.ico"
}
endpoint_config = {
    "endpoints": {
        "index": "",
        "login": "",
        "register": "",
        "authenticate": "",
        "forms": "",
        "charts": "",
        "tables": ""
    }
}
user_config = {
    "user_config": {
        "user_avatar": "img/avatar-0.jpg",
        "user_name": "Nathan Andrews",
        "user_role": "Developer"
    }
}
user_config["user_config"][
    "user_acronym"] = f"{user_config['user_config']['user_role'][0]}:{''.join(name_part[0] for name_part in user_config['user_config']['user_name'].split(' '))}"
# Note that icons are xlink references
menu_config = {
    "menus": {
        "MAIN": {
            "#meta": {
                "icon": "#real-estate-1",
                "type": "xl",
            },
            "Home": {
                "icon": "#real-estate-1",
                "type": "xl",
                "href": "index"
            },
            "Forms": {
                "icon": "bed",
                "type": "fa",
                "href": "forms"
            },
            "My Dropdown": {
                "icon": "#browser-window-1",
                "type": "xl",
                "href": "#drop",
                "dropdown": {
                    "Page1": {
                        "href": "index"
                    },
                    "Page2": {
                        "href": "index"
                    },
                    "Page3": {
                        "href": "index"
                    }
                }
            },
            "Login page": {
                "icon": "bed",
                "type": "fa",
                "href": "login"
            },
            "Demo": {
                "icon": "bed",
                "type": "fa",
                "href": "index",
                "flag": {
                    "type": "warning",
                    "text": "6 New"
                }
            }
        },
        "SECOND MENU": {
            "#meta": {
                "icon": "bed",
                "type": "fa"
            },
            "Demo1": {
                "icon": "",
                "type": "fa",
                "href": "index"
            },
            "My Dropdown": {
                "icon": "bed",
                "type": "fa",
                "href": "#demodrop",
                "dropdown": {
                    "DemoPage1": {
                        "href": "index",
                        "icon": "",
                        "type": "fa"
                    },
                    "DemoPage2": {
                        "href": "index",
                        "icon": "",
                        "type": "fa"
                    }
                }
            }
        }}
}

for dictionary in [endpoint_config, menu_config, user_config]:
    global_config.update(dictionary)


if __name__ == "__main__":
    global_config.pop("user_config")
    print(global_config)
    ac = CommonFlaskApplicationController(global_config)
    print(ac.app.url_map)
    ac.run_app()

