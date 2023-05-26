# -*- coding: utf-8 -*-
"""
****************************************************
*                     Utility
*            (c) 2022 Alexander Hering             *
****************************************************
"""
import copy
from sqlalchemy import and_, or_, not_
from typing import Optional, Any, List, Union
from ..static_utility import sql_utility
from ..static_utility.filter_mask import FilterMask
from ..static_utility.dictionary_utility import get_filter_depth
from ..static_utility.comparison_utility import COMPARISON_METHOD_DICTIONARY as CMD
from .common_entity_data_interface import CommonEntityDataInterface, handle_gateways

# Dictionary, mapping filter types of filters to SQLAlchemy-compatible filters
SQLALCHEMY_FILTER_CONVERTER = {
    "equals": lambda x, y: x == y,
    "not_equals": lambda x, y: not_(x == y),
    "contains": lambda x, y: x.contains(y),
    "not_contains": lambda x, y: not_(x.contains(y)),
    "is_contained": lambda x, y: x.in_(y),
    "not_is_contained": lambda x, y: not_(x.in_(y)),
    "==": lambda x, y: x == y,
    "!=": lambda x, y: or_(x != y, and_(x is None, y is not None)),
    "has": lambda x, y: x.contains(y),
    "not_has": lambda x, y: not_(x.contains(y)),
    "in": lambda x, y: x.in_(y),
    "not_in": lambda x, y: not_(x.in_(y))
}

# Dictionary, defining table for manual linking
PDM_MANUAL_LINKAGE = {
    "id": {
        "type": "int",
        "primary_key": True,
        "autoincrement": True,
        "required": True
    },
    "linkage": {
        "type": "str_180",
        "required": True,
        "description": "Linkage type."
    },
    "source_type": {
        "type": "str_180",
        "required": True,
        "description": "Source type."
    },
    "source_key": {
        "type": "text",
        "required": True,
        "description": "Source key."
    },
    "target_type": {
        "type": "str_180",
        "required": True,
        "description": "Target type."
    },
    "target_key": {
        "type": "text",
        "required": True,
        "description": "Target key."
    }
}


