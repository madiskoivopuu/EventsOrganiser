# To make creating training data easier, includes metadata that would otherwise take me a min to get and write down for each email
import json
from pathvalidate import sanitize_filename

# Include email data module
import sys, os
sys.path.append(os.path.abspath(os.path.join('..', 'gemma_tensorflow')))
from gemma_tensorflow.email_data import Email

emails_plaintext = open("emails.json", "r", encoding="UTF-8").read()
emails_json = json.reads(emails_plaintext)

for email_data in emails_json["value"]:
    email = Email.from_outlook_json(email_data)

    prepared_content = f"Email reader: {email.reader_email}\n"
    prepared_content += f"Email sender: {email.sender_email}\n"
    prepared_content += f"Email from: {email.from_email}\n"
    prepared_content += f"Email recipients: {', '.join(email.recipient_emails)}\n"
    prepared_content += f"Send time: {email.send_date.strftime("%H:%M %d/%m/%Y")}\n"
    prepared_content += f"Title: {email.title}\n"
    prepared_content += f"Content:\n{email.content}"

    out_filename = sanitize_filename(email.title)
    with open(f"./emails_output/{out_filename}.txt", "w", encoding="UTF-8") as f:
        f.write(prepared_content)