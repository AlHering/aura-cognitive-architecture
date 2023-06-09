# -*- coding: utf-8 -*-
"""
****************************************************
*           aura-cognitive-architecture
*            (c) 2023 Alexander Hering             *
****************************************************
"""
from typing import List, Any
from ..configuration import configuration as cfg
from ..utility.gold.sqlalchemy_entity_data_interface import SQLAlchemyEntityInterface as DBInterface


class ModelDatabase(DBInterface):
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
            "targets": "*",
            "handle_as_objects": True
        },
            entity_profiles=cfg.ENTITY_PROFILE,
            linkage_profiles=cfg.LINKAGE_PROFILE,
            view_profiles=cfg.VIEW_PROFILE)

    def get_tracked_model_files(model_folder: str = None) -> List[Any]:
        """
        Method for getting tracked model files.
        :param model_folder: Model folder to fetch tracked model files for.
            Defaults to None in which case all tracked files are returned.
        """
        pass
