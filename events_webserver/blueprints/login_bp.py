import flask
import app_config
from flask import Blueprint, redirect, url_for, render_template, request
import identity
import identity.web

from helpers import apps

login_apis = Blueprint('login_apis', __name__)
@login_apis.route("/finishLogin", methods=["GET"])
def finish_login():
    if(apps.get_ms_app().get_user() != None):
        return redirect(url_for('events_apis.home'))

    if(apps.get_ms_app()._AUTH_FLOW not in flask.session):
        return "Session is missing", 400 # TODO: redirect to error page

    login_result = apps.get_ms_app().complete_log_in(request.args)
    if("error" in login_result):
        return render_template("auth_error.html", login_result=login_result)

    return redirect(url_for('events_apis.home'))

@login_apis.route("/login", methods=["GET"])
def login():
    if(apps.get_ms_app().get_user() != None):
        return redirect(url_for('events_apis.home'))

    return render_template(
        "login.html", **apps.get_ms_app().log_in(
            scopes=app_config.SCOPES,
            redirect_uri=app_config.MICROSOFT_LOGIN_REDIRECT
        )
    )