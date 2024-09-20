import flask, flask_session
import threading
import app_config

from blueprints.login_test_bp import login_test_apis
import event_parser_thread

app = flask.Flask(__name__)
app.config.from_object(app_config)
flask_session.Session(app)

app.register_blueprint(login_test_apis)

if __name__ == "__main__":
    t = threading.Thread(target=event_parser_thread.parse_loop)
    t.start()

    app.run(host="0.0.0.0")