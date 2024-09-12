import requests
from datetime import datetime
from helpers.email_data import Email

def read_user_emails_raw(access_token: str, skip: int = 0, top: int = 100):
    response = requests.get(f"https://graph.microsoft.com/v1.0/me/messages?$top={top}&$skip={skip}", 
                    headers={
                        "Prefer": 'outlook.body-content-type="text"',
                        "Authorization": "Bearer " + access_token
                    }
                )
    if(response.status_code != 200):
        raise {"status": "fail", "data": None, "status_code": response.status_code, "response_data": response.text, "response_headers": response.headers}
    
    return {"status": "success", "data": response.json()}

# Reads emails that were sent after or on the same day as the given date
def read_emails_after_date(access_token: str, after_date: datetime, skip: int = 0, top: int = 100):
    emails = []

    last_processed_email_date = datetime.now()
    while last_processed_email_date.date() >= after_date.date():
        result = read_user_emails_raw(access_token, skip=skip, top=100)
        if(result["status"] != "success"):
            return result
        if(len(result["data"]["value"]) == 0): # no more emails to read from user
            break
        
        for data in result["data"]["value"]:
            email = Email.from_outlook_json(data)
            last_processed_email_date = email.send_date

            if(email.send_date < after_date.date()):
                break

            emails.append(email)

        skip += top

    return {"status": "success", "data": emails}