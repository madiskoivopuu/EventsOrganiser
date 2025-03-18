import dotenv
dotenv.load_dotenv(".env")
import json

from dataclasses import dataclass
import torch, os, datasets
from transformers import BitsAndBytesConfig, AutoTokenizer, AutoModelForCausalLM, TrainingArguments, DataCollatorForLanguageModeling
from trl import SFTTrainer
from peft import LoraConfig

import email_data
from email_data import Email

DATASET_LOC = "./training_data/"
INPUT_OUTPUT_SEPARATOR = "!<-=->!" # for simplicity we use text files which contain stuff separated by this token (input above, output below)

@dataclass
class PromptMetadata:
    comment: str
    tags: list[str]
    reader_email: str
    mail_data: str
    expected_output: dict[str]

def read_prompt_file(loc: str) -> PromptMetadata:
    with open(f"{loc}", "r", encoding="UTF-8") as f:
        content = f.read().split(INPUT_OUTPUT_SEPARATOR)

        return PromptMetadata(
            comment=content[0],
            tags=[tag.strip() for tag in content[1].split(";") if len(tag.strip()) > 0],
            reader_email=content[2],
            mail_data=content[3],
            expected_output=json.loads(content[4])
        )

def read_all_prompts(dir: str) -> list[PromptMetadata]:
    metadatas = []
    for filename in os.listdir(dir):
        metadatas.append(
            read_prompt_file(f"{dir}/{filename}")
        )

    return metadatas

def generate_chats_from_prompt(metadata: PromptMetadata) -> list[str]:
    global sys_prompt, tokenizer
    email = email_data.str_to_mail(metadata.mail_data)
    chats = []
    prompt_template = [
        {
            "role": "system",
            "content": sys_prompt % ",".join(metadata.tags)
        },
        {
            "role": "user",
            "content": email_data.format_email_for_llm(email)
        },
        {
            "role": "assistant",
            "content": ""
        }
    ]

    prompt_template[3]["content"] = json.dumps(metadata.expected_output)
    chats.append(
        tokenizer.apply_chat_template(prompt_template, tokenize=False)
    )

    prompt_template[3]["content"] = json.dumps(metadata.expected_output, indent=4)
    chats.append(
        tokenizer.apply_chat_template(prompt_template, tokenize=False)
    )

    prompt_template[3]["content"] = json.dumps(metadata.expected_output, indent="\t")
    chats.append(
        tokenizer.apply_chat_template(prompt_template, tokenize=False)
    )

if __name__ == "__main__":
    bnb_conf = BitsAndBytesConfig(
        load_in_8bit=True,
        bnb_8bit_compute_dtype=torch.bfloat16
    )

    tokenizer = AutoTokenizer.from_pretrained("google/gemma-2-9b-it", token=os.environ["HF_TOKEN"])
    model = AutoModelForCausalLM.from_pretrained(
        "google/gemma-2-9b-it", 
        quantization_config=bnb_conf,
        device_map="auto",
        token=os.environ["HF_TOKEN"]
    )

    sys_prompt = ""
    with open(f"{DATASET_LOC}/SYS_PROMPT.txt", "r", encoding="UTF-8") as f:
        sys_prompt = f.read()

    training_dataset = datasets.Dataset.from_list(read_prompts(f"{DATASET_LOC}/train"))
    training_dataset = training_dataset.map(lambda data: tokenizer(data["prompt"] + tokenizer.eos_token, max_length=8192, truncation=True), batched=False)
    training_dataset = training_dataset.remove_columns(["prompt"])

    #val_dataset = datasets.Dataset.from_list(read_prompts(f"{DATASET_LOC}/val"))
    #val_dataset = val_dataset.map(lambda data: tokenizer(data["prompt"] + tokenizer.eos_token, max_length=8192, truncation=True), batched=False)
    #val_dataset = val_dataset.remove_columns(["prompt"])

    # prepare peft model & train

    peft_config = LoraConfig(
        lora_alpha=16,
        lora_dropout=0.1,
        r=64,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=["q_proj", "o_proj", "k_proj", "v_proj", "gate_proj", "up_proj", "down_proj"]  
    )
    model.add_adapter(peft_config)

    trainer = SFTTrainer(
        model = model, 
        tokenizer = tokenizer, 
        train_dataset=training_dataset, 
        peft_config=peft_config,
        dataset_text_field="prompt",

        args = TrainingArguments(
            output_dir="./training",
            remove_unused_columns=False,
            per_device_train_batch_size=2,
            gradient_checkpointing=True,
            gradient_accumulation_steps=4,
            max_steps=400,
            learning_rate=2.5e-5, 
            logging_steps=5,
            fp16=True,
            optim="paged_adamw_8bit",
            save_strategy="steps",     
            save_steps=50,             
    #                         evaluation_strategy="steps",
    #                         eval_steps=5,              
    #                         do_eval=True,
            report_to = "none",
        ),
        data_collator=DataCollatorForLanguageModeling(tokenizer, mlm=False),
    )
    trainer.train()