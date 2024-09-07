from dataclasses import dataclass
from datetime import datetime
import json

@dataclass
class Email:
    id: str
    title: str
    send_date: datetime
    content: str
    sender_email: str # Usually the same, but can be something different from the original sender, if that person is using a mailing list
    from_email: str # Original sender's email
    recipient_emails: list[str]
    reader_email: str

    @staticmethod
    def from_outlook_json(email_data: dict, reader_email: str):
        if(email_data["body"]["contentType"] != "text"):
            raise RuntimeError(f"email data for {email_data['id']} is not text")
        
        recipients: list[str] = [recipient["emailAddress"]["address"] for recipient in email_data["toRecipients"]]

        return Email(id=email_data["id"],
                     title=email_data["subject"],
                     send_date=datetime.strptime(email_data["sentDateTime"], "%Y-%m-%dT%H:%M:%SZ"),
                     content=email_data["body"]["content"],
                     sender_email=email_data["sender"]["emailAddress"]["address"],
                     from_email=email_data["from"]["emailAddress"]["address"],
                     recipient_emails=recipients,
                     reader_email=reader_email
                    )
    

def parse_outlook_emails_from_file(filename: str, reader_email: str) -> list[Email]:
    emails: list[Email] = []
    with open(filename, "r", encoding="UTF-8") as f:
        emails_json = json.load(f)
        emails = [Email.from_outlook_json(data, reader_email) for data in emails_json["value"]]
        return emails
