# -*- coding: utf-8 -*-
"""
****************************************************
*                CommonPhysicalDataModel                 
*            (c) 2022 Alexander Hering             *
****************************************************
"""
from typing import Any, List, Optional
import hashlib
import logging
import functools
import copy
import os
from .plugins import BackendPlugin
from common_plugin_controller.model.exceptions import PluginImportException
from common_plugin_controller.control.common_plugin_controller import PluginController
from .common_sqlalchemy_interface import SQLAlchemyEntityInterface
from ..static_utility.filter_mask import FilterMask


def hash_password(password: str) -> str:
    """
    Function for hashing passwords.
    :param password: Password to hash.
    :return: Hashed password.
    """
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def authorize(func: Any) -> Any:
    """
    Decorator method for wrapping interfacing methods and handling authorization.
    :param func: Function to wrap.
    :return: Function wrapper.
    """

    def func_wrapper(*args: Optional[Any], **kwargs: Optional[Any]) -> Any:
        """
        Function wrapper to be configured as decorator.
        :param args: Arguments. Arguments should contain model instance as first argument and target entity type as
            second argument.
        :param kwargs: Arbitrary keyword arguments. Arguments should contain the password hash under 'authorize' if
            entity type is protected.
        :return: Result of wrapped function.
        """
        res = None
        if len(args) < 2 or not isinstance(args[0], PhysicalDataModel):
            instance = args[0]
            gateway = instance.get_entity_type_gateways(args[1])

            if "authorize" not in gateway or hash_password(kwargs.get("authorize")) == gateway["authorize"]:
                res = func(*args, **kwargs)
        return res

    return func_wrapper


