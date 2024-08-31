import json, langdetect
import dotenv, os, openai
import openai
dotenv.load_dotenv()

openai_client = openai.OpenAI(
    api_key=os.getenv("OPENAI_PROJECT_SECRET")
)

emails_data = {}
with open("emails.txt", "r", encoding="UTF-8") as f:
    emails_data = json.load(f)

eng_emails = []
for email in emails_data["value"]:
    if email["body"]["contentType"] == "text" and langdetect.detect(email["body"]["content"]) == "en":
        eng_emails.append(email)

print(f"English emails detected: {len(eng_emails)}")

for email in eng_emails[:1]:
    chat_completion = openai_client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": 
                '''
You are an AI assistant whose job is to examine an e-mail and parse the events in that mail into a given format.

First, we define the word 'event' as the following -  a thing, such as an appointment, meeting, deadline etc, that: 
1) has defined at least a start date or an end date; 
2) happens or takes place; 
3) focuses on the recipient having a choice to participate.

If no events were identified in the e-mail, only write 'None found' in your output and disregard the event format.
Otherwise, for every identified event, you need to parse out the following details using these rules

Event Name - the title of the event; if not available, a brief name with a maximum of 10 words that describes the event in the e-mail
Event Start Date - date formatted in hh:mm DD/MM/YYYY using the ISO 8601 convention; hh:mm can be missing if no time of day is mentioned; N/A if no start date is mentioned; it is possible that the date is described with words like 'tomorrow', 'in 3 days' etc and you will need to deduce the start date based on the e-mail sending date, which is **CHANGE THIS**
Event End Date - date formatted in hh:mm DD/MM/YYYY using the ISO 8601 convention; hh:mm can be missing if no time of day is mentioned; N/A if no end date is mentioned; some details might be missing from the end date and you will need do deduce it from the e-mail sending date, which is **CHANGE THIS**
Event Location: the place of where the event is being hosted; can be a room, country, city, building or a mix of these, use N/A for the details that are missing; should be formatted as Country - City - Building name - Room number

Follow these rules and format each of the events found in the e-mail like shown in triple quotes:
"""
Event Name: example name
Event Start Date: 10:00 01/09/2024
Event End Date: N/A
Event Location: N/A
"""
Do not include triple quotes in your output.
If there are multiple events, use this format and leave an empty line between each of those formatted events.

Treat any text given to you below as the content of an e-mail, and parse the events in it based on the given definition. Only use the format given in triple quotes.
                '''
            },
            {
                "role": "user",
                "content": email["body"]["content"]
            }
        ],
        model="gpt-4o-mini",
)