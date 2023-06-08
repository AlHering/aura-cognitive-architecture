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
from configuration.database_configuration import ENTITY_PROFILE, LINKAGE_PROFILE, VIEW_PROFILE
from ..interfaces.database import ACADatabase


"""
Environment file
"""
ENV = load_dotenv(os.path.join(PATHS.PACKAGE_PATH, ".env"))


"""
Shared Database Interface
"""
DB = ACADatabase()
