import msal
import os, dotenv
import urllib.parse as parse
import requests

dotenv.load_dotenv(".env")
app = msal.ConfidentialClientApplication(
    client_id="e7531514-8913-47a8-8cd2-b80dcef955b7",
    client_credential=os.getenv("MSAL_CLIENT_SECRET"), # should replace with a certificate? for ConfidentialClientApplication
    authority="https://login.microsoftonline.com/common",
    token_cache=msal.TokenCache() # viable too https://msal-python.rtfd.io/en/latest/#msal.SerializableTokenCache
)

def log_in_and_fetch_user_token():
    flow = app.initiate_auth_code_flow(scopes=["Mail.ReadBasic", "Mail.Read"])
    print(f"Use the following URL to log in: {flow['auth_uri']}")

    redirected_to_url = input("After logging in, copy the URL you were redirected to: ")
    auth_response = dict(parse.parse_qsl(parse.urlsplit(redirected_to_url).query))

    token = app.acquire_token_by_auth_code_flow(flow, auth_response=auth_response)
    return token

def read_user_emails(access_token):
    response = requests.get("https://graph.microsoft.com/v1.0/me/messages", 
                    headers={
                        "Prefer": 'outlook.body-content-type="text"',
                        "Authorization": "Bearer " + access_token
                    }
                )
    if(response.status_code != 200):
        print("Response returned with non-OK code")
        print(response.status_code)
        print(response.text)
    else:
        print("Saving e-mails to file")
        with open("emails.txt", "w", encoding="UTF-8") as f:
            f.write(response.text)
    

    
token = log_in_and_fetch_user_token()
print(token)
read_user_emails(token["access_token"])