from dataclasses import dataclass
from datetime import datetime, timezone
import json

@dataclass
class Email:
    id: str
    title: str
    send_date: datetime # UTC timezone aware send date
    content: str
    sender_email: str # Usually the same as from_email, but can be something different from the original sender, if that person is using a mailing list
    from_email: str # Original sender's email
    recipient_emails: list[str]
    reader_email: str
    is_draft: bool

    @staticmethod
    def from_outlook_json(email_data: dict, reader_email: str) -> 'Email':
        if(email_data["body"]["contentType"] != "text"):
            raise ValueError(f"email data for {email_data['id']} is {email_data['body']['contentType']}, but expected 'text'")
        
        recipients: list[str] = [recipient["emailAddress"]["address"] for recipient in email_data["toRecipients"]]
        sender_email = None if email_data["isDraft"] else email_data["sender"]["emailAddress"]["address"]
        from_email = None if email_data["isDraft"] else email_data["from"]["emailAddress"]["address"]

        return Email(id=email_data["id"],
                    title=email_data["subject"],
                    send_date=datetime.strptime(email_data["sentDateTime"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc), # graph api returns dates in UTC format
                    content=email_data["body"]["content"],
                    sender_email=sender_email,
                    from_email=from_email,
                    recipient_emails=recipients,
                    reader_email=reader_email,
                    is_draft=email_data["isDraft"])
