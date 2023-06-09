# -*- coding: utf-8 -*-
"""
****************************************************
*           aura-cognitive-architecture
*            (c) 2023 Alexander Hering             *
****************************************************
"""
from typing import List, Any
from ..configuration import configuration as cfg
from ..model.model_control.model_database_profiles import ENTITY_PROFILE, LINKAGE_PROFILE, VIEW_PROFILE
from ..utility.gold.sqlalchemy_entity_data_interface import SQLAlchemyEntityInterface as DBInterface
from ..utility.gold.filter_mask import FilterMask


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
            entity_profiles=ENTITY_PROFILE,
            linkage_profiles=LINKAGE_PROFILE,
            view_profiles=VIEW_PROFILE)

    def get_tracked_model_files(self, model_folder: str = None, ignored_sub_folders: List[str] = [], ignored_model_files: List[str] = []) -> List[Any]:
        """
        Method for getting tracked model files.
        :param model_folder: Model folder to fetch tracked model files for.
            Defaults to None in which case all tracked files are returned.
        :param ignored_sub_folders: Subfolder parts to ignore.  
            Defaults to an empty list.
        :param ignored_model_files: Model files to ignore.  
            Defaults to an empty list.
        """
        filter_expressions = [["folder", "contains",
                               model_folder]] if model_folder is not None else []
        filter_expressions.extend(
            [["folder", "not_contains", ignored] for ignored in ignored_sub_folders])
        filter_expressions.extend([["file_name", "!=", ignored]
                                  for ignored in ignored_model_files])

        return self._get_batch("model_file", [FilterMask(filter_expressions)
                                              ] if filter_expressions else [])

    def get_unlinked_model_files(self, files: List[str] = None) -> List[Any]:
        """
        Method for getting unlinked model files.
        :param files: Files to link.
            Defaults to None, in which case all unknown models are linked.
        :return: List of unlinked model files.
        """
        filter_expressions = [["file_name", "in",
                               files]] if files is not None else []

        return self._get_batch("model_file", [FilterMask(filter_expressions)
                                              ] if filter_expressions else [])
