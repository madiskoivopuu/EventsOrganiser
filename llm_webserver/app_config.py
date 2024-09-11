import flask, flask_session
import msal

import app_config

app = msal.ConfidentialClientApplication(
    client_id="e7531514-8913-47a8-8cd2-b80dcef955b7", # TODO: use os env
    client_credential=os.getenv("MSAL_CLIENT_SECRET"), # should replace with a certificate? for ConfidentialClientApplication
    authority="https://login.microsoftonline.com/common",
    token_cache=msal.TokenCache() # viable too https://msal-python.rtfd.io/en/latest/#msal.SerializableTokenCache
)

app = flask.Flask(__name__)
app.config.from_object(app_config)
flask_session.Session(app)