class PhysicalDataModel(object):
    """
    Class, representing Physical Data Model objects.
    A Physical Data Model contains information on
        - environment
        - entities
        - linkage
        (- view)
    and handles interfacing tasks.
    """

    def __init__(self, environment_profiles: dict, entity_profiles: dict, linkage_profiles: dict = None,
                 view_profiles: dict = None) -> None:
        """
        Method for initiating Phyiscal Data Models.
        :param environment_profiles: Environment profiles for entity profiles.
        :param entity_profiles: Physical Data Model for data entities.
        :param linkage_profiles: Physical Data Model for connecting to other data entities.
        :param view_profiles: Visual representation profiles.
        """
        self._logger = logging.getLogger("[PDM]")
        self._environment_profiles = environment_profiles
        self._entity_profiles = entity_profiles
        self._linkage_profiles = linkage_profiles if linkage_profiles is not None else {}
        self._view_profiles = view_profiles if view_profiles is not None else {}

        # Cache for fast-access temporary configuration and data
        self.cache = {
            "keys": {
                entity_type: [] for entity_type in self._entity_profiles
            }
        }

        # Plugin Controller for backend and more complex transformation functionalities.
        self._plugin_controller = PluginController()
        # Gateway, transforming data on PDM-level entry and exit
        self._gateways = self._populate_gateway_barriers()
        # Routing, handling forwarding to data backend
        self._routing = self._initiate_routing()

    """
    Initiation methods
    """

    def _populate_gateway_barriers(self) -> dict:
        """
        Method for populating gateway barriers.
        :return: Gateway dictionary.
        """
        gateway = {
            entity_type: {
            } for entity_type in self._entity_profiles
        }
        for entity_type in self._entity_profiles:
            authorization = self._entity_profiles[entity_type].get(
                "#meta", {}).get("authorize")
            if authorization:
                gateway[entity_type]["authorize"] = authorization
        return gateway

    def _initiate_routing(self) -> dict:
        """
        Method for initiating infrastructure.
        :return: Routing dictionary.
        """
        routing = {entity_type: [] for entity_type in self._entity_profiles}
        for environment_profile in self._environment_profiles:
            profile = self._environment_profiles[environment_profile]

            if isinstance(profile["targets"], str) and profile["targets"] == "*":
                targets = self._entity_profiles
            else:
                targets = {entity_type: self._entity_profiles[entity_type] for entity_type in
                           profile["targets"]}

            if profile["backend"] == "database":
                if self._environment_profiles[environment_profile]["framework"] == "sqlalchemy":
                    interface = SQLAlchemyEntityInterface(
                        profile,
                        targets,
                        self._linkage_profiles,
                        self._view_profiles)
                    interface.initiate_infrastructure()
                    for target in targets:
                        routing[target].append(interface)
            elif profile["backend"] == "filestore":
                # TODO: Implement or use and interface existing file store backend
                pass
            elif profile["backend"] == "plugin":
                plugin = None
                if profile["framework"] in self._plugin_controller.plugins["backend"]:
                    plugin = self._plugin_controller.plugins["backend"][profile["framework"]]
                elif os.path.exists(profile["framework"]):
                    plugin = self._plugin_controller.dynamically_load_plugin(
                        profile["framework"])
                if plugin is not None and isinstance(plugin, BackendPlugin):
                    interface = plugin.get_interface(
                        profile, targets, self._linkage_profiles, self._view_profiles)
                    interface.initiate_infrastructure()
                    for target in targets:
                        routing[target].append(interface)
                else:
                    raise PluginImportException(plugin, "BackendPlugin")

        return routing

    """
    Getter methods
    """

    def get_entity_type_gateways(self, entity_type: str) -> dict:
        """
        Method for getting gateway dictionary.
        :param entity_type: Entity type.
        :return: Gateway dictionary.
        """
        return self._gateways.get(entity_type, {})

    """
    Interfacing methods
    """

    @authorize
    def get(self, entity_type: str, filters: List[FilterMask], **kwargs: Optional[Any]) -> Optional[Any]:
        """
        Method for acquiring entity data.
        :param entity_type: Entity type.
        :param filters: A list of Filtermasks declaring constraints.
        :param kwargs: Arbitrary keyword arguments.
            'authorize': Optional password, if data requires authorization.
        :return: Target entity data.
        """
        return self._routing[entity_type].get(entity_type, filters, **kwargs)

    @authorize
    def post(self, entity_type: str, entity_data: dict, **kwargs: Optional[Any]) -> Optional[Any]:
        """
        Method for adding new entity.
        :param entity_type: Entity type.
        :param entity_data: Dictionary containing entity data.
        :param kwargs: Arbitrary keyword arguments.
            'authorize': Optional password, if data requires authorization.
        :return: Target entity data.
        """
        return self._routing[entity_type].post(entity_type, entity_data, **kwargs)

    @authorize
    def patch(self, entity_type: str, filters: List[FilterMask], entity_data: dict, **kwargs: Optional[Any]) -> Optional[Any]:
        """
        Method for patching existing entity.
        :param entity_type: Entity type.
        :param filters: A list of Filtermasks declaring constraints.
        :param entity_data: Dictionary containing entity data.
        :param kwargs: Arbitrary keyword arguments.
            'authorize': Optional password, if data requires authorization.
        :return: Target entity data.
        """
        return self._routing[entity_type].patch(entity_type, filters, entity_data, **kwargs)

    @authorize
    def delete(self, entity_type: str, filters: List[FilterMask], **kwargs: Optional[Any]) -> Optional[Any]:
        """
        Method for deleting entity.
        :param entity_type: Entity type.
        :param filters: A list of Filtermasks declaring constraints.
        :param kwargs: Arbitrary keyword arguments.
            'force_delete': Optional force deletion flag for ignoring soft deletion options.
            'authorize': Optional password, if data requires authorization.
        :return: Target entity data.
        """
        return self._routing[entity_type].delete(entity_type, filters, **kwargs)

    @authorize
    def get_batch(self, entity_type: str, filters_list: List[List[FilterMask]], **kwargs: Optional[Any]) -> List[Any]:
        """
        Method for acquring entity_data for multiple entities.
        :param entity_type: Entity type.
        :param filters_list: A list of lists of Filtermasks declaring constraints. Each separate list of Filtermasks describes 'OR'-constraints for one entry.
        :param kwargs: Arbitrary keyword arguments.
            'authorize': Optional password, if data requires authorization.
        :return: Target entity data.
        """
        return self._routing[entity_type].get_batch(entity_type, filters_list, **kwargs)

    @authorize
    def post_batch(self, entity_type: str, entity_data: List[dict], **kwargs: Optional[Any]) -> List[Any]:
        """
        Method for adding multiple entities.
        :param entity_type: Entity type.
        :param entity_data: List of dictionaries containing entity data.
        :param kwargs: Arbitrary keyword arguments.
            'authorize': Optional password, if data requires authorization.
        :return: Target entity data.
        """
        return self._routing[entity_type].post_batch(entity_type, entity_data, **kwargs)

    @authorize
    def patch_batch(self, entity_type: str, filters_list: List[List[FilterMask]], entity_data: List[dict], **kwargs: Optional[Any]) -> \
            List[Any]:
        """
        Method for patching multiple existing entities.
        :param entity_type: Entity type.
        :param filters_list: A list of lists of Filtermasks declaring constraints. Each separate list of Filtermasks describes 'OR'-constraints for one entry.
        :param entity_data: List of dictionaries containing entity data.
        :param kwargs: Arbitrary keyword arguments.
            'authorize': Optional password, if data requires authorization.
        :return: Target entity data.
        """
        return self._routing[entity_type].patch_batch(entity_type, filters_list, entity_data, **kwargs)

    @authorize
    def delete_batch(self, entity_type: str, filters_list: List[List[FilterMask]], **kwargs: Optional[Any]) -> List[Any]:
        """
        Method for deleting multiple entities.
        :param entity_type: Entity type.
        :param filters_list: A list of lists of Filtermasks declaring constraints. Each separate list of Filtermasks describes 'OR'-constraints for one entry.
        :param kwargs: Arbitrary keyword arguments.
            'force_delete': Optional force deletion flag for ignoring soft deletion options.
            'authorize': Optional password, if data requires authorization.
        :return: Target entity data.
        """
        return self._routing[entity_type].delete_batch(entity_type, filters_list, **kwargs)
