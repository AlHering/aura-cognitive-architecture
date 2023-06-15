# -*- coding: utf-8 -*-
"""
****************************************************
*           aura-cognitive-architecture            *
*            (c) 2023 Alexander Hering             *
****************************************************
"""
from src.utility.bronze import json_utility, docker_utility


class DockerController(object):
    """
    Controller for managing Docker-based environments.
    """

    def __init__(self, cache: dict = None) -> None:
        """
        Initiation method.
        :param cache: Cache to initialize controller with.
            Defaults to None in which case an empty cache is created.
        """
        self._cache = cache if cache is not None else {}

    def import_cache(self, import_path: str) -> None:
        """
        Method for importing cache data.
        :param import_path: Import path.
        """
        self._logger.log(f"Importing cache from '{import_path}'...")
        self._cache = json_utility.load(import_path)

    def export_cache(self, export_path: str) -> None:
        """
        Method for exporting cache data.
        :param export_path: Export path.
        """
        self._logger.log(f"Exporting cache to '{export_path}'...")
        json_utility.save(self._cache, export_path)
