# -*- coding: utf-8 -*-
"""
****************************************************
*           aura-cognitive-architecture
*            (c) 2023 Alexander Hering             *
****************************************************
"""
from ..configuration import configuration as cfg
from ..utility.gold.sqlalchemy_entity_data_interface import SQLAlchemyEntityInterface as DBInterface


class ACADatabase(DBInterface):
    """
    Class, representing ACA Database.
    """

    def __init__(self) -> None:
        """
        Initiation method.
        """
        super().__init__(environment_profile={
            "backend": "database",
            "framework": "sqlalchemy",
            "arguments": {
                "database": cfg.ENV["DB_URL"],
                "dialect": cfg.ENV["DB_DIALECT"],
                "encoding": "utf-8"
            },
            "targets": "*"
        },
            entity_profiles=cfg.ENTITY_PROFILE,
            linkage_profiles=cfg.LINKAGE_PROFILE,
            view_profiles=cfg.VIEW_PROFILE)
