# -*- coding: utf-8 -*-
"""
****************************************************
*           aura-cognitive-architecture            *
*            (c) 2023 Alexander Hering             *
****************************************************
"""
global_config = {
    "page_title": "Aura Cognitive Architecture",
    "page_icon_path": "img/icons/favicon.ico"
}
endpoint_config = {
    "endpoints": {
        "index": "",
        "docker": "",
        "models": "",
    }
}
# Note that icons are xlink references
menu_config = {
    "menus": {
        "Aura": {
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
        }
    }
}

for dictionary in [endpoint_config, menu_config]:
    global_config.update(dictionary)
