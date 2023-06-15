# -*- coding: utf-8 -*-
"""
****************************************************
*                     Utility                      *
*            (c) 2023 Alexander Hering             *
****************************************************
"""
from typing import Any, Optional, List
from docker import DockerClient, from_env
from docker.models.images import Image
from docker.models.containers import Container


def get_docker_client(**kwargs: Optional[Any]) -> DockerClient:
    """
    Function for acquiring docker client.
    :param kwargs: Arbitrary keyword arguments.
    :return: Docker client
    """
    return from_env(**kwargs)


def get_available_containers(client: DockerClient) -> List[Container]:
    """
    Function for getting available Docker Containers.
    :param client: Docker client.
    :return: List of available Docker Containers.
    """
    return client.containers.list()


def get_container(client: DockerClient, container_name: str) -> Optional[Container]:
    """
    Function for getting a specific Docker Container.
    :param client: Docker client.
    :param container_name: Name of Docker Container.
    :return: Docker Container.
    """
    return client.images.get(container_name)


def get_available_images(client: DockerClient) -> List[Image]:
    """
    Function for getting available Docker Images.
    :param client: Docker client.
    :return: List of available Docker Images.
    """
    return client.images.list()


def get_image(client: DockerClient, image_name: str) -> Optional[Image]:
    """
    Function for getting a specific Docker Image.
    :param client: Docker client.
    :param image_name: Name of Docker Image.
    :return: Docker Image.
    """
    return client.images.get(image_name)


def pull_image(client: DockerClient, image_name: str) -> Image:
    """
    Function for pulling Docker Image.
    :param client: Docker client.
    :param image_name: Name of Docker Image to pull.
    :return: Pulled Docker Image.
    """
    return client.images.pull(image_name)
