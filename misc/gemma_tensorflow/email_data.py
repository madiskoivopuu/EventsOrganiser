from dataclasses import dataclass
from datetime import datetime
import json

@dataclass
class Email:
    id: str
    title: str
    send_date: datetime
    content: str

    @staticmethod
    def from_outlook_json(email_data: dict):
        if(email_data["body"]["contentType"] != "text"):
            raise RuntimeError(f"email data for {email_data['id']} is not text")
        
        return Email(id=email_data["id"],
                     title=email_data["subject"],
                     send_date=datetime.strptime(email_data["sentDateTime"], "%Y-%m-%dT%H:%M:%SZ"),
                     content=email_data["body"]["content"]
                     )
    

def parse_outlook_emails_from_file(filename: str) -> list[Email]:
    emails = []
    with open(filename, "r", encoding="UTF-8") as f:
        emails_json = json.load(f)
        emails = [Email.from_outlook_json(data) for data in emails_json["value"]]
        return emails
