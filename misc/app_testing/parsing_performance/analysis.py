from datetime import datetime
from dateutil import parser
from dataclasses import dataclass

CONTAINER_LOGS_FILE = "./container_logs/merged.log"
TEST_LOGS_FILE = "performance_test.log"

@dataclass
class SentEmailData:
    mail_id: str
    sent_date: datetime | None = None
    parse_started_date: datetime | None = None
    parse_ended_date: datetime | None = None

# Returns sorted performance data based on the send date
def get_parsing_performance_data() -> list[SentEmailData]:
    data: dict[str, SentEmailData] = {}

    with open(TEST_LOGS_FILE, "r", encoding="UTF-8") as f:
        for line in f:
            if("; http" not in line):
                continue

            parts = line.split(" ")
            sent_date = " ".join(parts[1:5])

            mail_id = parts[5].replace(";", "").strip()
            sent_date = parser.parse(sent_date)

            data[mail_id] = SentEmailData(
                mail_id, sent_date
            )

    # read in parse start data and end data
    with open(CONTAINER_LOGS_FILE, "r", encoding="UTF-8") as f:
        for line in f:
            parts = line.split(" ")
            mail_id = parts[-1].strip() # might not be mail id but it doesn't matter for the following check
            if(mail_id not in data):
                continue

            if("New e-mail" in line):
                data[mail_id].parse_started_date = parser.parse(" ".join(parts[1:5]))
            elif("E-mail parsing finished" in line):
                data[mail_id].parse_ended_date = parser.parse(" ".join(parts[1:5]))

    # data validation, print out issues

    filtered_data = []
    for mail_id, mail_parsing_info in data.items():
        if(mail_parsing_info.parse_started_date > mail_parsing_info.parse_ended_date):
            print(f"Mail ID {mail_id} has parsing start date set to after the end date, filtering it")
            continue

        if(mail_parsing_info.parse_started_date == None):
            print(f"Mail ID {mail_id} has no parsing start date, filtering it")
            continue

        if(mail_parsing_info.parse_ended_date == None):
            print(f"Mail ID {mail_id} has no parsing end date, filtering it")
            continue

        filtered_data.append(mail_parsing_info)

    return sorted(filtered_data, key=lambda val: val.sent_date)

def get_entire_parsing_duration(parsing_performance_data: list[SentEmailData]):
    return parsing_performance_data[-1].parse_ended_date - parsing_performance_data[0].sent_date

data = get_parsing_performance_data()

print(get_entire_parsing_duration(data))