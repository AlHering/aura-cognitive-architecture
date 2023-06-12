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
        :return: List of tracked model files.
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
        :param files: Files to get.
            Defaults to None, in which case all unknown models are retrieved.
        :return: List of unlinked model files.
        """
        filter_expressions = [["file_name", "in",
                               files]] if files is not None else []

        return self._get_batch("model_file", [FilterMask(filter_expressions)
                                              ] if filter_expressions else [])

    def link_model_file(self, model_file: Any, model_version_data: dict) -> None:
        """
        Method for linking model files.
        :param model_file: File to link.
        :param model_version_data: Model version data to link to model file.
            Needs to include "source", "api_url" and "metadata".
        """
        model_version = self._get("model_version", [FilterMask(
            [["api_url"], "==", model_version_data["api_url"]])])
        if model_version:
            model_version.metadata = model_version_data["metadata"]
            self._patch("model_version", model_version)
        else:
            model_version = self._post(
                "model_version", self.model["model_version"](**model_version_data))

        self.link_entities("link", model_file, model_version)
        model_file.status = "linked"
        self._patch("model_file", model_file)
