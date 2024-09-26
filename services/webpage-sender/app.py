
from flask import redirect, url_for, render_template, request
import flask, flask_session
import app_config
import identity.web

from helpers import apps
app = flask.Flask(__name__)
app.config.from_object(app_config)
app.config["SESSION_MONGODB"] = apps.get_mongo_connection()
app.config["SESSION_MONGODB_DB"] = app_config.SESSION_MONGODB_FLASK_DB
flask_session.Session(app)

@app.route("/finishLogin", methods=["GET"])
def finish_login():
    if(apps.get_ms_app().get_user() != None):
        return redirect(url_for('index'))

    if(apps.get_ms_app()._AUTH_FLOW not in flask.session):
        return "Session is missing", 400 # TODO: redirect to error page

    login_result = apps.get_ms_app().complete_log_in(request.args)
    if("error" in login_result):
        return render_template("auth_error.html", login_result=login_result)

    return redirect(url_for('index'))

@app.route("/login", methods=["GET"])
def login():
    if(apps.get_ms_app().get_user() != None):
        return redirect(url_for('index'))

    return render_template(
        "login.html", **apps.get_ms_app().log_in(
            scopes=app_config.SCOPES,
            redirect_uri=app_config.MICROSOFT_LOGIN_REDIRECT
        )
    )

@app.route("/", methods=["GET"])
def home():
    if(apps.get_ms_app().get_user() == None):
        return redirect(url_for('login'))

    return render_template(
        "index.html"
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0")