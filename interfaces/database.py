# -*- coding: utf-8 -*-
"""
****************************************************
*           aura-cognitive-architecture
*            (c) 2023 Alexander Hering             *
****************************************************
"""
from ..configuration import configuration as cfg
from ..utility.bronze.sqlalchemy_utility import SUPPORTED_DIALECTS, get_engine, get_automapped_base, get_session_factory, get_classes_from_base


class ACADatabase(object):
    """
    Class, representing ACA Database.
    """
    def __init__(self) -> None:
        """
        Initiation method.
        """
        pass