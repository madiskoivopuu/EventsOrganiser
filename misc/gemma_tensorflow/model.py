import os
import keras_nlp
import prompt_config

from email_data import Email

os.environ["KERAS_BACKEND"] = "tensorflow"
os.environ["XLA_PYTHON_CLIENT_MEM_FRACTION"] = "0.9"

# TODO: use env variables later on
EDIT__WEIGHTS_FILE = "./gemma/model.weights.h5"
EDIT__VOCAB_FILE = "./gemma/assets/tokenizer/vocabulary.spm"
EDIT__GEMMA_METADATA_DIR = "./gemma"

class Gemma2Model():
    START_USER_TURN = "<start_of_turn>user\n"
    START_MODEL_TURN = "<start_of_turn>model\n"
    END_OF_TURN = "<end_of_turn>\n"

    def __init__(self) -> None:
        #gemma_tokenizer = keras_nlp.models.GemmaTokenizer(EDIT__VOCAB_FILE)
        #gemma_preprocessor = keras_nlp.models.GemmaPreprocessor(gemma_tokenizer)
        #gemma_backbone = keras_nlp.models.GemmaCausalLM.from_preset("gemma2_instruct_9b_en", load_weights=True)
        #gemma_backbone.load_weights(EDIT__WEIGHTS_FILE)

        #self.model = keras_nlp.models.GemmaCausalLM(
        #    backbone=gemma_backbone,
        #    preprocessor=gemma_preprocessor
        #)
        self.model = keras_nlp.models.GemmaCausalLM.from_preset("gemma_instruct_2b_en")

    def translate_email(self, email_content: str) -> str:
        prompt = prompt_config.get_translation_prompt() + "\n" + self.START_USER_TURN + email_content + self.END_OF_TURN
        translation = self.model.generate(prompt + self.START_MODEL_TURN)
        return translation.replace(prompt, "")
    
    def parse_events_from_emails(self, emails: list[Email]) -> list[str]:
        events_plaintext = []
        for email in emails:
            prompt = prompt_config.format_event_parse_prompt(email.send_date.strftime("%d/%m/%Y")) + "\n" + self.START_USER_TURN + email.content + self.END_OF_TURN
            events_in_email = self.model.generate(prompt + self.START_MODEL_TURN)
            events_plaintext.append(events_in_email)

        return events_plaintext.replace(prompt, "")
    
    def generate_tags_for_email_events(self, event_name: str, email: Email) -> list[str]:
        raise NotImplementedError("")