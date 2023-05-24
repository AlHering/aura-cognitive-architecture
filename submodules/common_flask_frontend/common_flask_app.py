# -*- coding: utf-8 -*-
"""
****************************************************
*                CommonFlaskFrontend                 
*            (c) 2022 Alexander Hering             *
****************************************************
"""
import flask
from flask import Flask, render_template, request, url_for, redirect, flash
from common_flask_frontend import flask_utility
from flask import session
import hashlib
import traceback
from flask_sqlalchemy import SQLAlchemy
from common_flask_frontend.configuration import configuration as cfg
from common_flask_frontend.model import database
from common_flask_frontend.model.login_manager import login_manager, user_loader, login_user, logout_user
from common_flask_frontend.control import email_control
from datetime import datetime
import uuid
import logging
logging.basicConfig(level=logging.INFO)


# Note that all file paths need to be given relative to the static folder.
global_config = {
    "page_title": "My Service Title",
    "page_icon_path": "img/favicon.ico"
}
endpoint_config = {
    "endpoints": {
        "index": "",
        "login": "",
        "register": "",
        "authenticate": "",
        "forms": "",
        "charts": "",
        "tables": ""
    }
}
user_config = {
    "current_user": {
        "user_avatar": "img/avatar-0.jpg",
        "user_name": "Nathan Andrews",
        "user_role": "Developer"
    }
}
user_config["current_user"][
    "user_acronym"] = f"{user_config['current_user']['user_role'][0]}:{''.join(name_part[0] for name_part in user_config['current_user']['user_name'].split(' '))}"
# Note that icons are xlink references
menu_config = {
    "menus": {
        "MAIN": {
            "Home": {
                "icon": "#real-estate-1",
                "type": "xl",
                "href": "index"
            },
            "Forms": {
                "icon": "bed",
                "type": "fa",
                "href": "forms"
            },
            "My Dropdown": {
                "icon": "#browser-window-1",
                "type": "xl",
                "href": "#drop",
                "dropdown": {
                    "Page1": {
                        "href": "#1"
                    },
                    "Page2": {
                        "href": "#2"
                    },
                    "Page3": {
                        "href": "#3"
                    }
                }
            },
            "Login page": {
                "icon": "bed",
                "type": "fa",
                "href": "login"
            },
            "Demo": {
                "icon": "bed",
                "type": "fa",
                "href": "#!",
                "flag": {
                    "type": "warning",
                    "text": "6 New"
                }
            }
        },
        "SECOND MENU": {
            "Demo1": {
                "icon": "",
                "type": "fa",
                "href": ""
            },
            "My Dropdown": {
                "icon": "bed",
                "type": "fa",
                "href": "#demodrop",
                "dropdown": {
                    "DemoPage1": {
                        "href": "#1",
                        "icon": "",
                        "type": "fa"
                    },
                    "DemoPage2": {
                        "href": "#2",
                        "icon": "",
                        "type": "fa"
                    }
                }
            }
        }}
}

for dictionary in [endpoint_config, user_config, menu_config]:
    global_config.update(dictionary)

app = Flask(__name__,
            static_folder=f"{cfg.PATHS.PACKAGE_PATH}/common_static",
            template_folder=f"{cfg.PATHS.PACKAGE_PATH}/common_templates")
logger = logging.getLogger(global_config["page_title"])


CACHE = {}


@app.route("/", methods=["GET"])
@app.route("/index", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        data = request.form
        print(data)
    return render_template("index.html", **global_config)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        data = request.form
        user = database.get_user_by_login(data["loginEmail"],
                                   hashlib.sha256(data["loginPassword"].encode('utf-8')).hexdigest())
        valid_login = user and login_user(user)
        if data["loginReferrer"] not in global_config["endpoints"].keys():
            return flask.abort(400)
        elif valid_login and user.is_authenticated():
            flash("Login was successful!", "info")
            return redirect(f"/{data['loginReferrer']}")
        elif valid_login:
            flash("Account is not authenticated yet!", "warning")
            return redirect(f"/authenticate/{user.status}")
        else:
            flash("Login was not successful!", "warning")
            return render_template("login.html", **global_config, referrer_endpoint=data["loginReferrer"], failure=True)
    elif request.method == "GET":
        referrer_endpoint = None
        if request.referrer:
            referrer_endpoint = request.referrer.replace(request.host_url, "")
        if not referrer_endpoint or referrer_endpoint not in global_config["endpoints"].keys():
            referrer_endpoint = "index"
        return render_template("login.html", **global_config, referrer_endpoint=referrer_endpoint)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        form_data = request.form
        try:
            user = database.post_entity("user", {
                "username": form_data["registerUsername"],
                "email": form_data["registerEmail"],
                "password": hashlib.sha256(form_data["registerPassword"].encode('utf-8')).hexdigest()
            })
        except Exception as ex:
            app.logger.error("Exception on register_endpoint!")
            app.logger.error(ex)
            app.logger.error(traceback.format_exc())
            flash("Signup was not successful!", "error")
            return render_template("register.html", **global_config)
        email_control.send_authentication_mail(form_data["registerEmail"])
        flash("An eMail was send to you. Please authenticate via the sent link.", "info")
        return render_template("login.html", **global_config, referrer_endpoint="index")
    elif request.method == "GET":
        return render_template("register.html", **global_config)


@app.route("/authenticate/<authentication_uuid>", methods=["GET", "POST"])
def authenticate(authentication_uuid: str):
    if request.method == "GET":
        data = request.form
        print(data)
    elif request.method == "POST":
        data = request.form
        print(data)


@app.route("/forms", methods=["GET"])
def forms():
    return render_template("forms.html", **global_config)


@app.route("/tables", methods=["GET"])
def tables():
    return render_template("tables.html", **global_config)


@app.route("/charts", methods=["GET"])
def charts():
    return render_template("charts.html", **global_config)


def check_profile(profile: dict) -> bool:
    """
    Function for checking profile on validity.
    :param profile: Profile to check
    :return: True, if profile is valid, else False.
    """
    """
    Menu Subprofile
    """
    menu_profile = profile["menus"]
    mem = []
    for key in [key for key in menu_profile if "dropdown" in menu_profile[key]]:
        if menu_profile[key]["href"] not in mem:
            if menu_profile[key]["href"][0] == "#":
                mem.append(menu_profile[key]["href"])
            else:
                logger.warning(f"{menu_profile[key]['href']} must start with '#'.")
                return False
        else:
            logger.warning(f"{menu_profile[key]['href']} is used as dropdown href multiple times in menu configuration.")
            return False
    return True


if __name__ == "__main__":
    if check_profile(global_config):
        app.secret_key = cfg.ENV["FLASK_SECRET"]
        login_manager.init_app(app)
        app.run(debug=True, port=5001)
