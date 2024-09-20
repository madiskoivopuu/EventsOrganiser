
import flask, flask_session
import threading
import app_config

from helpers import apps

from blueprints.login_bp import login_apis
from blueprints.events_bp import events_apis

app = flask.Flask(__name__)
app.config.from_object(app_config)
app.config["SESSION_MONGODB"] = apps.get_mongo_connection()
app.config["SESSION_MONGODB_DB"] = app_config.SESSION_MONGODB_FLASK_DB

flask_session.Session(app)

app.register_blueprint(login_apis)
app.register_blueprint(events_apis)

if __name__ == "__main__":
    app.run(host="0.0.0.0")