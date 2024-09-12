import app_config
import msal, pymysql

# TODO: make some error checks in case mysql connections fail

ms_app = msal.ConfidentialClientApplication(
    client_id=app_config.MICROSOFT_APP_CLIENT_ID,
    client_credential=app_config.MICROSOFT_APP_SECRET, # should replace with a certificate? for ConfidentialClientApplication
    authority="https://login.microsoftonline.com/common",
    token_cache=msal.TokenCache() # viable too https://msal-python.rtfd.io/en/latest/#msal.SerializableTokenCache
)

events_mysql = pymysql.connect(
    host="172.17.89.147",
    user=app_config.EVENTS_PARSER_MYSQL_USER,
    password=app_config.EVENTS_PARSER_MYSQL_PASSWORD,
    database="events"
)