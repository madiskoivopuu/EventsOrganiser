import json
import prompt_config
from llama_cpp import Llama

from email_data import Email

# TODO: use env variables or config later on
EDIT__MODEL_FILE = "./gemma/gemma-2-9b-it-Q8_0-f16.gguf"

class Gemma2EventParser():
    MAX_GENERATED_TOKENS = 1024

    def __init__(self, **kwargs) -> None:
        self.model = Llama(
            model_path=EDIT__MODEL_FILE, 
            chat_format="gemma",
            **kwargs
        )

    def translate_email(self, email_content: str) -> str:
        prompt: str = prompt_config.get_translation_prompt()
        chat_output = self.model.create_chat_completion(
            messages = [
                {
                    "role": "user",
                    "message": prompt
                },
                {
                    "role": "user",
                    "message": email_content
                }
            ],
            max_tokens=self.MAX_GENERATED_TOKENS,
        )
        return chat_output["choices"][0]["message"]["content"]
    
    def parse_events_from_emails(self, emails: list[Email]) -> list[str]:
        events_plaintext: list[dict] = []
        for email in emails:
            prompt = prompt_config.format_event_parse_prompt()
            
            # TODO: make a better function for this
            prepared_content: str = f"Email reader: {email.reader_email}\n"
            prepared_content += f"Email sender: {email.sender_email}\n"
            prepared_content += f"Email from: {email.from_email}\n"
            prepared_content += f"Email recipients: {', '.join(email.recipient_emails)}\n"
            prepared_content += f"Send time: {email.send_date.isoformat()}\n"
            prepared_content += f"Title: {email.title}\n"
            prepared_content += f"Content:\n{email.content}"

            chat_output = self.model.create_chat_completion(
                messages = [
                    {
                        "role": "user",
                        "content": prompt
                    },
                    {
                        "role": "user",
                        "content": prepared_content
                    },
                ],
                response_format={
                    "type": "json_object"
                },
                max_tokens=self.MAX_GENERATED_TOKENS
            )
        
            events_plaintext.append(json.loads(chat_output["choices"][0]["message"]["content"]))

        return events_plaintext
    
    def generate_tags_for_email_events(self, event_name: str, email: Email) -> list[str]:
        raise NotImplementedError("")