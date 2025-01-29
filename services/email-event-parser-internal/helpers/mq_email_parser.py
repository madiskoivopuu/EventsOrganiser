from .email_data import Email

def parse(msg_with_email: dict[str]) -> Email:
    email_data = msg_with_email["email"]
    reader_email = msg_with_email["reader_email"]

    match msg_with_email["account_type"]:
        case "outlook":
            return Email.from_outlook_json(email_data, reader_email)
        case _:
            return None