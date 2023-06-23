# -*- coding: utf-8 -*-
"""
****************************************************
*           aura-cognitive-architecture
*            (c) 2023 Alexander Hering             *
****************************************************
"""


class WorkerNode(object):
    """
    Class representing a container-based working node.
    """

    def __init__(self, setup_profile: dict = None, interface_profile: dict = None) -> None:
        """
        Initiation method.
        :param setup_profile: Setup profile as dictionary, containing
            'image': Base image as string
            'environment':  List of tuples of the form (<variable>, <value>)
            'arguments': List of tuples of the form (<variable>, <value>)
            'packages': List of packages to install on image level
            'directories': List of tuples of directories to import of the form (<source path>, <path inside container>)
            'runtime': Runtime type as string
            'runtime_version': Optional runtime version
            'runtime_packages': Runtime packages to install
            'run': List of lines to run sequentially
            'cmd': Command to be run when starting container as List of command elements
        :param interface_profile: Interface profile as dictionary, containing
            nested configuration dictionaries under the supported interface types.
        """
        self._setup_profile = setup_profile
        self._interface_profile = interface_profile

    def _validate_setup_profile() -> bool:
        """
        Internal method for validating setup profile.
        """
        pass

    def _validate_interface_profile() -> bool:
        """
        Internal method for validating interface profile.
        """
        pass

    def import_dockerfile(path: str) -> None:
        """
        Method for importing Dockerfile. 
        :path: Dockerfile path.
        """
        pass
