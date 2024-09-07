import email_data
import model
import time, os

emails = email_data.parse_outlook_emails_from_file("emails.json", "madis.koivopuu@ut.ee")
print(emails[8].title)

gemma = model.Gemma2EventParser(n_ctx=8192, verbose=False)

print("Starting to parse events")
print("1.")

events = gemma.parse_events_from_emails([emails[8]])
print(events)

print("2.")
events = gemma.parse_events_from_emails([emails[7]])
print(events)
