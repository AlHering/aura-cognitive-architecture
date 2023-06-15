# -*- coding: utf-8 -*-
"""
****************************************************
*           aura-cognitive-architecture            *
*            (c) 2023 Alexander Hering             *
****************************************************
"""


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
