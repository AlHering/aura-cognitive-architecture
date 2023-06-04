# -*- coding: utf-8 -*-
"""
****************************************************
*           aura-cognitive-architecture
*            (c) 2023 Alexander Hering             *
****************************************************
"""
from ..configuration import configuration as cfg
from ..utility.bronze.sqlalchemy_utility import SUPPORTED_DIALECTS, get_engine, get_automapped_base, get_session_factory, get_classes_from_base


"""
Database handles
"""
if cfg.ENV["DB_DIALECT"] not in SUPPORTED_DIALECTS:
    raise NotImplementedError(
        f"Dialect {cfg.ENV['DB_DIALECT']} not supported by SQLAlchemy Utility!")
ENGINE = get_engine(cfg.ENV["DB_URL"])
BASE = get_automapped_base(ENGINE)
SESSION_FACTORY = get_session_factory(ENGINE)
MODEL = get_classes_from_base(BASE)


"""
Dataclasses
"""
# TODO: Implement dataclasses
