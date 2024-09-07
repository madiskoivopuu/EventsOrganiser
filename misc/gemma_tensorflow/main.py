import email_data
import model
import time, os

emails = email_data.parse_outlook_emails_from_file("emails.json")
print(emails[8].title)

gemma = model.Gemma2EventParser()

s = time.time()
events = gemma.parse_events_from_emails([emails[8]])
elapsed = time.time() - s
print(events)
print(f"TOOK {elapsed} s")

s = time.time()
events = gemma.parse_events_from_emails([emails[7]])
elapsed = time.time() - s
print(events)
print(f"TOOK {elapsed} s")
