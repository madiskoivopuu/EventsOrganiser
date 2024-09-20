import flask
import app_config
from flask import Blueprint, redirect, url_for, render_template, request
import identity
import identity.web

from helpers import apps

events_apis = Blueprint('events_apis', __name__)
@events_apis.route("/", methods=["GET"])
def home():
    if(apps.get_ms_app().get_user() == None):
        return redirect(url_for('login_apis.login'))

    return render_template(
        "index.html", **apps.get_ms_app().log_in(
            scopes=app_config.SCOPES,
            redirect_uri=app_config.MICROSOFT_LOGIN_REDIRECT
        )
    )