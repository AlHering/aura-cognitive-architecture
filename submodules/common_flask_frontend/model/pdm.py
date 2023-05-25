# -*- coding: utf-8 -*-
"""
****************************************************
*                CommonFlaskFrontend                 
*            (c) 2022 Alexander Hering             *
****************************************************
"""
from common_flask_frontend.configuration import configuration as cfg
from common_flask_frontend.utility import json_utility, physical_data_model
from flask_login import UserMixin

PDM_DATA = json_utility.load(f"{cfg.PATHS.DATA_PATH}/pdm.json")
PDM = physical_data_model.PhysicalDataModel(
    environment_profile=PDM_DATA["environment"],
    entity_profiles=PDM_DATA["entity"],
    linkage_profiles=PDM_DATA["linkage"]
)


class User(UserMixin):
    """
    User class.
    """
    def __init__(self, data: dict, fetch: bool = False) -> None:
        """
        Initiation method for user class.
        :param data: User data.
        :param fetch: Fetch flag, declaring whether user data should be fetched from PDM.
        """
        if fetched:
            self.data = data
        else:
            self.data = PDM.get_deep_data("user", data)
        self.authentication = self.data.get("authenticated")[0][] if self.data.get("authenticated") else None

    def is_authenticated(self) -> bool:
        """
        Getter method for 'authenticated' flag.
        :return: Boolean, showing status of 'authenticated' flag.
        """
        return self.data.get("authenticated")

    def is_active(self) -> bool:
        """
        Getter method for 'active' flag.
        :return: Boolean, showing status of 'active' flag.
        """
        return self.inactive == ""

    def is_anonymous(self) -> bool:
        """
        Getter method for 'anonymous' flag.
        :return: Boolean, showing status of 'anonymous' flag.
        """
        return self.anonymous == "X"

    def get_id(self) -> int:
        """
        Getter method for user ID.
        :return: User ID.
        """
        return self.id