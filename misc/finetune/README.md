# Finetuning subproject

A fragment in the project related to finetuning Llama 3.2 to give more accurate event information, given the event parser propmts.

## Training the model
You will need PyTorch, unsloth, trl, transformers and datasets installed. 
To begin training, run `py finetune.py` and you will start finetuning the model! Outputs of the trained LoRA model will go into "outputs" directory

Currently, training the model will require at least 20GB of VRAM, if you have less then enable load_in_4bit to reduce VRAM usage even further. 
Unsloth most likely also has other types of optimizations to reduce the VRAM usage even further.