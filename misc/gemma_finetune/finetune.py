import dotenv
dotenv.load_dotenv(".env")

import torch, os, datasets
from transformers import BitsAndBytesConfig, AutoTokenizer, AutoModelForCausalLM, TrainingArguments, DataCollatorForLanguageModeling
from trl import SFTTrainer
from peft import LoraConfig

CURR_DATASET = "./training_data/event_parser"
INPUT_OUTPUT_SEPARATOR = "!<<<OUTPUT>>>!" # for simplicity we use text files which contain input & output separated by this token (input above, output below)

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

training_prompts = []
sys_prompt = ""
with open(f"{CURR_DATASET}/SYS_PROMPT.txt", "r", encoding="UTF-8") as f:
    sys_prompt = f.read()

for filename in os.listdir(CURR_DATASET):
    if filename == "SYS_PROMPT.txt":
        continue

    f = open(f"{CURR_DATASET}/{filename}", "r", encoding="UTF-8")
    content = f.read()
    f.close()

    llm_input, llm_output = content.split(INPUT_OUTPUT_SEPARATOR)
    llm_input, llm_output = llm_input.rstrip(), llm_output.lstrip()

    formatted_prompt = tokenizer.apply_chat_template(
        [
            {
                "role": "user",
                "content": llm_input
            },
            {
                "role": "assistant",
                "content": llm_output
            }
        ], tokenize=False, 
    )

    formatted_prompt.replace("<bos>", f"<bos>{sys_prompt}")
    training_prompts.append({"prompt": formatted_prompt})

training_dataset = datasets.Dataset.from_list(training_prompts)
training_dataset = training_dataset.map(lambda data: tokenizer(data["prompt"] + tokenizer.eos_token, max_length=8192, truncation=True), batched=False)
training_dataset = training_dataset.remove_columns(["prompt"])

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