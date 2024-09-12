import flask
import app_config
from flask import Blueprint
from helpers import apps

login_test_apis = Blueprint('login_test_apis', __name__)
@login_test_apis.route("/finishLogin", methods=["GET"])
def login():
    if("auth_flow" not in flask.session):
        return "session missing", 400

    flow = flask.session["auth_flow"]
    token = apps.ms_app.acquire_token_by_auth_code_flow(flow, auth_response=flask.request.args)
    return "login success", 200

@login_test_apis.route("/", methods=["GET"])
def home():
    flow = apps.ms_app.initiate_auth_code_flow(scopes=app_config.SCOPES)
    # no error checks
    flask.session["auth_flow"] = flow

    return f"Link: {flow['auth_uri']}", 200