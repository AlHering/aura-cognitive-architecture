# -*- coding: utf-8 -*-
"""
****************************************************
*           aura-cognitive-architecture            *
*            (c) 2023 Alexander Hering             *
****************************************************
"""
from typing import Any, Optional, List
import abc
from ...utility.bronze import json_utility


class AbstractModelHandler(object):
    """
    Class, representing ML Model Handler objects.
    A Model Handler utilizes API Wrappers for collecting metadata and downloading assets from
    model services and managing updates, organization and usage.
    """

    def __init__(self) -> None:
        """
        Initiation method.
        """
        pass

    def import_data(self, import_path: str) -> None:
        """
        Method for importing data.
        :param import_path: Import path.
        """
        self.cache = json_utility.load(import_path)

    def export_data(self, export_path: str) -> None:
        """
        Method for exporting data.
        :param export_path: Export path.
        """
        json_utility.save(self.cache, export_path)

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
    def download_model(self, *args: Optional[List], **kwargs: Optional[dict]) -> None:
        """
        Abstract method for downloading a model.
        :param args: Arbitrary arguments.
        :param kwargs: Arbitrary keyword arguments.
        """
        pass

    @abc.abstractmethod
    def download_asset(self, *args: Optional[List], **kwargs: Optional[dict]) -> None:
        """
        Abstract method for downloading an asset.
        :param args: Arbitrary arguments.
        :param kwargs: Arbitrary keyword arguments.
        """
        pass


class StabeDiffusionModelHandler(AbstractModelHandler):
    """
    Class representing Model Handler for Stable Diffusion models.
    """
    pass
