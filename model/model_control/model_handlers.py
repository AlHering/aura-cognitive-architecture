# -*- coding: utf-8 -*-
"""
****************************************************
*           aura-cognitive-architecture            *
*            (c) 2023 Alexander Hering             *
****************************************************
"""
from typing import Any, Optional, List
import abc
from ...configuration import configuration as cfg
import os
from logging import Logger
import copy
from ...utility.bronze import json_utility, hashing_utility, dictionary_utility
from ...interfaces.model_database import ModelDatabase


class AbstractModelHandler(object):
    """
    Class, representing ML Model Handler objects.
    A Model Handler utilizes API Wrappers for collecting metadata and downloading assets from
    model services and managing updates, organization and usage.
    """

    def __init__(self, db_interface: ModelDatabase, api_wrapper_dict: dict) -> None:
        """
        Initiation method.
        :param db_interface: Entity Data Interface.
        :param api_wrapper_dict: Dictionary, mapping source to API wrapper.
        """
        self._logger = Logger["ModelHandler"]
        self._db = db_interface
        self._apis = api_wrapper_dict
        self._cache = {}

    def import_cache(self, import_path: str) -> None:
        """
        Method for importing cache data.
        :param import_path: Import path.
        """
        self._logger.log(f"Importing cache from '{import_path}'...")
        self._cache = json_utility.load(import_path)

    def export_cache(self, export_path: str) -> None:
        """
        Method for exporting cache data.
        :param export_path: Export path.
        """
        self._logger.log(f"Exporting cache to '{export_path}'...")
        json_utility.save(self._cache, export_path)

    @abc.abstractmethod
    def load_model_folder(self, *args: Optional[List], **kwargs: Optional[dict]) -> None:
        """
        Abstract method for loading model folder.
        :param args: Arbitrary arguments.
        :param kwargs: Arbitrary keyword arguments.
        """
        pass

    @abc.abstractmethod
    def update_metadata(self, *args: Optional[List], **kwargs: Optional[dict]) -> None:
        """
        Abstract method for updating cached metadata.
        :param args: Arbitrary arguments.
        :param kwargs: Arbitrary keyword arguments.
        """
        pass

    @abc.abstractmethod
    def organize_models(self, *args: Optional[List], **kwargs: Optional[dict]) -> None:
        """
        Abstract method for organizing local models.
        :param args: Arbitrary arguments.
        :param kwargs: Arbitrary keyword arguments.
        """
        pass

    @abc.abstractmethod
    def move_model(self, *args: Optional[List], **kwargs: Optional[dict]) -> None:
        """
        Abstract method for moving local model and adjusting metadata.
        :param args: Arbitrary arguments.
        :param kwargs: Arbitrary keyword arguments.
        """
        pass


class StabeDiffusionModelHandler(AbstractModelHandler):
    """
    Class, representing Model Handler for Stable Diffusion models.
    """

    def __init__(self, db_interface: ModelDatabase, api_wrapper_dict: dict) -> None:
        """
        Initiation method.
        :param db_interface: Entity Data Interface.
        :param api_wrapper_dict: Dictionary, mapping source to API wrapper.
        """
        super().__init__(db_interface, api_wrapper_dict)
        self._logger = Logger["StabeDiffusionModelHandler"]

    def load_model_folder(self, model_folder: str, ignored_sub_folders: List[str] = [], ignored_model_files: List[str] = []) -> None:
        """
        Method for loading model folder.
        :param model_folder: Model folder to load.
        :param ignored_sub_folders: Subfolder parts to ignore.  
            Defaults to an empty list.
        :param ignored_model_files: Model files to ignore.  
            Defaults to an empty list.
        """
        self._logger.info(f"Loading model folders under '{model_folder}'...")
        already_tracked_files = self._db.get_tracked_model_files(
            model_folder, ignored_sub_folders, ignored_model_files)
        self._logger.info(
            f"Found {len(already_tracked_files)} already tracked files...")

        for root, _, files in os.walk(model_folder, topdown=True):
            self._logger.info(f"Checking '{root}'...")
            ignored_subfolder = any(subfolder in ignored_sub_folders for subfolder in root.replace(
                model_folder, "").split("/"))
            for model_file in self.extract_model_files(files):
                self._logger.info(f"Found '{model_file}'.")
                full_model_path = os.path.join(root, model_file)
                if not any(os.path.join(model.folder, model.file_name) == full_model_path for model in already_tracked_files):
                    if model_file not in ignored_model_files and not ignored_subfolder:
                        self._logger.info(
                            f"'{model_file}' is not tracked, collecting data...")

                        data = {
                            "file_name": model_file,
                            "folder": root,
                            "sha256": hashing_utility.hash_with_sha256(os.path.join(root, model_file))
                        }
                        self._db._post(
                            "model_file", self._db.model["model_file"](**data))

                    else:
                        self._logger.info(f"Ignoring '{model_file}'.")
                else:
                    self._logger.info(f"'{model_file}' is already tracked.")

    def update_metadata(self, *args: Optional[List], **kwargs: Optional[dict]) -> None:
        """
        Method for updating cached metadata.
        :param args: Arbitrary arguments.
        :param kwargs: Arbitrary keyword arguments.
        """
        pass

    def organize_models(self, *args: Optional[List], **kwargs: Optional[dict]) -> None:
        """
        Method for organizing local models.
        :param args: Arbitrary arguments.
        :param kwargs: Arbitrary keyword arguments.
        """
        pass

    def move_model(self, *args: Optional[List], **kwargs: Optional[dict]) -> None:
        """
        Method for moving local model and adjusting metadata.
        :param args: Arbitrary arguments.
        :param kwargs: Arbitrary keyword arguments.
        """
        pass
