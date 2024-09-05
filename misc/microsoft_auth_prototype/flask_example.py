import msal
import os, dotenv, threading
import app_config
import flask, flask_session
import email_parser_thread

REDIRECT_PATH = "/finishLogin"

dotenv.load_dotenv(".env")
msal_app = msal.ConfidentialClientApplication(
    client_id="e7531514-8913-47a8-8cd2-b80dcef955b7",
    client_credential=os.getenv("MSAL_CLIENT_SECRET"), # should replace with a certificate? for ConfidentialClientApplication
    authority="https://login.microsoftonline.com/common",
    token_cache=msal.TokenCache() # viable too https://msal-python.rtfd.io/en/latest/#msal.SerializableTokenCache
)

app = flask.Flask(__name__)
app.config.from_object(app_config)
flask_session.Session(app)

@app.route("/finishLogin", methods=["GET"])
def login():
    if("auth_flow" not in flask.session):
        return "session missing", 400

    flow = flask.session["auth_flow"]
    token = msal_app.acquire_token_by_auth_code_flow(flow, auth_response=flask.request.args)
    return "login success", 200

@app.route("/", methods=["GET"])
def home():
    flow = msal_app.initiate_auth_code_flow(scopes=["Mail.ReadBasic", "Mail.Read"])
    # no error checks
    flask.session["auth_flow"] = flow

    return f"Link: {flow['auth_uri']}", 200

if __name__ == "__main__":
    t = threading.Thread(target=email_parser_thread.parser_loop, args=(msal_app,))
    t.start()

    app.run()