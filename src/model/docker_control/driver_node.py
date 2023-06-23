# -*- coding: utf-8 -*-
"""
****************************************************
*           aura-cognitive-architecture
*            (c) 2023 Alexander Hering             *
****************************************************
"""
from typing import Any
from src.utility.gold.entity_data_interface import EntityDataInterface
from .worker_node import WorkerNode


class DriverNode(object):
    """
    Class representing a container-based driver node.
    """

    def __init__(self, db_interface: EntityDataInterface, blueprints: list) -> None:
        """
        Initiation method.
        :param db_interface: Database interface.
        :param blueprints: Blueprints for worker nodes.
        """
        self._db = db_interface
        self.blueprints = blueprints

    def add_blueprint(self, blueprint: Any) -> None:
        """
        Method for adding worker ndoe.
        :param blueprint: Blueprint to add.
        """
        self.blueprints.append(blueprint)
