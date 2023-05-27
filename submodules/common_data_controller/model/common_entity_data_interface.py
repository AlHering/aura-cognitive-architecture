# -*- coding: utf-8 -*-
"""
****************************************************
*                     Utility
*            (c) 2022 Alexander Hering             *
****************************************************
"""
from abc import ABC, abstractmethod
import copy
from typing import List, Optional, Union, Any
from ..static_utility import environment_utility
from common_plugin_controller.control.common_plugin_controller import PluginController
from .plugins import ObfuscatorPlugin
from ..static_utility.filter_mask import FilterMask


def handle_gateways(filter_index: int = None, data_index: int = None) -> Any:
    """
    Decorator method for wrapping interfacing methods and handling defaults, obfuscation and deobuscation.
    :param filter_index: Index of filter argument.
    :param data_index: Index of data argument.
    :return: Function wrapper.
    """

    def decorator(func: Any) -> Any:
        """
        Decorator method for decorating interfacing functions.
        :param func: Interfacing function.
        :return: Interfacing function decorator.
        """
        batch = func.__name__.endswith("_batch")
        interface_method = func.__name__.replace("_batch", "")

        def func_wrapper(*args: Optional[Any], **kwargs: Optional[Any]) -> Any:
            """
            Function wrapper for wrapping decorated function.
            :param args: Arguments. Arguments should contain interface instance as first argument and target entity type
                as second argument.
            :param kwargs: Arbitrary keyword arguments.
            :return: Result of wrapped function.
            """
            res = None
            if len(args) < 2 or not isinstance(args[0], CommonEntityDataInterface):
                instance = args[0]
                entity_type = args[1]

                if filter_index is not None:
                    instance.obfuscate_filters(
                        entity_type, args[filter_index], batch)
                if data_index is not None:
                    instance.set_defaults(
                        entity_type, interface_method, args[data_index], batch)
                    instance.obfuscate_entity_data(
                        entity_type, args[data_index], batch)

                res = instance.deobfuscate_entity_data(
                    entity_type, func(*args, **kwargs), batch)
                if kwargs.get("return_as_dict", False):
                    if batch:
                        res = [instance.data_to_dictionary(
                            entry) for entry in res]
                    else:
                        res = instance.data_to_dictionary(res)
            return res

        return func_wrapper

    return decorator