class SQLAlchemyEntityInterface(CommonEntityDataInterface):
    """
    Class representing SQLAlchemy Entity Interface.
    """

    def __init__(self, environment_profile: dict, entity_profiles: dict, linkage_profiles: dict,
                 view_profiles: dict = None) -> None:
        """
        Initiation method for SQLAlchemy Entity Interface.
        :param environment_profile: Environment profile.
        :param entity_profiles: Entity profiles under entity name.
        :param linkage_profiles: Physical Data Model linkage for connecting to other data entities.
        :param view_profiles: Visual representation profiles.
        """
        super().__init__(environment_profile, entity_profiles, linkage_profiles, view_profiles)
        self.base = sql_utility.DECLARATIVE_BASE()
        self.engine = sql_utility.get_engine(environment_profile["arguments"]["database"],
                                             encoding=environment_profile["arguments"].get("encoding", "utf-8"))
        self.model = {}
        self.session_factory = None

    """
    Initiation methods
    """

    def initiate_infrastructure(self) -> None:
        """
        Method for initiating infrastructure.
        """
        # add profile for manual linking
        global PDM_MANUAL_LINKAGE
        self._entity_profiles["PDM_MANUAL_LINKAGE"] = PDM_MANUAL_LINKAGE
        # add dataclasses, based off of with schema args enriched profiles, to model
        for profile in self._entity_profiles:
            self._create_dataclass(profile)

        # create infrastructure and define session factory
        self.base.metadata.create_all(self.engine)
        self.session_factory = sql_utility.get_session_factory(self.engine)

    def _create_dataclass(self, entity_type: str) -> None:
        """
        Internal method for creating dataclass for the given entity type.
        :param entity_type: Entity type.
        """
        mapping_profile = copy.deepcopy(
            {key: {"type": self._entity_profiles[entity_type][key]["type"],
                   "schema_args": {
                       "primary_key": self._entity_profiles[entity_type][key].get("primary_key", False),
                       "nullable": not self._entity_profiles[entity_type][key].get("not_null", False),
                       "comment": self._entity_profiles[entity_type][key].get("description", "")
            }} for key in
                self._entity_profiles[entity_type] if
                key != "#meta"})
        desc = self._entity_profiles[entity_type].get(
            "#meta", {}).get("description", False)
        if desc:
            mapping_profile["#meta"] = {"description": desc}
        for key in mapping_profile:
            if "autoincrement" in mapping_profile[key]:
                mapping_profile[key]["schema_args"]["autoincrement"] = mapping_profile[key]["autoincrement"]
            if "unique" in mapping_profile[key]:
                mapping_profile[key]["schema_args"]["unique"] = mapping_profile[key]["unique"]
        self.model[entity_type] = sql_utility.create_mapping_for_dictionary(self.base, entity_type, mapping_profile,
                                                                            self._linkage_profiles)

    """
    Gateway methods
    """

    def convert_filters(self, entity_type: str, filters: List[FilterMask]) -> list:
        """
        Method for coverting common filters to SQLAlchemy-filter expressions.
        :param entity_type: Entity type.
        :param filters: A list of Filtermasks declaring constraints.
        :return: Filter expressions.
        """
        filter_expressions = []
        for filtermask in filters:
            filter_expressions.extend([
                SQLALCHEMY_FILTER_CONVERTER[exp[1]](getattr(self.model[entity_type], exp[0]),
                                                    exp[2]) for exp in filtermask.expressions])
        return filter_expressions

    """
    Interfacing methods
    """

    # override
    def _get_obj(self, entity_type: str, filters: List[FilterMask], **kwargs: Optional[Any]) -> Optional[Any]:
        """
        Method for acquring entity as object.
        :param entity_type: Entity type.
        :param filters: A list of Filtermasks declaring constraints.
        :param kwargs: Arbitrary keyword arguments.
            'return_as_dict': Flag declaring, whether return values should be formatted as dictionaries.
        :return: Target entity.
        """
        with self.session_factory() as session:
            result = session.query(self.model[entity_type]).filter(
                *self.convert_filters(entity_type, filters)
            ).first()
        return result

    # override
    def _post_obj(self, entity_type: str, entity_data: dict, **kwargs: Optional[Any]) -> Optional[Any]:
        """
        Method for adding new entity.
        :param entity_type: Entity type.
        :param entity_data: Dictionary containing entity data.
        :param kwargs: Arbitrary keyword arguments.
            'return_as_dict': Flag declaring, whether return values should be formatted as dictionaries.
        :return: Target entity data.
        """
        with self.session_factory() as session:
            result = self.model[entity_type](**entity_data)
            session.add(result)
            session.commit()
            session.refresh(result)
        return result

    # override
    def _patch_obj(self, entity_type: str, filters: List[FilterMask], entity_data: dict, **kwargs: Optional[Any]) -> Optional[Any]:
        """
        Method for patching existing entity.
        :param entity_type: Entity type.
        :param filters: A list of Filtermasks declaring constraints.
        :param entity_data: Dictionary containing entity data.
        :param kwargs: Arbitrary keyword arguments.
            'return_as_dict': Flag declaring, whether return values should be formatted as dictionaries.
        :return: Target entity data.
        """
        with self.session_factory() as session:
            result = session.query(self.model[entity_type]).filter(
                *self.convert_filters(entity_type, filters)
            ).first()
            if result:
                for arg in entity_data:
                    setattr(result, arg, entity_data[arg])
                session.commit()
                session.refresh(result)
            return result

    # override
    def _delete_obj(self, entity_type: str, filters: List[FilterMask], **kwargs: Optional[Any]) -> Optional[Any]:
        """
        Method for deleting entity.
        :param entity_type: Entity type.
        :param filters: A list of Filtermasks declaring constraints.
        :param kwargs: Arbitrary keyword arguments.
            'return_as_dict': Flag declaring, whether return values should be formatted as dictionaries.
        :return: Target entity data.
        """
        with self.session_factory() as session:
            result = session.query(self.model[entity_type]).filter(
                *self.convert_filters(entity_type, filters)
            ).first()
            if result:
                session.delete(result)
                session.commit()
        return result

    # override
    @handle_gateways(filter_index=2, data_index=None)
    def get_batch(self, entity_type: str, filters_list: List[List[FilterMask]], **kwargs: Optional[Any]) -> List[dict]:
        """
        Method for acquring entity_data for multiple entities.
        :param entity_type: Entity type.
        :param filters_list: A list of lists of Filtermasks declaring constraints. Each separate list of Filtermasks describes 'OR'-constraints for one entry.
        :param kwargs: Arbitrary keyword arguments.
            'return_as_dict': Flag declaring, whether return values should be formatted as dictionaries.
        :return: Target entity data.
        """
        with self.session_factory() as session:
            result = session.query(self.model[entity_type]).filter(or_(and_(
                *self.convert_filters(entity_type, filters)) for filters in filters_list)).all()
        return result

    # override
    @handle_gateways(filter_index=None, data_index=2)
    def post_batch(self, entity_type: str, entity_data: List[dict], **kwargs: Optional[Any]) -> List[dict]:
        """
        Method for adding multiple entities.
        :param entity_type: Entity type.
        :param entity_data: List of dictionaries containing entity data.
        :param kwargs: Arbitrary keyword arguments.
            'return_as_dict': Flag declaring, whether return values should be formatted as dictionaries.
        :return: Target entity data.
        """
        with self.session_factory() as session:
            result = session.bulk_insert_mappings(
                self.model[entity_type], entity_data)
            session.commit()
        return result

    """
    Linkage methods
    """

    # override
    def get_linked_entities(self, linkage: str, source_filters: List[FilterMask], target_filters: List[FilterMask] = [],
                            **kwargs: Optional[Any]) -> list:
        """
        Method for getting linked entities.
        :param linkage: Linkage profile.
        :param source_filters: Source FilterMasks.
        :param target_filters: Target FilterMasks. Defaults to empty list.
        :param kwargs: Arbitrary keyword arguments.
            'return_as_dict': Flag declaring, whether return values should be formatted as dictionaries.
        :return: Linked entities.
        """
        source_type = self._linkage_profiles[linkage]["source"]
        if self._linkage_profiles[linkage]["linkage_type"] == "foreign_key":
            with self.session_factory() as session:
                result = session.query(self.model[source_type]).filter(
                    *self.convert_filters(source_type, source_filters)
                ).first()
                if result:
                    return getattr(result, linkage)
        elif self._linkage_profiles[linkage]["linkage_type"] == "manual":
            source_key = self._linkage_profiles[linkage]["source_key"]
            target_key = self._linkage_profiles[linkage]["target_key"]

            pdm_filters = [["linkage", "==", linkage],
                           ["source_type", "==", source_type]]

            for primary_key in self.cache["primary_keys"][source_type]:
                pdm_filters.append(["source_key", "==",
                                    [filter_mask[2] for filter_mask in source_filters if filter_mask[0] == primary_key][
                                        0]])

            target_filters = set([sql_utility.python_typing_dictionary[target_key[0]](elem["target_key"]) for elem in
                                  self.get_batch("PDM_MANUAL_LINKAGE", [pdm_filters])])
            target_filters = [[target_key[1], "==", elem]
                              for elem in target_filters]
        elif self._linkage_profiles[linkage]["linkage_type"] == "filter_masks":
            elem = self.get(
                self._linkage_profiles[linkage]["source"], source_filters)
            target_filters.extend([[fm[0], fm[1], elem[fm[2]]]
                                  for fm in self._linkage_profiles[linkage]["linkage"]])
        if target_filters:
            return self.get_batch(self._linkage_profiles[linkage]["target"], [[tf] for tf in target_filters])
        else:
            return []

    # override
    def link_entities(self, linkage: str, source_filters: List[FilterMask], target_filters: List[FilterMask] = [],
                      **kwargs: Optional[Any]) -> None:
        """
        Method for getting linked entities.
        :param source_filters: Source FilterMasks.
        :param linkage: Linkage profile.
        :param target_filters: Target FilterMasks. Defaults to empty list.
        :param kwargs: Arbitrary keyword arguments.
            'return_as_dict': Flag declaring, whether return values should be formatted as dictionaries.
        :return: Linked entities.
        """
        if get_filter_depth(target_filters) == 2:
            target_filters = [target_filters]
        if self._linkage_profiles[linkage]["linkage_type"] == "manual":
            linkage_entries = [{
                "linkage": linkage,
                "source_type": self._linkage_profiles[linkage]["source"],
                "source_key": str([f[2] for f in source_filters if
                                   f[0] == self.cache["primary_keys"][self._linkage_profiles[linkage]["source"]][0]][
                    0]),
                "target_type": self._linkage_profiles[linkage]["target"],
                "target_key": str(
                    [f[2] for f in target if
                     f[0] == self.cache["primary_keys"][self._linkage_profiles[linkage]["target"]][0]][0])
            } for target in target_filters]
            self.post_batch("PDM_MANUAL_LINKAGE", linkage_entries)
        elif self._linkage_profiles[linkage]["linkage_type"] == "foreign_key":
            reference_id = self.get(self._linkage_profiles[linkage]["source"], source_filters)[
                self._linkage_profiles[linkage]["source_key"][1]]
            target_column = f"{self._linkage_profiles[linkage]['source']}_{self._linkage_profiles[linkage]['source_key'][1]}"
            for target in target_filters:
                self.patch(self._linkage_profiles[linkage]["target"], target, {
                           target_column: reference_id})
