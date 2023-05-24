# -*- coding: utf-8 -*-
"""
****************************************************
*                CommonFlaskFrontend                 
*          (c) 2022-2023 Alexander Hering          *
****************************************************
"""
import os
import re
import sys
import shutil
try:
    from dotenv import dotenv_values
    ENV = dotenv_values(os.path.abspath(os.path.join(os.path.dirname(__file__), ".env")))
    print(ENV)
except:
    ENV = os.environ

from . import paths as PATHS
from ..static_utility import json_utility, time_utility, file_system_utility

# Keep these currently unused imports for access at runtime!
from . import urls as URLS

CFG = None
default_configuration_json = os.path.join(PATHS.CONFIG_PATH + "/configuration.json")
if os.path.exists(default_configuration_json):
    CFG = json_utility.load(default_configuration_json)
    CFG["os"] = "windows" if sys.platform == "win32" else "linux"
else:
    CFG = json_utility.load(PATHS.CONFIG_PATH + "/base_configuration.json")
    CFG["os"] = "windows" if sys.platform == "win32" else "linux"

GLOBALS = json_utility.load(PATHS.CONFIG_PATH + "/globals.json")

if PATHS.MAIN_PLUGIN_FOLDER not in CFG["plugin_folders"]:
    CFG["plugin_folders"].append(PATHS.MAIN_PLUGIN_FOLDER)


############################
# Functionality for common #
#        Projects          #
############################


def save_configuration() -> None:
    """
    Function for saving configuration to disk.
    """
    global CFG

    json_utility.save(CFG, os.path.join(PATHS.CONFIG_PATH, "configuration.json"))


def safely_create_dump(dump_data: dict, dump_path: str = PATHS.DUMP_PATH) -> None:
    """
    Function for safely creating configuration dump
    :param dump_data: Data to dump.
    :param dump_path: Path for dumps, defaults to global dump path.
    """
    global CFG

    if not os.path.exists(dump_path):
        os.makedirs(dump_path)
    else:
        for root, dirs, files in os.walk(dump_path, topdown=True):
            config_files = [file for file in files if re.match(r'^confiuration_.*\.json', file)]
            while len(config_files) >= CFG["max_backups"]:
                os.remove(os.path.join(root, config_files[0]))
                config_files = config_files[1:]
            break
    json_utility.save(dump_data, os.path.join(dump_path, "configuration_" + time_utility.get_timestamp() + ".json"))


def backup_configuration() -> None:
    """
    Function for writing configuration backup on full and protocol level to disk.
    """
    global CFG

    safely_create_dump(CFG, os.path.join(PATHS.BACKUP_PATH, "configuration_" + time_utility.get_timestamp() + ".json"))


def reset_configuration() -> None:
    """
    Function for resetting configuration and protocol configurations.
    """
    global CFG
    backup_configuration()

    CFG = json_utility.load(PATHS.CONFIG_PATH + "/base_configuration.json")
    CFG["os"] = "windows" if sys.platform == "win32" else "linux"


############################
#    Functionality for     #
#     current Project      #
############################
"""from logging.config import dictConfig


dictConfig(
    {
        "version": 1,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
            }
        },
        "handlers": {
            "wsgi": {
                "class": "logging.StreamHandler",
                "stream": "ext://flask.logging.wsgi_errors_stream",
                "formatter": "default",
                "level": "INFO" if not CFG["debug"] else "DEBUG"
            },
            "standard": {
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
                "formatter": "default",
                "level": "INFO" if not CFG["debug"] else "DEBUG"
            }
        },
        "root": {
            "level": "INFO" if not CFG["debug"] else "DEBUG",
            "handlers": ["wsgi", "standard"]
        }
    }
)"""
