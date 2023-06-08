# -*- coding: utf-8 -*-
"""
****************************************************
*                   Utility
*            (c) 2023 Alexander Hering             *
****************************************************
"""
# In-depth documentation can be found under utility/docs/entity_data_interfaces.md
import copy
from sqlalchemy import and_, or_, not_
from typing import Optional, Any, List, Union
from ..bronze import sqlalchemy_utility
from .filter_mask import FilterMask
from ..bronze.dictionary_utility import get_filter_depth
from ..bronze.comparison_utility import COMPARISON_METHOD_DICTIONARY as CMD
from .entity_data_interface import EntityDataInterface, handle_gateways

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
MANUAL_LINKAGE = {
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


class SQLAlchemyEntityInterface(EntityDataInterface):
    """
    Class, representing SQLAlchemy Entity Interface.
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
        self.engine = sqlalchemy_utility.get_engine(environment_profile["arguments"]["database"],
                                                    encoding=environment_profile["arguments"].get("encoding", "utf-8"))
        self.base = sqlalchemy_utility.get_automapped_base(self.engine)
        self.model = sqlalchemy_utility.get_classes_from_base(self.base)
        self.session_factory = None

    """
    Initiation methods
    """

    def initiate_infrastructure(self) -> None:
        """
        Method for initiating infrastructure.
        """
        # add profile for manual linking
        global MANUAL_LINKAGE
        self._entity_profiles["MANUAL_LINKAGE"] = MANUAL_LINKAGE

        # add dataclasses, based off of with schema args enriched profiles, to model
        for profile in [p for p in self._entity_profiles if p not in self.model]:
            self._create_dataclass(profile)

        # create infrastructure and define session factory
        self.base.metadata.create_all(self.engine)
        self.session_factory = sqlalchemy_utility.get_session_factory(
            self.engine)

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
                       "comment": self._entity_profiles[entity_type][key].get("description", ""),
            }} for key in
                self._entity_profiles[entity_type] if
                key != "#meta"})
        desc = self._entity_profiles[entity_type].get(
            "#meta", {}).get("description", False)
        schema = self._entity_profiles[entity_type].get(
            "#meta", {}).get("schema", False)

        mapping_profile["#meta"] = {}
        if desc:
            mapping_profile["#meta"]["comment"] = desc
        if schema:
            mapping_profile["#meta"]["schema"] = schema

        for key in mapping_profile:
            if "autoincrement" in mapping_profile[key]:
                mapping_profile[key]["schema_args"]["autoincrement"] = mapping_profile[key]["autoincrement"]
            if "unique" in mapping_profile[key]:
                mapping_profile[key]["schema_args"]["unique"] = mapping_profile[key]["unique"]
        self.model[entity_type] = sqlalchemy_utility.create_mapping_for_dictionary(self.base, entity_type, mapping_profile,
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
    @handle_gateways(batch_index=2, filter_index=3, data_index=None, object_index=None)
    def _get_obj(self, entity_type: str, batch: bool, filters: List[FilterMask], **kwargs: Optional[Any]) -> Optional[Any]:
        """
        Method for acquring entity as object.
        :param entity_type: Entity type.
        :param batch: Flag, declaring whether to handle operation as batch-operation.
        :param filters: A list of Filtermasks declaring constraints.
        :param kwargs: Arbitrary keyword arguments.
        :return: Target entity.
        """
        with self.session_factory() as session:
            result = session.query(self.model[entity_type]).filter(
                *self.convert_filters(entity_type, filters)
            ).first()
        return result

    # override
    def _get_dict(self, entity_type: str, batch: bool, filters: List[FilterMask],  **kwargs: Optional[Any]) -> Optional[dict]:
        """
        Method for acquring entity data.
        :param entity_type: Entity type.
        :param batch: Flag, declaring whether to handle operation as batch-operation.
        :param filters: A list of Filtermasks declaring constraints.
        :param kwargs: Arbitrary keyword arguments.
        :return: Target entity data.
        """
        res = [self.obj_to_dictionary(entity_type, obj) for obj in self._get_as_obj(
            entity_type, filters, **kwargs)]
        return res[0] if res else None

    # override
    def get(self, entity_type: str, batch: bool, filters: List[FilterMask], **kwargs: Optional[Any]) -> Optional[Any]:
        """
        Method for acquring entity.
        :param entity_type: Entity type.
        :param batch: Flag, declaring whether to handle operation as batch-operation.
        :param filters: A list of Filtermasks declaring constraints.
        :param batch: Flag, declaring whether to handle operation as batch-operation.
        :param kwargs: Arbitrary keyword arguments.
            'mode': Overwrite class flag for handling entities via modes "as_object", "as_dict".
        :return: Target entity if existing, else None.
        """
        if kwargs.get("mode", self.handle_as_objects):
            return self._get_as_obj(entity_type, filters, **kwargs)
        else:
            return self._get_as_dict(entity_type, filters, **kwargs)

    # override
    @handle_gateways(batch_index=2, filter_index=None, data_index=None, object_index=3)
    def _post_obj(self, entity_type: str, batch: bool, entity: Any, **kwargs: Optional[Any]) -> Optional[Any]:
        """
        Method for adding a new entity.
        :param batch: Flag, declaring whether to handle operation as batch-operation.
        :param entity_type: Entity type.
        :param entity: Entity object.
        :param kwargs: Arbitrary keyword arguments.
        :return: Target entity data if existing, else None.
        """
        with self.session_factory() as session:
            session.add(entity)
            session.commit()
            session.refresh(entity)
        return entity

    # override
    def _post_dict(self, entity_type: str, batch: bool, entity_data: dict, **kwargs: Optional[Any]) -> Optional[dict]:
        """
        Method for adding a new entity data as dictionary.
        :param entity_type: Entity type.
        :param batch: Flag, declaring whether to handle operation as batch-operation.
        :param entity_data: Dictionary containing entity data.
        :param kwargs: Arbitrary keyword arguments.
        :return: Target entity data if existing, else None.
        """
        entity = self.model[entity_type](**entity_data)
        return self.obj_to_dictionary(self._post_obj(entity_type, entity, **kwargs))

    # override
    def post(self, entity_type: str, batch: str, entity: Any, **kwargs: Optional[Any]) -> Optional[Any]:
        """
        Method for adding a new entity.
        :param entity_type: Entity type.
        :param batch: Flag, declaring whether to handle operation as batch-operation.
        :param entity: Entity or entity data, depending on mode.
        :param kwargs: Arbitrary keyword arguments.
            'mode': Overwrite class flag for handling entities via modes "as_object", "as_dict".
        :return: Target entity if existing, else None.
        """
        if kwargs.get("mode", self.handle_as_objects):
            return self._post_dict(entity_type, entity, **kwargs)
        else:
            return self._post_obj(entity_type, entity, **kwargs)

    # override
    @handle_gateways(batch_index=2, filter_index=None, data_index=4, object_index=3)
    def _patch_obj(self, entity_type: str, batch: bool, entity: Any, patch: Optional[dict] = None, **kwargs: Optional[Any]) -> Optional[Any]:
        """
        Method for patching an existing entity.
        :param entity_type: Entity type.
        :param batch: Flag, declaring whether to handle operation as batch-operation.
        :param entity: Entity object to patch.
        :param patch: Patch as dictionary, if entity is not already patched.
        :param kwargs: Arbitrary keyword arguments.
        :return: Target entity data if existing, else None.
        """
        pass

    # override
    @handle_gateways(batch_index=2, filter_index=3, data_index=4, object_index=None)
    def _patch_dict(self, entity_type: str, batch: bool, filters: List[FilterMask], patch: dict, **kwargs: Optional[Any]) -> Optional[dict]:
        """
        Method for patching an existing entity data.
        :param entity_type: Entity type.
        :param batch: Flag, declaring whether to handle operation as batch-operation.
        :param filters: A list of Filtermasks declaring constraints.
        :param patch: Patch as dictionary.
        :param kwargs: Arbitrary keyword arguments.
        :return: Target entity data if existing, else None.
        """
        pass

    # override
    def patch(self, *args: Optional[Any], batch: bool, **kwargs: Optional[Any]) -> Optional[Any]:
        """
        Method for patching an existing entity.
        :param args: Arbitrary arguments.
        :param batch: Flag, declaring whether to handle operation as batch-operation.
        :param kwargs: Arbitrary keyword arguments.
            'mode': Overwrite class flag for handling entities via modes "as_object", "as_dict".
        :return: Target entity if existing, else None.
        """
        pass

    # override
    @handle_gateways(batch_index=2, filter_index=None, data_index=None, object_index=3)
    def _delete_obj(self, entity_type: str, batch: bool, entity: Any, **kwargs: Optional[Any]) -> Optional[Any]:
        """
        Method for deleting an entity.
        :param entity_type: Entity type.
        :param batch: Flag, declaring whether to handle operation as batch-operation.
        :param entity: Entity to delete.
        :param kwargs: Arbitrary keyword arguments.
        :return: Target entity data if existing, else None.
        """
        pass

    # override
    @handle_gateways(batch_index=2, filter_index=3, data_index=None, object_index=None)
    def _delete_dict(self, entity_type: str, batch: bool, filters: List[FilterMask], **kwargs: Optional[Any]) -> Optional[Any]:
        """
        Method for deleting an entity.
        :param entity_type: Entity type.
        :param batch: Flag, declaring whether to handle operation as batch-operation.
        :param filters: A list of Filtermasks declaring constraints.
        :param kwargs: Arbitrary keyword arguments.
        :return: Target entity data if existing, else None.
        """
        pass

    # override
    def delete(self, *args: Optional[Any], batch: bool, **kwargs: Optional[Any]) -> Optional[Any]:
        """
        Method for deleting an entity.
        :param args: Arbitrary arguments.
        :param batch: Flag, declaring whether to handle operation as batch-operation.
        :param kwargs: Arbitrary keyword arguments.
            'mode': Overwrite class flag for handling entities via modes "as_object", "as_dict".
        :return: Target entity if existing, else None.
        """
        pass

    """
    Linkage methods
    """

    # override
    def get_linked_entities(self, linkage: str, *args: Optional[Any], **kwargs: Optional[Any]) -> List[Any]:
        """
        Method for getting linked entities.
        :param args: Arbitrary arguments.
        :param kwargs: Arbitrary keyword arguments.
        :return: Linked entities.
        """
        pass

    # override
    def link_entities(self, linkage: str, *args: Optional[Any], **kwargs: Optional[Any]) -> None:
        """
        Method for getting linked entities.
        :param args: Arbitrary arguments.
        :param kwargs: Arbitrary keyword arguments.
        :return: Linked entities.
        """
        pass
