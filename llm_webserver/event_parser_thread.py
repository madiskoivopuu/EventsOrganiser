from helpers import apps
from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta

import app_config
import time

EMAIL_SENT_AFTER = datetime.now(timezone.utc) + relativedelta(months=-6)

def get_last_parsed_email_date(acc_id: str, mail_type: str) -> datetime:
    sql_cursor = apps.events_mysql.cursor(dictionary=True)
    
    affected_rows = sql_cursor.execute("SELECT last_parsed_email_date FROM parsing_status WHERE mail_acc_id = %s AND mail_acc_type = %s", (acc_id, mail_type))
    if(affected_rows == 0):
        sql_cursor.execute("INSERT INTO parsing_status (mail_acc_id, mail_acc_type, last_parsed_email_date) VALUES (%s, %s, %s)", (acc_id, mail_type, EMAIL_SENT_AFTER.strftime("%Y-%m-%d %H:%M:%S")))
        return EMAIL_SENT_AFTER
    
    result = sql_cursor.fetchone() 
    # last parsed email dates are in DATETIME field and UTC timezone, we need to retain that info
    return datetime.strptime(result["last_parsed_email_date"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)

def update_last_parsed_email_date(acc_id: str, mail_type: str, email_date: datetime):
    sql_cursor = apps.events_mysql.cursor(dictionary=True)
    affected_rows = sql_cursor.execute("UPDATE parsing_status SET last_parsed_email_date = %s WHERE mail_acc_id = %s AND mail_acc_type = %s", (email_date.strftime("%Y-%m-%d %H:%M:%S"), acc_id, mail_type))
    return affected_rows != 0

# Only parses outlook emails for now
def parse_loop():
    while True:
        for account in apps.ms_app.get_accounts():
            access_token = apps.ms_app.acquire_token_silent(account=account, scopes=app_config.SCOPES)
            if not access_token: continue

        time.sleep(5)