# -*- coding: utf-8 -*-
"""
****************************************************
*                     Utility                      *
*            (c) 2022 Alexander Hering             *
****************************************************
"""
import datetime
import json
from contextlib import contextmanager
from typing import List, Union, Any, Optional
import pickle

from sqlalchemy import Column, String, Boolean, Integer, JSON, Text, DateTime, CHAR, ForeignKey, Table, Float, BLOB, TEXT
from sqlalchemy.orm import Session, relationship
from sqlalchemy import and_, or_, not_
from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy import orm, inspect
from sqlalchemy.engine import create_engine, Engine
from sqlalchemy.sql import text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import ProgrammingError, OperationalError

DECLARATIVE_BASE = declarative_base

PROGRAMMING_ERROR = ProgrammingError
OPERATIONAL_ERROR = OperationalError

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
    "not_in": lambda x, y: not_(x.in_(y)),
    "and": lambda *x: and_(*x),
    "or": lambda *x: or_(*x),
    "not": lambda x: not_(x),
    "&&": lambda *x: and_(*x),
    "||": lambda *x: or_(*x),
    "!": lambda x: not_(x)
}

# Conversion dictionary for SQL typing
SQL_TYPING_DICTIONARY = {
    int: "int",
    str: "varchar(255)",
    float: "float",
    dict: "json",
    list: "json",
    bool: "BOOLEAN",
    chr: "CHAR",
}

# Conversion dictionary for SQLAlchemy typing
ALCHEMY_TYPING_DICTIONARY = {
    "int": Integer,
    "dict": JSON,
    "datetime": DateTime,
    "str": String(60),
    "str_": String,
    "text": Text,
    "bool": Boolean,
    "char": CHAR,
    "longtext": Text,
    "float_": Float,
    "float": Float,
    "blob": BLOB
}

# Conversion dictionary for Python typing
PYTHON_TYPING_DICTIONARY = {
    "int": int,
    "dict": dict,
    "datetime": datetime.datetime,
    "str": str,
    "text": str,
    "bool": bool,
    "char": chr,
    "longtext": str,
    "float": float,
    "blob": bytes
}


def encode_dictionary(data: dict) -> dict:
    """
    Refactors dictionary to ensure relational database compatibility.
    :param data: Dictionary to refactor.
    :return: Encoded dictionary.
    """
    for key in list(data.keys()):
        if isinstance(data[key], dict):
            data[key] = json.dumps({"#META_dict": data[key]})
        if isinstance(data[key], list):
            data[key] = json.dumps({"#META_list": data[key]})
    return encode_dictionary_keys(data)


def encode_dictionary_keys(data: dict) -> dict:
    """
    Function for encoding key names in dictionary.
    :param data: Dictionary to encode.
    :return: Encoded dictionary.
    """
    for key in list(data.keys()):
        if "#" in key:
            data[key.replace("#", "HASHTAG_")] = data.pop(key)
    return data


def decode_dictionary(data: dict) -> dict:
    """
    Refactors dictionary to ensure relational database compatibility.
    :param data: Dictionary to refactor.
    :return: Decoded dictionary.
    """
    for key in list(data.keys()):
        if isinstance(data[key], str) and data[key].startswith('{"#META_dict": {'):
            data[key] = json.loads(data[key])["#META_dict"]
        elif isinstance(data[key], str) and data[key].startswith('{"#META_list": {'):
            data[key] = json.loads(data[key])["#META_list"]
        if "HASHTAG_" in key:
            data[key.replace("HASHTAG_", "#")] = data.pop(key)
    return data


def get_engine(engine_url: str, pool_recycle: int = 280, encoding: str = "utf-8") -> Engine:
    """
    Function for getting database engine.
    :param engine_url: URL to create engine for.
    :param pool_recycle: Parameter for preventing the reuse of connections that were stale for some time.
    :param encoding: Encoding string. Defaults to 'utf-8'.
    :return: Engine to given database.
    """
    try:
        #SQLAlchemy 1.4
        return create_engine(engine_url, encoding=encoding, pool_recycle=pool_recycle)
    except TypeError:
        #SQLAlchemy 2.0
        return create_engine(engine_url, pool_recycle=pool_recycle)


def execute_engine_command(engine: Engine, command: str) -> Optional[Any]:
    """
    Function for executing commands via database engine.
    :param engine: Database engine.
    :param command: Command to execute.
    :return: Return value of command, if existing.
    """
    return engine.execute(text(command))


def get_session_factory(engine: Engine) -> Any:
    """
    Function for getting database session factory.
    :param engine: Engine to bind session factory to.
    :return: Engine to given database.
    """
    return orm.scoped_session(
        orm.sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine,
        ),
    )