class CommonEntityDataInterface(ABC):
    """
    Abstract class for common data handle objects.
    """

    def __init__(self, environment_profile: dict, entity_profiles: dict, linkage_profiles: dict = None,
                 view_profiles: dict = None, plugin_controller: PluginController = None) -> None:
        """
        Method for initiating common data handle object.
        :param environment_profile: Environment profile for entity profiles.
        :param entity_profiles: Physical Data Model for data entities.
        :param linkage_profiles: Physical Data Model for connecting to other data entities.
        :param view_profiles: Visual representation profiles.
        :param plugin_controller: Plugin Controller.
        """
        self._environment_profile = copy.deepcopy(environment_profile)
        self._entity_profiles = copy.deepcopy(entity_profiles)
        self._linkage_profiles = copy.deepcopy(linkage_profiles)
        self._view_profiles = copy.deepcopy(view_profiles)
        self.plugin_controller = plugin_controller

        self.cache = {
            "keys": {
                entity_type: [] for entity_type in self._entity_profiles
            }
        }

        self._gateways = self._populate_gateway_barriers()
        self._defaults = self._populate_default_parsers()

    """
    Initiation methods
    """

    @abstractmethod
    def initiate_infrastructure(self) -> None:
        """
        Abstract method for initiating infrastructure.
        """
        pass

    def _populate_gateway_barriers(self) -> dict:
        """
        Method for populating gateway barriers.
        :return: Gateway dictionary.
        """
        gateways = {
            entity_type: {
            } for entity_type in self._entity_profiles
        }
        for entity_type in self._entity_profiles:
            obfuscate = self._entity_profiles[entity_type].get(
                "#meta", {}).get("obfuscate")
            deobfuscate = self._entity_profiles[entity_type].get(
                "#meta", {}).get("deobfuscate")
            if obfuscate:
                if obfuscate.startswith("lambda"):
                    gateways[entity_type]["obfuscate"] = environment_utility.get_lambda_function_from_string(
                        obfuscate)
                elif isinstance(self.plugin_controller.plugins.get("obfuscator", {}).get(obfuscate, ""), ObfuscatorPlugin):
                    gateways[entity_type]["obfuscate"] = self.plugin_controller.plugins["obfuscator"][obfuscate].obfuscate
            if deobfuscate:
                if deobfuscate.startswith("lambda"):
                    gateways[entity_type]["deobfuscate"] = environment_utility.get_lambda_function_from_string(
                        deobfuscate)
                elif isinstance(self.plugin_controller.plugins.get("obfuscator", {}).get(deobfuscate, ""), ObfuscatorPlugin):
                    gateways[entity_type]["deobfuscate"] = self.plugin_controller.plugins["obfuscator"][deobfuscate].deobfuscate
        return gateways

    def _populate_default_parsers(self) -> dict:
        """
        Method for initiating argument parser for default value insertion.
        :return: Default parser dictionary.
        """
        argument_parsers = {
            entity_type: {
                "post": {},
                "patch": {},
                "delete": {}
            } for entity_type in self._entity_profiles
        }
        for entity_type in self._entity_profiles:
            for key in [key for key in self._entity_profiles[entity_type]]:
                for option in [opt for opt in ["post", "patch", "delete"] if
                               opt in self._entity_profiles[entity_type][key]]:
                    argument_parsers[entity_type][option][key] = \
                        self._entity_profiles[entity_type][key][option]
                if self._entity_profiles[entity_type][key].get("key", False) and key not in self.cache["keys"][entity_type]:
                    self.cache["keys"][entity_type].append(key)
        return argument_parsers

    """
    Gateway methods
    """

    def set_defaults(self, entity_type: str, method_type: str, data: Union[list, dict, Any], batch: bool = False) \
            -> None:
        """
        Method for setting default value.
        :param entity_type: Entity type.
        :param method_type: Method type out of 'post', 'patch' and 'delete'
        :param data: Data to set standard values for.
        :param batch: Flag, declaring whether data contains multiple entries. Defaults to False.
        """
        if self._defaults[entity_type].get(method_type, False):
            if isinstance(data, dict):
                for key in self._defaults[entity_type][method_type]:
                    data[key] = self._defaults[entity_type][method_type][key](
                        data)
            elif not batch:
                for key in self._defaults[entity_type][method_type]:
                    setattr(
                        data, key, self._defaults[entity_type][method_type][key](data))
            else:
                for data_entry in data:
                    self.set_defaults(entity_type, data_entry, data_entry)

    def obfuscate_filters(self, entity_type: str, filters: Union[List[FilterMask], List[List[FilterMask]]], batch: bool = False) -> None:
        """
        Method for obfuscating filters.
        :param entity_type: Entity type.
        :param filters: List of FilterMasks or list of lists of FilterMasks in case of batch filtering.
        :param batch: Flag, declaring whether filters contain multiple entries. Defaults to False.
        """
        if "obfuscate" in self._gateways[entity_type] and filters:
            if not batch:
                for filtermask in filters:
                    filtermask.transform(
                        self._gateways[entity_type]["obfuscate"])
            else:
                for filter_list in filters:
                    self.obfuscate_filters(entity_type, filter_list)

    def obfuscate_entity_data(self, entity_type: str, data: Union[dict, list, Any], batch: bool = False) -> None:
        """
        Method for obfuscating entity data.
        :param entity_type: Entity type.
        :param data: Entity data or list of entity data entries.
        :param batch: Flag, declaring whether data contains multiple entries. Defaults to False.
        """
        # TODO: Allow for usage of Transformation Plugins
        if "obfuscate" in self._gateways[entity_type] and data:
            if isinstance(data, dict):
                for key in self._gateways[entity_type]["obfuscate"]:
                    data[key] = self._gateways[entity_type]["obfuscate"][key](
                        data, key)
            elif not batch:
                for key in self._gateways[entity_type]["obfuscate"]:
                    setattr(
                        data, key, self._gateways[entity_type]["obfuscate"][key](data, key))
            else:
                for data_entry in data:
                    self.obfuscate_entity_data(entity_type, data_entry)

    def deobfuscate_entity_data(self, entity_type: str, data: Union[dict, list, Any], batch: bool = False) -> None:
        """
        Method for deobfuscating data.
        :param entity_type: Entity type.
        :param data: Entity data or list of entity data entries.
        :param batch: Flag, declaring whether data contains multiple entries. Defaults to False.
        """
        if "deobfuscate" in self._gateways[entity_type] and data:
            if isinstance(data, dict):
                for key in self._gateways[entity_type]["deobfuscate"]:
                    data[key] = self._gateways[entity_type]["deobfuscate"][key](
                        data, key)
            elif not batch:
                for key in self._gateways[entity_type]["deobfuscate"]:
                    setattr(
                        data, key, self._gateways[entity_type]["deobfuscate"][key](data, key))
            else:
                for data_entry in data:
                    self.deobfuscate_entity_data(entity_type, data_entry)

    def filters_from_data(self, entity_type: str, data: Any) -> list:
        """
        Method to derive filters from data.
        :param entity_type: Entity type.
        :param data: Entity data.
        :return: Filter masks for data.
        """
        if self.cache["keys"].get(entity_type, False):
            return [[key, "==", data[key] if isinstance(data, dict) else getattr(data, key)] for key in
                    self.cache["keys"][entity_type]]
        else:
            return [[key, "==", data[key] if isinstance(data, dict) else getattr(data, key)] for key in data]

    def data_to_dictionary(self, entity_type: str, data: Any) -> dict:
        """
        Method for transforming data object to dictionary.
        :param entity_type: Entity type.
        :param data: Data object.
        :return: Dictionary, representing data object.
        """
        return data if isinstance(data, dict) else {key: getattr(data, key) for key in
                                                    self._entity_profiles[entity_type] if key != "#meta"}

    """
    Interfacing methods
    """

    @abstractmethod
    def _get_obj(self, entity_type: str, filters: List[FilterMask], **kwargs: Optional[Any]) -> Optional[Any]:
        """
        Abstract method for acquring entity_data.
        :param entity_type: Entity type.
        :param filters: A list of Filtermasks declaring constraints.
        :param kwargs: Arbitrary keyword arguments.
            'return_as_dict': Flag declaring, whether return values should be formatted as dictionaries.
        :return: Target entity data.
        """
        pass

    @handle_gateways(filter_index=2, data_index=None)
    def get(self, entity_type: str, filters: List[FilterMask], **kwargs: Optional[Any]) -> Optional[Any]:
        """
        Abstract method for acquring entity_data.
        :param entity_type: Entity type.
        :param filters: A list of Filtermasks declaring constraints.
        :param kwargs: Arbitrary keyword arguments.
            'return_as_dict': Flag declaring, whether return values should be formatted as dictionaries.
        :return: Target entity data.
        """
        return self._get_obj(entity_type, filters, **kwargs)

    @abstractmethod
    def _post_obj(self, entity_type: str, entity_data: dict, **kwargs: Optional[Any]) -> Optional[Any]:
        """
        Abstract method for adding new entity.
        :param entity_type: Entity type.
        :param entity_data: Dictionary containing entity data.
        :param kwargs: Arbitrary keyword arguments.
            'return_as_dict': Flag declaring, whether return values should be formatted as dictionaries.
        :return: Target entity data if existing, else None.
        """
        pass

    @handle_gateways(filter_index=None, data_index=2)
    def post(self, entity_type: str, entity_data: dict, **kwargs: Optional[Any]) -> Optional[Any]:
        """
        Abstract method for adding new entity.
        :param entity_type: Entity type.
        :param entity_data: Dictionary containing entity data.
        :param kwargs: Arbitrary keyword arguments.
            'return_as_dict': Flag declaring, whether return values should be formatted as dictionaries.
        :return: Target entity data if existing, else None.
        """
        return self._post_obj(entity_type, entity_data, **kwargs)

    @abstractmethod
    def _patch_obj(self, entity_type: str, filters: List[FilterMask], entity_data: dict, **kwargs: Optional[Any]) -> Optional[Any]:
        """
        Abstract method for patching existing entity.
        :param entity_type: Entity type.
        :param filters: A list of Filtermasks declaring constraints.
        :param entity_data: Dictionary containing entity data.
        :param kwargs: Arbitrary keyword arguments.
            'return_as_dict': Flag declaring, whether return values should be formatted as dictionaries.
        :return: Target entity data if existing, else None.
        """
        pass

    @handle_gateways(filter_index=2, data_index=3)
    def patch(self, entity_type: str, filters: List[FilterMask], entity_data: dict, **kwargs: Optional[Any]) -> Optional[Any]:
        """
        Abstract method for patching existing entity.
        :param entity_type: Entity type.
        :param filters: A list of Filtermasks declaring constraints.
        :param entity_data: Dictionary containing entity data.
        :param kwargs: Arbitrary keyword arguments.
            'return_as_dict': Flag declaring, whether return values should be formatted as dictionaries.
        :return: Target entity data if existing, else None.
        """
        return self._patch_obj(entity_type, filters, entity_data, **kwargs)

    @abstractmethod
    def _delete_obj(self, entity_type: str, filters: List[FilterMask], **kwargs: Optional[Any]) -> Optional[Any]:
        """
        Abstract method for deleting entity.
        :param entity_type: Entity type.
        :param filters: A list of Filtermasks declaring constraints.
        :param kwargs: Arbitrary keyword arguments.
            'return_as_dict': Flag declaring, whether return values should be formatted as dictionaries.
        :return: Target entity data if existing, else None.
        """
        pass

    @handle_gateways(filter_index=2, data_index=None)
    def delete(self, entity_type: str, filters: List[FilterMask], **kwargs: Optional[Any]) -> Optional[Any]:
        """
        Abstract method for deleting entity.
        :param entity_type: Entity type.
        :param filters: A list of Filtermasks declaring constraints.
        :param kwargs: Arbitrary keyword arguments.
            'return_as_dict': Flag declaring, whether return values should be formatted as dictionaries.
        :return: Target entity data if existing, else None.
        """
        return self._delete_obj(entity_type, filters, **kwargs)

    @handle_gateways(filter_index=2, data_index=None)
    def get_batch(self, entity_type: str, filters_list: List[List[FilterMask]], **kwargs: Optional[Any]) -> List[Any]:
        """
        Abstract method for acquring entity_data for multiple entities.
        :param entity_type: Entity type.
        :param filters_list: :param filters_list: A list of lists of Filtermasks declaring constraints. Each separate list of Filtermasks describes 'OR'-constraints for one entry.
        :param kwargs: Arbitrary keyword arguments.
            'return_as_dict': Flag declaring, whether return values should be formatted as dictionaries.
        :return: Target entity data entries.
        """
        results = [self._get_obj(entity_type, filters, **kwargs)
                   for filters in filters_list]
        return [entry for entry in results if entry is not None]

    @handle_gateways(filter_index=None, data_index=2)
    def post_batch(self, entity_type: str, entity_data: List[dict], **kwargs: Optional[Any]) -> List[Any]:
        """
        Abstract method for adding multiple entities.
        :param entity_type: Entity type.
        :param entity_data: List of dictionaries containing entity data.
        :param kwargs: Arbitrary keyword arguments.
            'return_as_dict': Flag declaring, whether return values should be formatted as dictionaries.
        :return: Target entity data entries.
        """
        results = [self._post_obj(entity_type, entity_data_entry, **kwargs)
                   for entity_data_entry in entity_data]
        return [entry for entry in results if entry is not None]

    @handle_gateways(filter_index=2, data_index=3)
    def patch_batch(self, entity_type: str, filters_list: List[List[FilterMask]], entity_data: List[dict], **kwargs: Optional[Any]) -> \
            List[Any]:
        """
        Abstract method for patching multiple existing entities.
        :param entity_type: Entity type.
        :param filters_list: A list of lists of Filtermasks declaring constraints. Each separate list of Filtermasks describes 'OR'-constraints for one entry.
        :param entity_data: List of dictionaries containing entity data.
        :param kwargs: Arbitrary keyword arguments.
            'return_as_dict': Flag declaring, whether return values should be formatted as dictionaries.
        :return: Target entity data entries.
        """
        results = [self._patch_obj(entity_type, *entry, **kwargs)
                   for entry in zip(filters_list, entity_data)]
        return [entry for entry in results if entry is not None]

    @handle_gateways(filter_index=2, data_index=None)
    def delete_batch(self, entity_type: str, filters_list: List[List[FilterMask]], **kwargs: Optional[Any]) -> List[Any]:
        """
        Abstract method for deleting multiple entities.
        :param entity_type: Entity type.
        :param filters_list: A list of lists of Filtermasks declaring constraints. Each separate list of Filtermasks describes 'OR'-constraints for one entry.
        :param kwargs: Arbitrary keyword arguments.
            'return_as_dict': Flag declaring, whether return values should be formatted as dictionaries.
        :return: Target entity data entries.
        """
        results = [self._delete_obj(
            entity_type, filters, **kwargs) for filters in filters_list]
        return [entry for entry in results if entry is not None]

    """
    Linkage methods
    """

    @abstractmethod
    def get_linked_entities(self, linkage: str, source_filters: List[FilterMask], target_filters: list = [],
                            **kwargs: Optional[Any]) -> list:
        """
        Method for getting linked entities.
        :param linkage: Linkage profile.
        :param source_filters: Source filters.
        :param target_filters: Target filters. Defaults to empty list.
        :param kwargs: Arbitrary keyword arguments.
            'return_as_dict': Flag declaring, whether return values should be formatted as dictionaries.
        :return: Linked entities.
        """
        pass

    @abstractmethod
    def link_entities(self, linkage: str, source_filters: List[FilterMask], target_filters: List[FilterMask] = [],
                      **kwargs: Optional[Any]) -> None:
        """
        Method for getting linked entities.
        :param source_filters: Source Filtermasks declaring constraints.
        :param linkage: Linkage profile.
        :param target_filters: Target Filtermasks declaring constraints. Defaults to empty list.
        :param kwargs: Arbitrary keyword arguments.
            'return_as_dict': Flag declaring, whether return values should be formatted as dictionaries.
        :return: Linked entities.
        """
        pass
