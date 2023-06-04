# -*- coding: utf-8 -*-
"""
****************************************************
*                   Utility
*            (c) 2023 Alexander Hering             *
****************************************************
"""
from abc import ABC, abstractmethod
import copy
import hashlib
from typing import List, Optional, Union, Any
from ..silver import environment_utility
from .filter_mask import FilterMask


def get_authorization_token(password: str) -> str:
    """
    Function for getting an authorization token.
    :param password: Password to get token.
    :return: Token.
    """
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def handle_gateways(filter_index: int = None, data_index: int = None, object_index: int = None) -> Any:
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
            if len(args) >= 2 and isinstance(args[0], EntityDataInterface):
                instance = args[0]
                entity_type = args[1]

                if instance.authorize(entity_type, kwargs.get("authorize")):
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
            return res

        return func_wrapper

    return decorator


class EntityDataInterface(ABC):
    """
    Abstract class for data handle objects.
    Based off of the Common Data Controller and streamlined for faster prototyping.
    In contrast to the Common Entity Data Interfaces, this solution is not split into authentication, transformation and backend layers!
    In contrast to the Common Entity Data Interfaces, this solution does not support Plugins!
    """

    def __init__(self, environment_profile: dict, entity_profiles: dict, linkage_profiles: dict = None,
                 view_profiles: dict = None) -> None:
        """
        Method for initiating data handle object.
        :param environment_profile: Environment profile for entity profiles.
        :param entity_profiles: Physical Data Model for data entities.
        :param linkage_profiles: Physical Data Model for connecting to other data entities.
        :param view_profiles: Visual representation profiles.
        """
        self._environment_profile = copy.deepcopy(environment_profile)
        self._entity_profiles = copy.deepcopy(entity_profiles)
        self._linkage_profiles = copy.deepcopy(linkage_profiles)
        self._view_profiles = copy.deepcopy(view_profiles)

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
            authorize = self._entity_profiles[entity_type].get(
                "#meta", {}).get("authorize")
            if obfuscate is not None:
                gateways[entity_type]["obfuscate"] = environment_utility.get_lambda_function_from_string(
                    obfuscate)
            if deobfuscate is not None:
                gateways[entity_type]["deobfuscate"] = environment_utility.get_lambda_function_from_string(
                    deobfuscate)
            if authorize is not None:
                gateways[entity_type]["authorize"] = authorize
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

    def authorize(self, entity_type: str, password: str) -> bool:
        """
        Method for checking authorized access to an entity type.
        :param entity_type: Entity type.
        :param password: Authorization password.
        :return: Authorization status.
        """
        return "authorize" not in self._gateways[entity_type] or get_authorization_token(password) == self._gateways[entity_type]("authorize")

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
        if "obfuscate" in self._gateways[entity_type] and data:
            if batch:
                for entry in data:
                    self.obfuscate_entity_data(entity_type, entry)
            else:
                data = self._gateways[entity_type]["obfuscate"](data)

    def deobfuscate_entity_data(self, entity_type: str, data: Union[dict, list, Any], batch: bool = False) -> None:
        """
        Method for deobfuscating data.
        :param entity_type: Entity type.
        :param data: Entity data or list of entity data entries.
        :param batch: Flag, declaring whether data contains multiple entries. Defaults to False.
        """
        if "deobfuscate" in self._gateways[entity_type] and data:
            if batch:
                for entry in data:
                    self.deobfuscate_entity_data(entity_type, entry)
            else:
                data = self._gateways[entity_type]["deobfuscate"](data)

    def filters_from_data(self, entity_type: str, data: Any) -> list:
        """
        Method to derive filters from data.
        :param entity_type: Entity type.
        :param data: Entity data.
        :return: Filter masks for data.
        """
        if self.cache["keys"].get(entity_type, False):
            return FilterMask([[key, "==", data[key] if isinstance(data, dict) else getattr(data, key)] for key in
                               self.cache["keys"][entity_type]])
        else:
            return FilterMask([[key, "==", data[key] if isinstance(data, dict) else getattr(data, key)] for key in data])

    def obj_to_dictionary(self, entity_type: str, obj: Any) -> dict:
        """
        Method for transforming data object to dictionary.
        :param entity_type: Entity type.
        :param data: Data object.
        :return: Dictionary, representing data object.
        """
        return obj if isinstance(obj, dict) else {key: getattr(obj, key) for key in
                                                  self._entity_profiles[entity_type] if key != "#meta"}

    """
    Interfacing methods
    """

    @abstractmethod
    @handle_gateways(filter_index=2, data_index=None, object_index=None)
    def _get_obj(self, entity_type: str, filters: List[FilterMask], **kwargs: Optional[Any]) -> Optional[Any]:
        """
        Abstract method for acquring entity as object.
        :param entity_type: Entity type.
        :param filters: A list of Filtermasks declaring constraints.
        :param kwargs: Arbitrary keyword arguments.
        :return: Target entity.
        """
        pass

    @abstractmethod
    @handle_gateways(filter_index=2, data_index=None, object_index=None)
    def _get_dict(self, entity_type: str, filters: List[FilterMask], **kwargs: Optional[Any]) -> Optional[dict]:
        """
        Abstract method for acquring entity data.
        :param entity_type: Entity type.
        :param filters: A list of Filtermasks declaring constraints.
        :param kwargs: Arbitrary keyword arguments.
        :return: Target entity data.
        """
        pass

    @abstractmethod
    def get(self, *args: Optional[Any], **kwargs: Optional[Any]) -> Optional[Any]:
        """
        Abstract method for acquring entity.
        :param args: Arbitrary arguments.
        :param kwargs: Arbitrary keyword arguments.
        :return: Target entity if existing, else None.
        """
        pass

    @abstractmethod
    @handle_gateways(filter_index=None, data_index=None, object_index=2)
    def _post_obj(self, entity_type: str, entity: Any, **kwargs: Optional[Any]) -> Optional[Any]:
        """
        Abstract method for adding a new entity.
        :param entity_type: Entity type.
        :param entity: Entity object.
        :param kwargs: Arbitrary keyword arguments.
        :return: Target entity data if existing, else None.
        """
        pass

    @abstractmethod
    @handle_gateways(filter_index=2, data_index=None, object_index=None)
    def _post_dict(self, entity_type: str, entity_data: dict, **kwargs: Optional[Any]) -> Optional[dict]:
        """
        Abstract method for adding a new entity data as dictionary.
        :param entity_type: Entity type.
        :param entity_data: Dictionary containing entity data.
        :param kwargs: Arbitrary keyword arguments.
        :return: Target entity data if existing, else None.
        """
        pass

    @abstractmethod
    def post(self, *args: Optional[Any], **kwargs: Optional[Any]) -> Optional[Any]:
        """
        Abstract method for adding a new entity.
        :param args: Arbitrary arguments.
        :param kwargs: Arbitrary keyword arguments.
        :return: Target entity if existing, else None.
        """
        pass

    @abstractmethod
    @handle_gateways(filter_index=None, data_index=3, object_index=2)
    def _patch_obj(self, entity_type: str, entity: Any, patch: Optional[dict] = None, **kwargs: Optional[Any]) -> Optional[Any]:
        """
        Abstract method for patching an existing entity.
        :param entity_type: Entity type.
        :param entity: Entity object to patch.
        :param patch: Patch as dictionary, if entity is not already patched.
        :param kwargs: Arbitrary keyword arguments.
        :return: Target entity data if existing, else None.
        """
        pass

    @abstractmethod
    @handle_gateways(filter_index=2, data_index=3, object_index=None)
    def _patch_dict(self, entity_type: str, filters: List[FilterMask], patch: dict, **kwargs: Optional[Any]) -> Optional[dict]:
        """
        Abstract method for patching an existing entity data.
        :param entity_type: Entity type.
        :param filters: A list of Filtermasks declaring constraints.
        :param patch: Patch as dictionary.
        :param kwargs: Arbitrary keyword arguments.
        :return: Target entity data if existing, else None.
        """
        pass

    @abstractmethod
    def patch(self, *args: Optional[Any], **kwargs: Optional[Any]) -> Optional[Any]:
        """
        Abstract method for patching an existing entity.
        :param args: Arbitrary arguments.
        :param kwargs: Arbitrary keyword arguments.
        :return: Target entity if existing, else None.
        """
        pass

    @abstractmethod
    @handle_gateways(filter_index=None, data_index=None, object_index=2)
    def _delete_obj(self, entity_type: str, entity: Any, **kwargs: Optional[Any]) -> Optional[Any]:
        """
        Abstract method for deleting an entity.
        :param entity_type: Entity type.
        :param entity: Entity to delete.
        :param kwargs: Arbitrary keyword arguments.
        :return: Target entity data if existing, else None.
        """
        pass

    @abstractmethod
    @handle_gateways(filter_index=2, data_index=None, object_index=None)
    def _delete_data(self, entity_type: str, filters: List[FilterMask], **kwargs: Optional[Any]) -> Optional[Any]:
        """
        Abstract method for deleting an entity.
        :param entity_type: Entity type.
        :param filters: A list of Filtermasks declaring constraints.
        :param kwargs: Arbitrary keyword arguments.
        :return: Target entity data if existing, else None.
        """
        pass

    @abstractmethod
    def delete(self, *args: Optional[Any], **kwargs: Optional[Any]) -> Optional[Any]:
        """
        Abstract method for deleting an entity.
        :param args: Arbitrary arguments.
        :param kwargs: Arbitrary keyword arguments.
        :return: Target entity if existing, else None.
        """
        pass

    """
    Batch interfacing methods
    """

    @abstractmethod
    def get_batch(self, *args: Optional[Any], **kwargs: Optional[Any]) -> List[Any]:
        """
        Abstract method for getting entities as batch.
        :param args: Arbitrary arguments.
        :param kwargs: Arbitrary keyword arguments.
        :return: Target entity if existing, else None.
        """
        pass

    @abstractmethod
    def post_batch(self, *args: Optional[Any], **kwargs: Optional[Any]) -> List[Any]:
        """
        Abstract method for posting entities as batch.
        :param args: Arbitrary arguments.
        :param kwargs: Arbitrary keyword arguments.
        :return: Target entity if existing, else None.
        """
        pass

    @abstractmethod
    def patch_batch(self, *args: Optional[Any], **kwargs: Optional[Any]) -> List[Any]:
        """
        Abstract method for patching entities as batch.
        :param args: Arbitrary arguments.
        :param kwargs: Arbitrary keyword arguments.
        :return: Target entity if existing, else None.
        """
        pass

    @abstractmethod
    def delete_batch(self, *args: Optional[Any], **kwargs: Optional[Any]) -> List[Any]:
        """
        Abstract method for getting entities as batch.
        :param args: Arbitrary arguments.
        :param kwargs: Arbitrary keyword arguments.
        :return: Target entity if existing, else None.
        """
        pass

    """
    Linkage methods
    """

    @abstractmethod
    def get_linked_entities(self, linkage: str, *args: Optional[Any], **kwargs: Optional[Any]) -> List[Any]:
        """
        Method for getting linked entities.
        :param args: Arbitrary arguments.
        :param kwargs: Arbitrary keyword arguments.
        :return: Linked entities.
        """
        pass

    @abstractmethod
    def link_entities(self, linkage: str, *args: Optional[Any], **kwargs: Optional[Any]) -> None:
        """
        Method for getting linked entities.
        :param args: Arbitrary arguments.
        :param kwargs: Arbitrary keyword arguments.
        :return: Linked entities.
        """
        pass