@contextmanager
def get_session_from_factory(factory: Any) -> Any:
    """
    Function for getting database session from session factory.
    :param factory: Session factory.
    :return: Database session.
    """
    session: orm.Session = factory()
    try:
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def write_dictionary_to_db(engine: Engine, source_table: str, data: dict, primary_key: str = None) -> None:
    """
    Function for writing dictionary data to sql database.
    :param engine: Database engine.
    :param source_table: Source table to write data into.
    :param data: Data to write to database.
    :param primary_key: Primary key field. Defaults to None in which case auto-incrementing integer field 'id' is used.
    """
    if not primary_key:
        primary_key = "id"
    data = encode_dictionary(data)
    fields = list(data.keys())
    with engine.connect() as con:
        statement = text("INSERT INTO "
                         + source_table
                         + "("
                         + ", ".join(fields)
                         + ") VALUES("
                         + ", ".join([":" + field for field in fields])
                         + ")"
                         + " ON DUPLICATE KEY UPDATE "
                         + ", ".join([field + "= :" + field for field in fields if field != primary_key])
                         + ";")

        con.execute(statement, **data)


def read_dictionaries_from_db(engine: Engine, source_table: str, target_fields: List[str] = None,
                            filter_masks: Union[List[list], str] = []) -> List[dict]:
    """
    Function for reading dictionary data from sql database.
    :param engine: Database engine.
    :param source_table: Source table to read data from.
    :param target_fields: List of fields to fetch. Defaults to None, in which case all fields are fetched
    :param filter_masks: List of filter masks translating to WHERE statements in SQL or WHERE statement as string.
            Defaults to empty list.
        Filter mask syntax:
            [field: str, value: Any] => Checking field against value
            [field: str, comparison_type: str, value: Any] => Checking field against value by comparison type.
        Comparison types:
            "equals": lambda x, y: x == y,
            "not_equals": lambda x, y: x != y,
            "contains": lambda x, y: y in x,
            "not_contains": lambda x, y: y not in x,
            "is_contained": lambda x, y: x in y,
            "not_is_contained": lambda x, y: x not in y
    :return: List of dictionaries containing query results.
    """
    if not target_fields:
        target_fields = "*"
    else:
        target_fields = ",".join(target_fields)
    if isinstance(filter_masks, list):
        where_statements = translate_filter_masks(filter_masks)
    else:
        where_statements = filter_masks

    result = engine.execute(text("SELECT "
                                 + target_fields
                                 + " FROM "
                                 + source_table
                                 + where_statements
                                 + ";"))
    result = [decode_dictionary(dict(row)) for row in result]
    return result


def translate_filter_masks(masks: List[list]) -> str:
    """
    Function for translating filter masks to WHERE statement as string.
    :param masks: Filter masks.
        Filter mask syntax:
            [field: str, value: Any] => Checking field against value
            [field: str, comparison_type: str, value: Any] => Checking field against value by comparison type.
        Comparison types:
            "equals": lambda x, y: x == y,
            "not_equals": lambda x, y: x != y,
            "contains": lambda x, y: y in x,
            "not_contains": lambda x, y: y not in x,
            "is_contained": lambda x, y: x in y,
            "not_is_contained": lambda x, y: x not in y
    :return: SQL WHERE-Statement in form of a string.
    """
    where_statement = " "
    for mask in masks:
        if len(mask) == 2:
            where_statement += " AND " + mask[0] + " = " + mask[1]
        elif len(mask) == 3:
            sub_statement = ""
            if "not" in mask[1]:
                sub_statement += "NOT"
            if "equals" in mask[1]:
                sub_statement += mask[0] + " = " + mask[2]
            elif "contains" in mask[1]:
                sub_statement += mask[0] + " LIKE '%" + mask[2] + "%'"
            elif "is_contained" in mask[1]:
                container = ["'" + con + "'" for con in mask[2] if isinstance(con, str)]
                container.extend([str(con) for con in mask[2] if isinstance(con, int)])
                sub_statement += mask[0] + " IN (" + ", ".join(container) + ")"
            where_statement += " AND " + sub_statement
    if where_statement.startswith("  AND"):
        where_statement = " WHERE" + where_statement[5:]
    return where_statement


def get_table_creation_statement(data: dict, source_table: str, primary_key: str = None,
                                 foreign_key: bool = False) -> str:
    """
    Function for getting table creation statement.
    :param data: Dictionary to create table for.
    :param source_table: Source table to potentially create and build tables for nested dictionaries from.
    :param primary_key: Primary key field. Defaults to None in which case auto-incrementing integer field 'id' is used.
    :param foreign_key: Boolean declaring, whether to create field for foreign key. Defaults to False.
    """
    encoded_keys = encode_dictionary_keys(data)
    statement = " CREATE TABLE IF NOT EXISTS " + source_table + " ("
    if primary_key:
        statement += primary_key + " " + SQL_TYPING_DICTIONARY[type(encoded_keys[primary_key])] + " NOT NULL, "
    else:
        statement += "id int NOT NULL AUTO_INCREMENT, "
    if foreign_key:
        statement += "ancestor varchar(255) NOT NULL, "
    statement += ", ".join([key + " " + SQL_TYPING_DICTIONARY[type(encoded_keys[key])] for key in encoded_keys if (not primary_key or key != primary_key)])
    if primary_key:
        statement += ", PRIMARY KEY (" + primary_key + ")"
    else:
        statement += ", PRIMARY KEY (id)"
    statement += ");"
    return statement


