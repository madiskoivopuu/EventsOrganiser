import dotenv
dotenv.load_dotenv(".env")
import json
import copy
import random

from dataclasses import dataclass
import torch, os, datasets, unsloth
from transformers import TrainingArguments
from trl import SFTTrainer
from unsloth import FastLanguageModel
import unsloth.save

import email_data
from email_data import Email

DATASET_LOC = "./training_data/"
INPUT_OUTPUT_SEPARATOR = "!<-=->!" # for simplicity we use text files which contain stuff separated by this token (input above, output below)
MAX_SEQ_LENGTH = 32768
BATCH_SIZE = 8
with open(f"{DATASET_LOC}/SYS_PROMPT.txt", "r", encoding="UTF-8") as f:
    SYS_PROMPT = f.read()

@dataclass
class TrainingData:
    comment: str
    categories: list[str]
    reader_email: str
    mail_data: str
    expected_output: list[dict[str]]

def read_prompt_file(loc: str) -> TrainingData:
    with open(f"{loc}", "r", encoding="UTF-8") as f:
        content = f.read().split(INPUT_OUTPUT_SEPARATOR)

        return TrainingData(
            comment=content[0].strip(),
            categories=[category.strip() for category in content[1].split(";") if len(category.strip()) > 0],
            reader_email=content[2],
            mail_data=content[3].strip(),
            expected_output=json.loads(content[4])
        )

def read_all_prompts(dir: str) -> list[TrainingData]:
    metadatas = []
    for filename in os.listdir(dir):
        obj_loc = f"{dir}/{filename}"

        if(not os.path.isfile(obj_loc)):
            metadatas += read_all_prompts(obj_loc)
        else:
            metadatas.append(
                read_prompt_file(f"{dir}/{filename}")
            )

    return metadatas

def get_all_unique_categories(metadatas: list[TrainingData]) -> list[str]:
    categories = set()
    for metadata in metadatas:
        for tag in metadata.categories:
            if(tag.strip() != ""):
                categories.add(tag)

    return list(categories)

def generate_chats_from_prompts(metadatas: list[TrainingData]) -> list[str]:
    global SYS_PROMPT

    default_categories = get_all_unique_categories(metadatas)

    chats = []
    for metadata in metadatas:
        email = email_data.str_to_mail(metadata.mail_data, metadata.reader_email)

        sys_part = {
            "role": "system",
            "content": ""
        }
        categories = metadata.categories.copy()
        if(len(categories) == 0):
            categories = default_categories.copy()
        random.shuffle(categories)

        sys_part["content"] = SYS_PROMPT % ",".join(categories)

        user_part = {
            "role": "user",
            "content": email_data.format_email_for_llm(email)
        }
        response_part = {
            "role": "assistant",
            "content": ""
        }

        chat_ = {
            "messages": [
                sys_part,
                user_part,
                response_part
            ]
        }

        chat_["messages"][2]["content"] = json.dumps(metadata.expected_output)
        chats.append(
            copy.deepcopy(chat_)
        )

    return chats

# followed https://huggingface.co/docs/trl/en/sft_trainer#supervised-fine-tuning-trainer
# and https://colab.research.google.com/github/unslothai/notebooks/blob/main/nb/Llama3.2_(1B_and_3B)-Conversational.ipynb
if __name__ == "__main__":
    def formatting_prompts_func(data):
        global tokenizer 
    
        convos = data["messages"]
        texts = [tokenizer.apply_chat_template(convo, tokenize = False, add_generation_prompt = False) for convo in convos]
        return { "text" : texts, }

    model, tokenizer = FastLanguageModel.from_pretrained(
        "./trainable_llm/llama3.2-3b-instruct",
        max_seq_length=MAX_SEQ_LENGTH,
        load_in_4bit=False,
        load_in_8bit=True,
        dtype=torch.bfloat16
    )

    model = FastLanguageModel.get_peft_model(
        model,
        r = 16, # Choose any number > 0 ! Suggested 8, 16, 32, 64, 128
        target_modules = ["q_proj", "k_proj", "v_proj", "o_proj",
                        "gate_proj", "up_proj", "down_proj",],
        lora_alpha = 16,
        lora_dropout = 0, # Supports any, but = 0 is optimized
        bias = "none",    # Supports any, but = "none" is optimized
        # [NEW] "unsloth" uses 30% less VRAM, fits 2x larger batch sizes!
        use_gradient_checkpointing = "unsloth", # True or "unsloth" for very long context
        random_state = 3407,
        use_rslora = False,  # We support rank stabilized LoRA
        loftq_config = None, # And LoftQ
    )
    tokenizer = unsloth.chat_templates.get_chat_template(
        tokenizer,
        chat_template = "llama-3.1",
    )
    
    SYS_PROMPT = ""
    with open(f"{DATASET_LOC}/SYS_PROMPT.txt", "r", encoding="UTF-8") as f:
        SYS_PROMPT = f.read()

    training_prompts = read_all_prompts(f"{DATASET_LOC}/train")
    validation_prompts = read_all_prompts(f"{DATASET_LOC}/train")

    training_ds = datasets.Dataset.from_list(generate_chats_from_prompts(training_prompts))
    training_ds = training_ds.map(formatting_prompts_func, batched=True)
    validation_ds = datasets.Dataset.from_list(generate_chats_from_prompts(validation_prompts))
    validation_ds = validation_ds.map(formatting_prompts_func, batched=True)

    trainer = SFTTrainer(
        model=model, 
        tokenizer=tokenizer,
        train_dataset=training_ds, 
        eval_dataset=validation_ds,
        args=TrainingArguments(
            per_device_train_batch_size = 8,
            gradient_accumulation_steps = 4,
            num_train_epochs=10.0,
            learning_rate = 2e-4,
            fp16 = not unsloth.is_bfloat16_supported(),
            bf16 = unsloth.is_bfloat16_supported(),
            logging_steps = 1,
            optim = "adamw_8bit",
            weight_decay = 0.01,
            lr_scheduler_type = "linear",
            seed = 3407,
            output_dir = "outputs",
            report_to = "none", # Use this for WandB etc

            fp16_full_eval = True,
            per_device_eval_batch_size = 8,
            eval_accumulation_steps = 4,
            eval_strategy = "steps",
            eval_steps = BATCH_SIZE / len(training_ds),
        )
    )
    trainer.train()

    unsloth.save.unsloth_save_pretrained_merged(model, "./outputs/merged_model", tokenizer)

    #unsloth.save.unsloth_save_pretrained_gguf(model, "./outputs/gguf", tokenizer)
