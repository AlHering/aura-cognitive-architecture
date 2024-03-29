# -*- coding: utf-8 -*-
"""
****************************************************
*           aura-cognitive-architecture            *
*            (c) 2023 Alexander Hering             *
****************************************************
"""
import requests
import json
from time import sleep
import shutil
from logging import Logger
from typing import Any, Optional, List
from src.utility.silver import image_utility, internet_utility
from src.configuration import configuration as cfg
import abc


class AbstractAPIWrapper(abc.ABC):
    """
    Abstract class, representing a API wrapper object.
    Such wrappers are used for connecting to model services.
    """

    @abc.abstractmethod
    def check_connection(self, *args: Optional[List], **kwargs: Optional[dict]) -> bool:
        """
        Abstract method for checking connection.
        :param args: Arbitrary arguments.
        :param kwargs: Arbitrary keyword arguments.
        :return: True if connection was established successfuly else False.
        """
        pass

    @abc.abstractmethod
    def get_api_url(self, identifier: str, model_id: Any, *args: Optional[List], **kwargs: Optional[dict]) -> str:
        """
        Abstract method for acquring API URL for model.
        :param identifier: Type of identification.
        :model_id: Identification of specified type.
        :param args: Arbitrary arguments.
        :param kwargs: Arbitrary keyword arguments.
        :return: API URL for given model ID.
        """
        pass

    @abc.abstractmethod
    def collect_metadata(self, identifier: str, model_id: Any, *args: Optional[List], **kwargs: Optional[dict]) -> dict:
        """
        Abstract method for acquring model data by identifier.
        :param identifier: Type of identification.
        :model_id: Identification of specified type.
        :param args: Arbitrary arguments.
        :param kwargs: Arbitrary keyword arguments.
        :return: Metadata for given model ID.
        """
        pass

    @abc.abstractmethod
    def normalize_metadata(self, metadata: dict, *args: Optional[List], **kwargs: Optional[dict]) -> dict:
        """
        Abstract method for normalizing metadata.
        :param metadata: Metadata.
        :param args: Arbitrary arguments.
        :param kwargs: Arbitrary keyword arguments.
        :return: Normalized metadata.
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


class CivitaiAbstractAPIWrapper(AbstractAPIWrapper):
    """
    Class, representing civitai API wrapper.
    """

    def __init__(self) -> None:
        """
        Initiation method.
        """
        self._logger = Logger("[CivitaiAbstractAPIWrapper]")
        self.authorization = cfg.ENV["CIVITAI_API_KEY"]
        self.base_url = "https://civitai.com/"
        self.api_base_url = "https://civitai.com/api/v1/"
        self.model_by_versionhash_url = "https://civitai.com/api/v1/model-versions/by-hash/"
        self.model_by_id_url = "https://civitai.com/api/v1/models/"

    def check_connection(self, *args: Optional[List], **kwargs: Optional[dict]) -> bool:
        """
        Method for checking connection.
        :param args: Arbitrary arguments.
        :param kwargs: Arbitrary keyword arguments.
        :return: True if connection was established successfuly else False.
        """
        result = requests.get(self.base_url).status_code == 200
        self._logger.info("Connection was successfuly established.") if result else self._logger.warn(
            "Connection could not be established.")
        return result

    def get_api_url(self, identifier: str, model_id: Any, *args: Optional[List], **kwargs: Optional[dict]) -> str:
        """
        Abstract method for acquring API URL for model.
        :param identifier: Type of identification.
        :model_id: Identification of specified type.
        :param args: Arbitrary arguments.
        :param kwargs: Arbitrary keyword arguments.
        :return: API URL for given model ID.
        """
        return {"hash": self.model_by_versionhash_url, "id": self.model_by_id_url}[identifier] + str(model_id)

    def collect_metadata(self, identifier: str, model_id: Any, *args: Optional[List], **kwargs: Optional[dict]) -> dict:
        """
        Method for acquring model data by identifier.
        :param identifier: Type of identification.
        :model_id: Identification of specified type.
        :param args: Arbitrary arguments.
        :param kwargs: Arbitrary keyword arguments.
        :return: Metadata for given model ID.
        """
        self._logger.info(
            f"Fetching metadata for model with '{model_id}' as '{identifier}'...")
        resp = requests.get(self.get_api_url(identifier, model_id), headers={
                            "Authorization": self.authorization})
        try:
            meta_data = json.loads(resp.content)
            if meta_data is not None and not "error" in meta_data:
                self._logger.info(f"Fetching metadata was successful.")
                return meta_data
            else:
                self._logger.warn(f"Fetching metadata failed.")
        except json.JSONDecodeError:
            self._logger.warn(f"Metadata response could not be deserialized.")
            return {}

    def normalize_metadata(self, metadata: dict, **kwargs: Optional[dict]) -> dict:
        """
        Method for normalizing metadata.
        :param metadata: Metadata.
        :param kwargs: Arbitrary keyword arguments.
        :return: Normalized metadata.
        """
        # TODO: Implement, once common metadata format is planned out.
        pass

    def download_model(self, *args: Optional[List], **kwargs: Optional[dict]) -> None:
        """
        Abstract method for downloading a model.
        :param args: Arbitrary arguments.
        :param kwargs: Arbitrary keyword arguments.
        """
        pass

    def download_asset(self, asset_type: str, url: str, output_path: str) -> bool:
        """
        Method for downloading assets to disk.
        :param asset_type: Asset type.
        :param url: Asset URL.
        :param output_path: Output path.
        :return: True, if process was successful, else False.
        """
        if asset_type == "image":
            return self.downloading_image(url, output_path)

    @internet_utility.timeout(360.0)
    def download_image(self, url: str, output_path: str) -> bool:
        """
        Method for downloading images to disk.
        :param url: Image URL.
        :param output_path: Output path.
        :return: True, if process was successful, else False.
        """
        sleep(2)
        download = requests.get(url, stream=True, headers={
                                "Authorization": self.authorization})
        with open(output_path, 'wb') as file:
            shutil.copyfileobj(download.raw, file)
        del download
        if image_utility.check_image_health(output_path):
            return True
        else:
            return False
