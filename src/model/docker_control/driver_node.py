# -*- coding: utf-8 -*-
"""
****************************************************
*           aura-cognitive-architecture
*            (c) 2023 Alexander Hering             *
****************************************************
"""
from typing import List
from src.utility.gold.entity_data_interface import EntityDataInterface
from .worker_node import WorkerNode


class DriverNode(object):
    """
    Class representing a container-based driver node.
    """

    def __init__(self, db_interface: EntityDataInterface, worker_nodes: List[WorkerNode]) -> None:
        """
        Initiation method.
        :param db_interface: Database interface.
        :param worker_nodes: List of worker nodes to initiate driver node with.
        """
        self._db = db_interface
        self.worker_nodes = worker_nodes

    def add_worker_node(self, worker_node: WorkerNode) -> None:
        """
        Method for adding worker ndoe.
        """
        self.worker_nodes.append(worker_node)
