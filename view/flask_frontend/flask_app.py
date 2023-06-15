# -*- coding: utf-8 -*-
"""
****************************************************
*           aura-cognitive-architecture            *
*            (c) 2023 Alexander Hering             *
****************************************************
"""

import os
import flask
from typing import List
from multiprocessing import Process
from flask import Flask, render_template, request, url_for, redirect, flash
from submodules.common_plugin_controller.static_utility import flask_transformation_utility
from flask import session
from flask.logging import default_handler
import hashlib
import traceback
from flask import Blueprint
from flask_sqlalchemy import SQLAlchemy
from configuration import configuration as cfg
from submodules.common_flask_frontend.model import exceptions
from ...model import database
from ...model import BlueprintPlugin
from ...model import login_manager, user_loader, login_user, logout_user
from ...control import email_control
from common_plugin_controller.control.common_plugin_controller import PluginController
from datetime import datetime
import uuid
import logging
logging.basicConfig(level=logging.DEBUG)


class CommonFlaskApplicationController(object):
    """
    Controller for managing common flask-based applications.
    """

    def __init__(self, app_config: dict, support_login: bool = False) -> None:
        """
        Initiation method for Application Controller objects.
        :param app_config: Application config.
        :param support_login: Flag, geclaring whether to support login functionality.
            Defaults to False.
        """
        self._logger = logging.Logger(
            f"[CFAController][{app_config['page_title']}]")
        self._logger.addHandler(default_handler)
        self._logger.info("Initiating ...")
        self.config = app_config
        if "plugins" not in self.config:
            self.config["plugins"] = {}
        if not self.check_config:
            raise exceptions.InvalidCFAConfigurationException(self.config)
        self.app = None
        self.support_login = support_login

        self.plugin_controller = PluginController(
            plugin_class_dictionary={"blueprints": BlueprintPlugin},
            plugin_folders=[cfg.PATHS.PLUGIN_PATH],
            supported_types=["blueprints"]
        )

        self._setup_app()
        self._setup_common_routs()
        if self.support_login:
            self._bind_login_manager()

        self._fix_config()

        self.process = Process(target=self._startup_app)

    def _fix_config(self) -> None:
        """
        Internal method for auto-fixing config after app and route creation and configuration.
        """
        for topic_index, topic in enumerate(self.config["menus"]):
            if "#meta" not in self.config["menus"][topic]:
                self.config["menus"][topic]["#meta"] = {
                    "icon": f"lock-icon.png",
                    "type": "lc"
                }
            if "current_topic" not in self.config:
                self.config["current_topic"] = list(
                    self.config["menus"].keys())[0]

    def _setup_app(self) -> None:
        """
        Internal method for setting up app.
        """
        self.app = Flask(__name__,
                         static_folder=f"{cfg.PATHS.PACKAGE_PATH}/common_static",
                         template_folder=f"{cfg.PATHS.PACKAGE_PATH}/common_templates")
        self.app.secret_key = os.environ.get("FLASK_SECRET")

    def _setup_common_routs(self) -> None:
        """
        Internal method for setting up common routs.
        """
        @self.app.route("/", methods=["GET"])
        @self.app.route("/index", methods=["GET", "POST"])
        def index():
            if request.method == "POST":
                data = request.form
                print(data)
            return render_template("index.html", **self.config)

        if self.support_login:
            self._setup_login_routs()

        for blueprint_plugin in self.plugin_controller.plugins.get("blueprints", []):
            self._logger.info(
                f"Importing Blueprints from '{blueprint_plugin}' ...")
            if blueprint_plugin not in self.config["plugins"]:
                self.config["plugins"][blueprint_plugin] = {}
            self.integrate_extension(self.plugin_controller.plugins["blueprints"][blueprint_plugin].get_blueprints(global_config=self.config),
                                     self.plugin_controller.plugins["blueprints"][blueprint_plugin].get_menu())

    def _setup_login_routs(self) -> None:
        """
        Internal method for setting up login routs.
        """
        @self.app.route("/login", methods=["GET", "POST"])
        def login():
            if request.method == "POST":
                data = request.form
                user = database.get_user_by_login(data["login_email_username"],
                                                  hashlib.sha256(data["login_password"].encode('utf-8')).hexdigest())
                valid_login = user and login_user(user)
                if data["login_referrer"] not in self.config["endpoints"].keys():
                    return flask.abort(400)
                elif valid_login and user.is_authenticated():
                    flash("Login was successful!", "info")
                    return redirect(f"/{data['login_referrer']}")
                elif valid_login:
                    flash("Account is not authenticated yet!", "warning")
                    return redirect(f"/authenticate/{user.authentication.uuid}")
                else:
                    flash("Login was not successful!", "warning")
                    return render_template("login.html", **self.config, referrer_endpoint=data["login_referrer"],
                                           failure=True)
            elif request.method == "GET":
                referrer_endpoint = None
                if request.referrer:
                    referrer_endpoint = request.referrer.replace(
                        request.host_url, "")
                if not referrer_endpoint or referrer_endpoint not in self.config["endpoints"].keys():
                    referrer_endpoint = "index"
                return render_template("login.html", **self.config, referrer_endpoint=referrer_endpoint)

        @self.app.route("/register", methods=["GET", "POST"])
        def register():
            if request.method == "POST":
                form_data = request.form
                try:
                    user = database.post_entity("user", {
                        "username": form_data["register_username"],
                        "email": form_data["register_email"].lower(),
                        "password": hashlib.sha256(form_data["register_password"].encode("utf-8")).hexdigest()
                    })
                    auth = database.post_entity("authentication", {
                        "uuid": str(uuid.uuid4().hex),
                        "user_id": user.id
                    })
                except Exception as ex:
                    self.app.logger.error("Exception on register_endpoint!")
                    self.app.logger.error(ex)
                    self.app.logger.error(traceback.format_exc())
                    flash("Signup was not successful!", "error")
                    return render_template("register.html", **self.config)
                email_control.send_authentication_mail(
                    form_data["register_email"].lower(), auth.uuid)
                flash(
                    "An eMail was send to you. Please authenticate via the sent link.", "info")
                return render_template("login.html", **self.config, referrer_endpoint="index")
            elif request.method == "GET":
                return render_template("register.html", **self.config)

        @self.app.route("/authenticate", methods=["GET", "POST"])
        @self.app.route("/authenticate/<authentication_uuid>", methods=["GET", "POST"])
        def authenticate(authentication_uuid: str):
            if request.method == "GET":
                # Show status if authentication_uuid is given, else show form to resend Email
                auth = database.get_authentication_by_uuid(authentication_uuid)
                return render_template("authenticate.html", **self.config, authentication_uuid=authentication_uuid,
                                       authentication_status=auth.status if auth else False)
            elif request.method == "POST":
                # Change authentication status, if authentication_uuid is given and authentication is not verified yet
                if authentication_uuid:
                    auth = database.get_authentication_by_uuid(
                        authentication_uuid)
                    if auth:
                        if not auth.status:
                            database.verify_authentication(auth.uuid)
                        flash("Authentication was confirmed.", "info")
                        return redirect(flask.url_for("login"), code=303)
                    else:
                        flash(
                            "Authentication request was not successful! Please issue a new request.", "warning")
                        # Redirect to authenticate endpoint with GET request.
                        return redirect(flask.url_for("authenticate"), code=303)
                elif request.form:
                    # Get user email, overwrite authentication (if existing) and resend email
                    form_data = request.form
                    curr_auth = database.overwrite_authentication(
                        form_data["register_email"].lower())
                    if not curr_auth.stats:
                        email_control.send_authentication_mail(
                            form_data["register_email"].lower(), curr_auth.uuid)
                        flash(
                            "An eMail was send to you. Please authenticate via the sent link.", "info")
                    else:
                        flash("Authentication was already confirmed.", "info")
                    return redirect(flask.url_for("login"), code=303)

        @self.app.route("/reset", methods=["GET", "POST"])
        @self.app.route("/reset/<authentication_uuid>", methods=["GET", "POST"])
        def reset(authentication_uuid: str):
            if request.method == "GET":
                # Show status if authentication_uuid is given, else show form to resend Email
                auth = database.get_authentication_by_uuid(authentication_uuid)
                return render_template("reset.html", **self.config, authentication_uuid=authentication_uuid,
                                       authentication_status=auth.status if auth else False)
            elif request.method == "POST":
                # Change authentication status, if authentication_uuid is given and authentication is not verified yet
                if authentication_uuid:
                    auth = database.get_authentication_by_uuid(
                        authentication_uuid, "password_reset")
                    if auth and not auth.status:
                        database.verify_authentication(auth.uuid)
                        temporary_password = hashlib.md5(
                            auth.user.email.encode("utf-8")).hexdigest()
                        database.update_user_by_id(auth.user_id,
                                                   {"password": temporary_password})
                        flash(
                            "Please log in with the temporary password and change it.", "info")
                        return render_template("reset.html", **self.config, authentication_uuid=authentication_uuid,
                                               authentication_status=temporary_password)
                    else:
                        flash(
                            "Authentication request was not successful! Please issue a new request.", "warning")
                        # Redirect to authenticate endpoint with GET request.
                        return redirect(flask.url_for("reset"), code=303)
                elif request.form:
                    # Get user email, overwrite authentication (if existing) and resend email
                    form_data = request.form
                    auth = database.create_new_reset_auth(
                        form_data["reset_email"].lower(), "password_reset")
                    if auth:
                        email_control.send_authentication_mail(
                            form_data["reset_email"].lower(), auth.uuid)
                        flash(
                            "An eMail was send to you. Please follow its instructions.", "info")
                    else:
                        flash(
                            "Request was not successful! Please issue a new request and re-check your inputs.", "warning")
                    return redirect(flask.url_for("login"), code=303)

    def _setup_testing_routs(self) -> None:
        """
        Internal method for setting up testing routs.
        """
        @self.app.route("/forms", methods=["GET"])
        def forms():
            return render_template("forms.html", **self.config)

        @self.app.route("/tables", methods=["GET"])
        def tables():
            return render_template("tables.html", **self.config)

        @self.app.route("/charts", methods=["GET"])
        def charts():
            return render_template("charts.html", **self.config)

    def integrate_extension(self, blueprints: List[Blueprint], menus: dict = {}) -> None:
        """
        Method for integrating extensions.
        :param blueprints: Flask Blueprints.
        :param menus: New menu entries.
            Defaults to empty dictionary in which case no menu entries are added.
        """
        for blueprint in blueprints:
            self._logger.info(f"Registering Blueprint '{blueprint}'")
            self.app.register_blueprint(blueprint)
        for topic in menus:
            if topic in self.config["menus"]:
                self.config["menus"][topic].update(menus[topic])
            else:
                self.config["menus"][topic] = menus[topic]

    def _bind_login_manager(self) -> None:
        """
        Internal method for binding login manager.
        """
        login_manager.init_app(self.app)

    def check_config(self) -> bool:
        """
        Method for checking configuration on validity.
        :return: True, if profile is valid, else False.
        """
        self._logger.info("Checking configuration ...")
        """
        Menu Subprofile
        """
        menu_profile = self.config["menus"]
        mem = []
        for topic in menu_profile:
            for key in [key for key in menu_profile[topic] if "dropdown" in menu_profile[topic][key]]:
                if menu_profile[topic][key]["href"] not in mem:
                    if menu_profile[topic][key]["href"][0] == "#":
                        mem.append(menu_profile[topic][key]["href"])
                    else:
                        self._logger.warning(
                            f"{menu_profile[topic][key]['href']} must start with '#'.")
                        return False
                else:
                    self._logger.warning(
                        f"{menu_profile[topic][key]['href']} is used as dropdown href multiple times in menu configuration.")
                    return False
        return True

    def _startup_app(self, port: int = 5001, debug: bool = False) -> None:
        """
        Internal method for running app.
        :param port: Port to run app on.
        :param debug: Debugging flag.
        """
        # WebUI(app=self.app, port=port, debug=debug).run()
        self.app.run(debug=debug, port=port)

    def run_app(self) -> None:
        """
        Method for running app.
        """
        self.process.start()
        self.process.join()

    def stop_app(self) -> None:
        """
        Method for stopping app (and setting up a new instance for the case it is needed).
        @Taken from https://stackoverflow.com/questions/23554644/how-do-i-terminate-a-flask-app-thats-running-as-a-service and adjusted.
        """
        self.process.terminate()
        self._setup_app()
        self._setup_common_routs()
        self._bind_login_manager()
