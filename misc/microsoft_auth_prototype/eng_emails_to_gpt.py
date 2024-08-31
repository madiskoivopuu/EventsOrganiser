import json, langdetect


emails_data = {}
with open("emails.txt", "r", encoding="UTF-8") as f:
    emails_data = json.load(f)

eng_emails = []
for email in emails_data["value"]:
    if email["body"]["contentType"] == "text" and langdetect.detect(email["body"]["content"]) == "en":
        eng_emails.append(email)

print(f"English emails detected: {len(eng_emails)}")