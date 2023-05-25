# -*- coding: utf-8 -*-
"""
****************************************************
*                  EntityProtocol                  *
*            (c) 2020-2022 Alexander Hering        *
****************************************************
"""
import os
from typing import Union, Any, Optional
from physical_data_model.model.common_entity_data_interface import CommonEntityDataInterface
from physical_data_model.utility import file_system_utility, json_utility, environment_utility


class GenericPlugin(object):
    """
    Generic Plugin class.
    """

    def __init__(self, info: dict, path: str) -> None:
        """
        Representation of a generic plugin.
        :param info: Plugin info.
        :param path: Path to plugin.
        """
        self.path = path
        self.info = info
        self.name = self.info["name"]
        self.type = self.info["type"]
        if "./" in self.info["data_path"]:
            self.info["data_path"] = os.path.normpath(
                os.path.join(path, self.info["data_path"]))
        file_system_utility.safely_create_path(self.info["data_path"])

    def save(self, path: str = None) -> None:
        """
        Method for saving plugin info to file.
        :param path: Plugin path to safe plugin info file to, defaults to None in which case the import path is taken.
        """
        json_utility.save(self.info, os.path.join(
            path, "info.json") if path is not None else os.path.join(self.path, "info.json"))


class ObfuscatorPlugin(GenericPlugin):
    """
    Obfuscator Plugin class, handling data transformation as pipeline component.
    """

    def __init__(self, info: dict, path: str) -> None:
        """
        Representation of an obfuscator plugin, obfuscating or deobfuscating entity data or objects in data pipelines.
        :param info: Plugin info.
        :param path: Path to plugin.
        """
        super().__init__(info, path)
        if "./" in self.info["obfuscator"]:
            self.info["obfuscator"] = os.path.normpath(
                os.path.join(path, self.info["obfuscator"]))
        self.obfuscator = environment_utility.get_module(
            self.info["obfuscator"])

    def obfuscate(self, data: Any, **kwargs: Optional[Any]) -> Any:
        """
        Method for obfuscating data.
        :param data: Data to transform.
        :param kwargs: Arbitrary keyword arguments.
        :return: Transformed data.
        """
        return getattr(self.obfuscator, "obfuscate")(data, **kwargs)

    def deobfuscate(self, data: Any, **kwargs: Optional[Any]) -> Any:
        """
        Method for deobfuscating data.
        :param data: Data to transform.
        :param kwargs: Arbitrary keyword arguments.
        :return: Transformed data.
        """
        return getattr(self.obfuscator, "deobfuscate")(data, **kwargs)


class BackendPlugin(GenericPlugin):
    """
    Backend Plugin class for interfacing data backends.
    """

    def __init__(self, info: dict, path: str) -> None:
        """
        Representation of a backend plugin, defining and interfacing a data backend.
        :param info: Plugin info.
        :param path: Path to plugin.
        """
        super().__init__(info, path)
        if "./" in self.info["interface"]:
            self.info["interface"] = os.path.normpath(
                os.path.join(path, self.info["interface"]))

    def get_interface(self, environment_profile: dict, entity_profiles: dict, linkage_profiles: dict = None,
                      view_profiles: dict = None, **kwargs: Optional[Any]) -> CommonEntityDataInterface:
        """
        Method for initiation the backend's environment.
        :param environment_profile: Environment profile for the current backend.
        :param entity_profiles: Physical Data Model for data entities.
        :param linkage_profiles: Physical Data Model for connecting to other data entities.
        :param view_profiles: Visual representation profiles.
        :param kwargs: Arbitrary keyword arguments.
        :return: Interface instance (based on a CommonEntityDataInterface-class).
        """
        return environment_utility.get_function_from_path(f"{self.info['interface']}:get_interface")(
            environment_profile,
            entity_profiles,
            linkage_profiles,
            view_profiles
        )
