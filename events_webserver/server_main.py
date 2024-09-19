
import flask, flask_session
import threading
import app_config

from helpers import apps

from blueprints.login_bp import login_bp

app = flask.Flask(__name__)
app.config.from_object(app_config)
app.config["SESSION_MONGODB"] = apps.get_mongo_connection()
app.config["SESSION_MONGODB_DB"] = app_config.SESSION_MONGODB_FLASK_DB

flask_session.Session(app)