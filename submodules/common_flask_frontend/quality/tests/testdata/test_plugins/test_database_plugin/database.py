# -*- coding: utf-8 -*-
"""
****************************************************
*                ScrapingService                 
*            (c) 2023 Alexander Hering             *
****************************************************
"""
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Boolean, Integer, JSON, Text, DateTime, CHAR, ForeignKey, func
import os
from typing import List, Any
import json

CURR_PATH = os.path.abspath(os.path.join(__file__, os.pardir))
INFO = json.load(open(f"{CURR_PATH}/info.json", "r", encoding='utf-8'))
BASE = declarative_base()
sqlite_path = os.path.abspath(os.path.join(__file__, INFO["data_path"], "test_database_plugin.db"))
URI = f"sqlite:///{sqlite_path}"


class TestTable(BASE):
    """
    Test table class for testing purposes.
    """
    __tablename__ = "test_database_plugin.test_table"
    __table_args__ = {"comment": "Table for testing purposes."}

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True, nullable=False,
                comment="ID of test object.")
    test_int = Column(Integer, nullable=False, comment="Integer of test object.")
    test_string = Column(String, nullable=False, comment="String of test object.")
    test_boolean = Column(Boolean, nullable=False, comment="Boolean of test object.")
    test_text = Column(Text, nullable=False, comment="Text of test object.")
    test_json = Column(JSON, nullable=False, comment="JSON of test object.")
    nullable_test_string = Column(String, nullable=True, comment="String of test object.")

    created = Column(DateTime, default=func.now(), comment="Timestamp of creation.")
    updated = Column(DateTime, onupdate=func.now(), comment="Timestamp of last update.")
    inactive = Column(CHAR, default="", comment="Flag for marking inactive entries.")


class ChildTestTable(BASE):
    """
    Child test table class for testing purposes.
    """
    __tablename__ = "test_database_plugin.child_test_table"
    __table_args__ = {"comment": "Child table for testing purposes."}

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True, nullable=False,
                comment="ID of test object.")
    test_int = Column(Integer, nullable=False, comment="Integer of test object.")
    test_string = Column(String, nullable=False, comment="String of test object.")

    test_foreign_key = Column(Integer, ForeignKey("test_database_plugin.test_table.id"),
                              comment="Foreign key of test object.")

    created = Column(DateTime, default=func.now(), comment="Timestamp of creation.")
    updated = Column(DateTime, onupdate=func.now(), comment="Timestamp of last update.")
    inactive = Column(CHAR, default="", comment="Flag for marking inactive entries.")


def get_classes() -> List[Any]:
    """
    Function for acquiring dataclasses.
    :return: Dataclasses.
    """
    return [TestTable, ChildTestTable]


def get_engine_uri() -> str:
    """
    Function for acquiring database engine URI.
    :return: Database engine URI.
    """
    return URI
