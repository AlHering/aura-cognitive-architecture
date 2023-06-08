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


"""
Environment file
"""
ENV = load_dotenv(os.path.join(PATHS.PACKAGE_PATH, ".env"))
