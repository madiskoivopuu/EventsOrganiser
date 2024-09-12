from helpers import apps, msgraph
from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta
from helpers.email_data import Email
from helpers.model import Gemma2EventParser

import langdetect
import app_config
import time

EMAIL_SENT_AFTER_DATE = datetime.now(timezone.utc) + relativedelta(months=-6)
gemma = Gemma2EventParser(n_threads=8, n_threads_batch=8)

def get_last_parsed_email_date(acc_id: str, mail_type: str) -> datetime:
    sql_cursor = apps.events_mysql.cursor(dictionary=True)
    
    affected_rows = sql_cursor.execute("SELECT last_parsed_email_date FROM parsing_status WHERE mail_acc_id = %s AND mail_acc_type = %s", (acc_id, mail_type))
    if(affected_rows == 0):
        sql_cursor.execute("INSERT INTO parsing_status (mail_acc_id, mail_acc_type, last_parsed_email_date) VALUES (%s, %s, %s)", (acc_id, mail_type, EMAIL_SENT_AFTER.strftime("%Y-%m-%d %H:%M:%S")))
        return EMAIL_SENT_AFTER_DATE
    
    result = sql_cursor.fetchone() 
    # last parsed email dates are in DATETIME field and UTC timezone, we need to retain that info
    return datetime.strptime(result["last_parsed_email_date"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)

def update_last_parsed_email_date(acc_id: str, mail_type: str, email_date: datetime):
    sql_cursor = apps.events_mysql.cursor(dictionary=True)
    affected_rows = sql_cursor.execute("UPDATE parsing_status SET last_parsed_email_date = %s WHERE mail_acc_id = %s AND mail_acc_type = %s", (email_date.strftime("%Y-%m-%d %H:%M:%S"), acc_id, mail_type))
    return affected_rows != 0

def get_events_in_emails(emails: list[Email]) -> list[dict]:
    parsed_events_per_email = []
    for email in emails:
        original_title = email.title
        original_content = email.content
        if(langdetect.detect(email.content) != "en"):
            translation_data = gemma.translate_email(email)
            email.content = translation_data["content"]
            email.title = translation_data["title"]

        parsed_events = gemma.parse_events_from_email(email)

        # TODO: add tags parsing
        # for event in parsed_events:
        # gemma.generate_tags_for_email_events()

        email.title = original_title
        email.content = original_content
        parsed_events_per_email.append({
            "email": email,
            "events": parsed_events
        })

    return parsed_events_per_email

# Only parses outlook emails for now
def parse_loop():
    while True:
        for account in apps.ms_app.get_accounts():
            token_data = apps.ms_app.acquire_token_silent(account=account, scopes=app_config.SCOPES)
            if(not token_data): continue # TODO: do we need to remove acc manually from cache?

            last_parsed_date = get_last_parsed_email_date(account["home_account_id"], "outlook")
            if(last_parsed_date < EMAIL_SENT_AFTER_DATE):
                last_parsed_date = EMAIL_SENT_AFTER_DATE

            result = msgraph.read_emails_after_date(token_data["access_token"], last_parsed_date)
            if(result["status"] != "success"):
                # TODO: log it properly
                print("Failed to fetch emails for user. ", result)
                continue

            events = get_events_in_emails(result["data"])
            print(events)

        time.sleep(5)