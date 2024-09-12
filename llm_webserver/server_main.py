import flask, flask_session
import msal

from blueprints.login_test_bp import login_test_apis

import app_config

app = flask.Flask(__name__)
app.config.from_object(app_config)
flask_session.Session(app)

app.register_blueprint(login_test_apis)

if __name__ == "__main__":
    app.run()