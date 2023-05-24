# -*- coding: utf-8 -*-
"""
****************************************************
*                CommonFlaskFrontend                 
*            (c) 2022 Alexander Hering             *
****************************************************
"""
import sys
import os

FIREFOX_PATH = None
PACKAGE_PATH = None
DATA_PATH = None

if os.environ.get("RUNNING_IN_DOCKER", False):
    PACKAGE_PATH = "/common_flask_frontend"
    GLOBAL_DATA_PATH = "/global_data"
    DATA_PATH = "/data"
else:
    PACKAGE_PATH = os.path.dirname(os.path.abspath(__file__)).split("common_flask_frontend")[0] + "common_flask_frontend"
    GLOBAL_DATA_PATH = os.path.abspath(PACKAGE_PATH + "/../../GlobalData")
    DATA_PATH = PACKAGE_PATH + "/data"
    if sys.platform == "win32":
        profile_path = os.path.join(os.getenv('APPDATA'), "Mozilla", "Firefox", "Profiles")
    else:
        if os.path.exists("/home/linux/"):
            home_path = "/home/linux"
        elif os.path.exists("/home/ubuntu/"):
            home_path = "/home/ubuntu"
        elif os.path.exists("/home/pi/"):
            home_path = "/home/pi"
        else:
            home_path = "/"
        profile_path = os.path.join(home_path, ".mozilla", "firefox")
    if os.path.exists(profile_path):
        folders = []
        for root, dirs, files in os.walk(profile_path, topdown=True):
            folders = dirs
            break
        for folder in folders:
            if "release" in folder:
                FIREFOX_PATH = os.path.join(profile_path, folder)
                break
            elif "default" in folder:
                if not FIREFOX_PATH or len(os.path.join(profile_path, folder)) > len(FIREFOX_PATH):
                    FIREFOX_PATH = os.path.join(profile_path, folder)
        del folders
    del profile_path


CONDA_PATH = None
options = [path for path in sys.path if "conda3" in path]
if options:
    options = options[0]
    if "anaconda3" in options:
        CONDA_PATH = options.split("anaconda3")[0] + "anaconda3"
    elif "miniconda3" in options:
        CONDA_PATH = options.split("miniconda3")[0] + "miniconda3"


CONFIG_PATH = PACKAGE_PATH + "/configuration"
MAIN_PLUGIN_FOLDER = PACKAGE_PATH + "/plugins"
MAIN_PROTOCOL_FOLDER = PACKAGE_PATH + "/protocols"
BACKUP_PATH = DATA_PATH + "/Backups"
SNAPSHOT_PATH = DATA_PATH + "/Snapshots"
UTILITY_PATH = DATA_PATH + "/utility"
DUMP_PATH = DATA_PATH + "/dumps"

"""
On config depending paths to be set in configuration.py
"""

TTS_DATA_PATH = None
TTS_MODEL_PATH = None
STT_DATA_PATH = None
STT_MODEL_PATH = None
NLP_DATA_PATH = None