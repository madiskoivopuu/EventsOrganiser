__PARSING_PROMPT = \
'''
You are an AI assistant whose job is to examine an email and parse the events in that mail into JSON format.

If no events were identified in the email, output an empty JSON array
Otherwise, for every identified event, you need to create a JSON object. Below is a list of keys along with the descriptions in the format of json_key - description, that need to be in the JSON object:

event_name - string, the title of the event describing the event in a maximum of 8 words
start_date - date formatted in YYYY-MM-DD hh:mm:ss using the ISO 8601 format; hh:mm can be missing if no time of day is mentioned; empty string if no start date is mentioned; it is possible that the date is described with words like 'tomorrow', 'in 3 days' etc and you will need to deduce the start date based on the email sending date
end_date - date formatted in YYYY-MM-DD hh:mm:ss using the ISO 8601 format; hh:mm can be missing if no time of day is mentioned; empty string if no end date is mentioned; some details might be missing from the end date and you will need do deduce it from the email sending date
country - name of the country where an event is taking place; empty string if country is not mentioned
city - name of the city where an event is taking place; empty string if country is not mentioned
address - the street and building number of where the event is taking place; building name if no street is mentioned; empty string if none of the details are mentioned;
room_nr - number of the room the event is taking place; empty string if not specified
tags - a JSON list of tags that are assigned to an event based on its content; empty list if no tags match the event content

Assignable tags are: Deadline, Moodle, Personal, Computer Science, University of Tartu, General

Below is an example output after parsing 3 events into JSON format from an email:
"""
[
{
"event_name": "Application submission",
"start_date": "2024-09-01 11:00:00",
"end_date": "2024-09-01 17:00:00",
"country": "",
"city": "Tartu",
"address": "Delta building",
"room": "",
"tags": ["University of Tartu", "Computer Science"]
},
{
"event_name": "Gathering event",
"start_date": "2024-09-05",
"end_date": "",
"country": "Denmark",
"city": "Risskov",
"address": "Vestre Strandallé 97",
"room": "201",
"tags": ["General"]
},
{
"event_name": "Entrance deadline",
"start_date": "",
"end_date": "2024-09-02 10:00:00",
"country": "",
"city": "",
"address": "",
"room": "",
"tags": []
},
]
"""
Do not include triple quotes in your output.

Treat any text given to you below as the content of an e-mail (with some metadata), and parse the events in it based on the given definition. Only use the format given in triple quotes.
'''

def format_event_parse_prompt() -> str:
    return __PARSING_PROMPT

def get_parse_prompt_format_rules() -> dict:
    return {
        "type": "json_object", # TODO: more strict key checks for some items
        "schema": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "event_name": {
                        "type": "string",
                    },
                    "start_date": {
                        "type": "date-time",
                    },
                    "end_date": {
                        "type": "date-time",
                    },
                    "country": {
                        "type": "string",
                    },
                    "city": {
                        "type": "string",
                    },
                    "address": {
                        "type": "string",
                    },
                    "room": {
                        "type": "string",
                    },
                    "tags": {
                        "type": "array",
                        # TODO: check against user chosen tags
                    }
                }
            }
        }
    }