def create_tables_for_dictionary(engine: Engine, source_table: str, data: dict) -> None:
    """
    Function for creating tables for dictionary structure.
    :param engine: Database engine.
    :param source_table: Source table to potentially create and build tables for nested dictionaries from.
    :param data: Dictionary to create tables for.
    """
    creation_statement = get_table_creation_statement(data, source_table, "id")
    engine.execute(creation_statement)


def create_mapping_for_dictionary(mapping_base: Any, entity_type: str, column_data: dict, linkage_data: dict = None, typing_translation: dict = ALCHEMY_TYPING_DICTIONARY) -> Any:
    """
    Function for creating database mapping from dictionary.
    :param mapping_base: Mapping base class.
    :param entity_type: Entity type to create mapping for.
    :param column_data: Column data dictionary.
    :param linkage_data: Linkage data dictionary. Defaults to None
    :param typing_translation: Typing translation dictionary. Defaults to default sqlalchemy-translation.
    :return: Mapping class.
    """
    class_data = {"__tablename__": entity_type}
    desc = column_data.get("#meta", {}).get("description", False)
    if desc:
        class_data["__table_args__"] = {"comment": desc}

    class_data.update(
        {
                param: Column(typing_translation[column_data[param]["type"]], **column_data[param].get("schema_args", {})) if "_" not in column_data[param]["type"]
                else Column(typing_translation[column_data[param]["type"].split("_")[0] + "_"](*[int(arg) for arg in column_data[param]["type"].split("_")[1:]]), **column_data[param].get("schema_args", {}))
                for param in column_data if param != "#meta"
        }
    )
    if linkage_data is not None:
        for profile in [profile for profile in linkage_data if
                        linkage_data[profile]["linkage_type"] == "foreign_key" and linkage_data[profile][
                            "source"] == entity_type]:
            target_class = linkage_data[profile]["target"][0].upper() + linkage_data[profile]["target"][1:]
            if linkage_data[profile]["relation"] == "1:1":
                class_data.update({
                    profile: relationship(target_class, back_populates=profile, uselist=False)})
            elif linkage_data[profile]["relation"] == "1:n":
                class_data.update({profile: relationship(target_class, back_populates=profile)})
            elif linkage_data[profile]["relation"] == "n:m":
                class_data.update({profile: relationship(target_class, secondary=Table(
                    profile,
                    mapping_base.metadata,
                    Column(f"{entity_type}_{linkage_data[profile]['source_key'][1]}",
                           ForeignKey(f"{entity_type}.{linkage_data[profile]['source_key'][1]}")),
                    Column(f"{linkage_data[profile]['target']}_{linkage_data[profile]['target_key'][1]}",
                           ForeignKey(f"{entity_type}.{linkage_data[profile]['source_key'][1]}"))
                ))})
        for profile in [profile for profile in linkage_data if
                        linkage_data[profile]["linkage_type"] == "foreign_key" and linkage_data[profile][
                            "target"] == entity_type]:
            source_class = linkage_data[profile]["source"][0].upper() + linkage_data[profile]["source"][1:]
            source = linkage_data[profile]["source"]
            source_key = linkage_data[profile]["source_key"][1]
            if linkage_data[profile]["relation"].startswith("1:"):
                class_data.update({
                    f"{source}_{source_key}": Column(
                        typing_translation[linkage_data[profile]["source_key"][0]],
                        ForeignKey(f"{source}.{source_key}")
                    ),
                    profile: relationship(source_class, back_populates=profile)
                })
    return type(entity_type[0].upper()+entity_type[1:], (mapping_base,), class_data)


def migrate_database(old_db: str, new_db: str, model: Any, tables: List[str] = None) -> None:
    """
    Function for migrating database content.
    :param old_db: Database connection string for old database.
    :param old_db: Database connection string for new database.
    :param model: Model representation.
    :param tables: List of tables to migrate. Defaults to None in which case all tables are migrated
    """

    old_base = automap_base()
    old_engine = create_engine(old_db)
    old_base.prepare(old_engine, reflect=True)
    old_session = Session(old_engine)

    new_base = automap_base()
    new_engine = create_engine(new_db)
    new_base.prepare(new_engine, reflect=True)
    new_session = Session(new_engine)
    old_base.metadata.create_all(new_engine)

    for target in [table for table in old_base.metadata.tables if tables is None or table in tables]:
        old_base.metadata.tables[target]
        batch = [dict(entry) for entry in old_session.query(old_base.metadata.tables[target]).all()]
        new_session.bulk_insert_mappings(model[target]["dataclass"], batch)
        new_session.commit()

