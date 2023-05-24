# -*- coding: utf-8 -*-
"""
****************************************************
*                CommonFlaskFrontend                 
*            (c) 2022 Alexander Hering             *
****************************************************
"""
import uuid

from sqlalchemy import Table, Column, String, Boolean, Integer, JSON, Text, DateTime, CHAR, ForeignKey, Table, Float, BLOB, TEXT, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
Base = declarative_base()
from flask_login import UserMixin


holds_table = Table(
    "holds",
    Base.metadata,
    Column("user_id", ForeignKey("user.id"), primary_key=True, comment="ID of the user."),
    Column("role_id", ForeignKey("role.id"), primary_key=True, comment="ID of the role."),
)


accessible_by_table = Table(
    "accessible_by",
    Base.metadata,
    Column("user_id", ForeignKey("user.id"), primary_key=True, comment="ID of the user."),
    Column("asset_id", ForeignKey("asset.id"), primary_key=True, comment="ID of the asset."),
)


uuid_creator = lambda _: str(uuid.uuid4())


class User(Base, UserMixin):
    """
    User class.
    """
    __tablename__ = "user"
    __table_args__ = {"comment": "User Table."}

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True, nullable=False, comment="ID of the object.")
    username = Column(Text, nullable=False, unique=True, comment="Username of user.")
    email = Column(Text, nullable=False, unique=True, comment="Email address of user.")
    displayname = Column(Text, nullable=False, comment="Display name of user.")
    password = Column(Text, nullable=False, comment="Password hash of user.")
    anonymous = Column(CHAR, default="", comment="Flag for marking anonymous users.")

    created = Column(DateTime, default=func.now(), comment="Timestamp of creation.")
    updated = Column(DateTime, onupdate=func.now(), comment="Timestamp of last update.")
    inactive = Column(CHAR, default="", comment="Flag for marking inactive entries.")

    roles = relationship("Role", secondary=holds_table, back_populates="users")
    assets = relationship("Asset", back_populates="owner")
    accessibles = relationship("Asset", secondary=accessible_by_table)
    authentication = relationship("Authentication", back_populates="user")

    def is_authenticated(self) -> bool:
        """
        Getter method for 'authenticated' flag.
        :return: Boolean, showing status of 'authenticated' flag.
        """
        return self.authentication.status

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


class Role(Base):
    """
    Role class.
    """
    __tablename__ = "role"
    __table_args__ = {"comment": "Role Table."}

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True, nullable=False, comment="ID of the role.")
    title = Column(Text, nullable=False, comment="Title of the role.")
    access = Column(Integer, nullable=False, default=0, comment="Access rights.")

    created = Column(DateTime, default=func.now(), comment="Timestamp of creation.")
    updated = Column(DateTime, onupdate=func.now(), comment="Timestamp of last update.")
    inactive = Column(CHAR, default="", comment="Flag for marking inactive entries.")

    users = relationship("User", secondary=holds_table, back_populates="roles")


class Asset(Base):
    """
    Asset class.
    """
    __tablename__ = "asset"
    __table_args__ = {"comment": "Asset Table."}

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True, nullable=False, comment="ID of the asset.")
    type = Column(Text, nullable=False, comment="Type of asset.")
    content = Column(Text, nullable=False, comment="Content of the asset.")
    path = Column(Text, nullable=False, comment="Path to asset data.")

    created = Column(DateTime, default=func.now(), comment="Timestamp of creation.")
    updated = Column(DateTime, onupdate=func.now(), comment="Timestamp of last update.")
    inactive = Column(CHAR, default="", comment="Flag for marking inactive entries.")

    owner_id = Column(Integer, ForeignKey("user.id"))
    owner = relationship("User", back_populates="assets")
    accessors = relationship("User", secondary=accessible_by_table, back_populates="accessibles")


class Authentication(Base):
    """
    Asset class.
    """
    __tablename__ = "authentication"
    __table_args__ = {"comment": "Authentication Table."}

    uuid = Column(Text, primary_key=True, unique=True, nullable=False, comment="UUID of the authentication.")
    type = Column(String, nullable=False, default="registration", comment="Type of the authentication.")
    status = Column(Boolean, default=False, comment="Boolean, declaring authentication status of user.")

    created = Column(DateTime, default=func.now(), comment="Timestamp of creation.")
    updated = Column(DateTime, onupdate=func.now(), comment="Timestamp of last update.")

    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User", back_populates="authentication")
