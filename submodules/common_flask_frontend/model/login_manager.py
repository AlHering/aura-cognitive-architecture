# -*- coding: utf-8 -*-
"""
****************************************************
*                CommonFlaskFrontend                 
*            (c) 2022 Alexander Hering             *
****************************************************
"""
from typing import Optional
from flask_login import LoginManager, login_user, logout_user
from common_flask_frontend.model import database


login_manager = LoginManager()


@login_manager.user_loader
def user_loader(user_id: int) -> Optional[database.MODEL["user"]]:
    """
    User loader method.
    :param user_id: User ID.
    :return: User instance fitting ID.
    """
    return database.get_user_by_id(user_id)
