# -*- coding: utf-8 -*-
"""
****************************************************
*                CommonFlaskFrontend                 
*            (c) 2022 Alexander Hering             *
****************************************************
"""
import logging


def send_authentication_mail(target_address: str, authentication_uuid: str, auth_type: str = "registration") -> None:
    """
    Function for sending out autentication eMail.
    :param target_address: Target eMail address.
    :param authentication_uuid: Authentication UUID.
    :param auth_type: Type of Authentication. Defaults to 'registration'.
    """
    # TODO: Implement
    logging.info(f"target_address : {target_address}, authentication_uuid: {authentication_uuid}, auth_type: {auth_type}.")
    pass
