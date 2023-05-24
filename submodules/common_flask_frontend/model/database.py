# -*- coding: utf-8 -*-
"""
****************************************************
*                FinanceProtocol                 
*            (c) 2022 Alexander Hering             *
****************************************************
"""
import os
import uuid
from typing import Any, Optional
import re
from ..static_utility import json_utility, sql_utility
from . import data_model
from sqlalchemy import update


EMAIL_VALIDATION_PATTERN = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
BASE = data_model.Base
MODEL = {
    "user": data_model.User,
    "role": data_model.Role,
    "asset": data_model.Asset,
    "authentication": data_model.Authentication
}
ENGINE = sql_utility.get_engine(os.getenv("CFF_DB_URI"))
BASE.metadata.create_all(ENGINE)
SESSION_FACTORY = sql_utility.get_session_factory(ENGINE)


def get_user_by_id(user_id: int) -> data_model.User:
    """
    Method for getting user by ID.
    :param user_id: User ID.
    :return: User for given ID.
    """
    return SESSION_FACTORY().query(MODEL["user"]).filter_by(
        MODEL["user"].id == user_id
    ).first()


def get_authentication_by_uuid(uuid: str, auth_type: str = "registration") -> Optional[data_model.Authentication]:
    """
    Method for getting authentication by UUID.
    :param uuid: Authentication UUID.
    :param auth_type: Authentication type. Defaults to
    :return: Authentication for given UUID.
    """
    return SESSION_FACTORY().query(MODEL["authentication"]).filter_by(
        MODEL["authentication"].uuid == uuid,
        MODEL["authentication"].type == auth_type
    ).first()


def verify_authentication(uuid: str) -> Optional[data_model.Authentication]:
    """
    Method for getting authentication by UUID.
    :param uuid: Authentication UUID.
    :return: Authentication for given UUID.
    """
    with SESSION_FACTORY() as session:
        auth = session.query(MODEL["authentication"]).filter_by(
            MODEL["authentication"].uuid == uuid
        ).first()
        if auth and auth.status is False:
            auth.stats = True
            session.commit()
            session.refresh(auth)
        return auth


def overwrite_authentication(email: str) -> Optional[data_model.Authentication]:
    """
    Method for getting authentication by UUID.
    :param email: Account Email.
    """
    with SESSION_FACTORY() as session:
        user = session.query(MODEL["user"]).filter_by(
            MODEL["user"].email == email
        ).first()
        if user:
            auth = [auth for auth in user.authentication if auth.type == "registration"]
            if not auth:
                auth = data_model.Authentication(
                        uuid=str(uuid.uuid4().hex),
                        user_id=user.id
                    )
                session.add(auth)
                session.commit()
            else:
                auth = auth[0]
            return auth


def create_new_reset_auth(user_email: str, auth_type: str = "password_reset") -> Optional[data_model.Authentication]:
    """
    Method for creating reset authentication.
    :param user_email: User email.
    :param auth_type: Authentication type. Defaults to
    :return: Authentication.
    """
    with SESSION_FACTORY() as session:
        user = session.query(MODEL["user"]).filter_by(
            MODEL["user"].email == user_email
        ).first()
        if user:
            for auth in user.authentication:
                if auth.type == auth_type and not auth.status:
                    session.delete(auth)
            session.commit()

            auth = MODEL["authentication"](
                uuid=str(uuid.uuid4().hex),
                type=auth_type,
                user_id=user.id
            )
            session.add(auth)
            session.commit()
            session.refresh(auth)
            return auth


def delete_authentication(uuid: str) -> None:
    """
    Method for deleting authentication by UUID.
    :param uuid: Authentication UUID.
    :return: Authentication for given UUID.
    """
    with SESSION_FACTORY() as session:
        auth = session.query(MODEL["authentication"]).filter_by(
            MODEL["authentication"].uuid == uuid
        ).first()
        if auth:
            session.delete(auth)
            session.commit()


def get_user_by_login(username_or_email: str, password_hash: str) -> data_model.User:
    """
    Method for getting user by ID.
    :param username_or_email: User's name or Email.
    :param password_hash: User's password hash.
    :return: User for given data.
    """
    if re.fullmatch(EMAIL_VALIDATION_PATTERN, username_or_email):
        target_attribute = "email"
        username_or_email = username_or_email.lower()
    else:
        target_attribute = "username"
    return SESSION_FACTORY().query(MODEL["user"]).filter(
        sql_utility.and_(
            getattr(MODEL["user"], target_attribute) == username_or_email,
            MODEL["user"].password == password_hash
        )
    ).first()


def post_entity(entity_type: str, entity_data: dict) -> Any:
    """
    Method for posting user to data backend.
    :param entity_type: Entity type.
    :param entity_data: Entity data as dictionary.
    """
    with SESSION_FACTORY() as session:
        result = MODEL[entity_type](**entity_data)
        session.add(result)
        session.commit()
        session.refresh(result)
    return result


def update_user_by_id(user_id: int, update_data: dict) -> data_model.User:
    """
    Method for getting user by ID.
    :param user_id: User ID.
    :param update_data: Update data.
    :return: User for given ID.
    """
    with SESSION_FACTORY() as session:
        user = session.query(MODEL["user"]).filter_by(
            MODEL["user"].id == user_id
        ).first()
        for arg in update_data:
            setattr(user, arg, update_data[arg])
        session.commit()
        session.refresh(user)
    return user
