# -*- coding: utf-8 -*-
"""
****************************************************
*           aura-cognitive-architecture
*            (c) 2023 Alexander Hering             *
****************************************************
"""
import os
from dotenv import load_dotenv
import paths as PATHS
import urls as URLS
from data_backend import ENTITY_PROFILE, LINKAGE_PROFILE, VIEW_PROFILE


"""
Environment file
"""
ENV = load_dotenv(os.path.join(PATHS.PACKAGE_PATH, ".env"))
