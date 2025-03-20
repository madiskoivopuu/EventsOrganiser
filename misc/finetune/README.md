# LLM finetuning subproject
A fragment in the project related to finetuning Llama 3.2 to give more accurate event information, given the event parser propmts.

## Training the model
You will need PyTorch, unsloth, trl, transformers and datasets installed. 
To begin training, run `py finetune.py` and you will start finetuning the model! Outputs of the trained LoRA model will go into "outputs" directory

Currently, training the model will require at least 20GB of VRAM, if you have less then enable load_in_4bit to reduce VRAM usage. 
Unsloth most likely also has other types of optimizations to reduce the VRAM usage even further.

## Converting merged model to GGUF
If you plan on using the *.gguf format of the model, you can use convert_hf_to_gguf.py to do so.

Firstly, you need to clone the llama.cpp repository with `git clone https://github.com/ggml-org/llama.cpp`. After that, install gguf for Python with `pip install gguf`

After those steps, you can convert the model to GGUF with the following command:
`py ./llama.cpp/convert_hf_to_gguf.py ./outputs/merged_model --outfile ./outputs/gguf/llama3.2-3b-it-finetuned.gguf --outtype bf16`

Another method to save to GGUF would be to update finetune.py to save the model directly to GGUF, changing `unsloth.save.unsloth_save_pretrained_merged(model, "./outputs/merged_model", tokenizer)` to `unsloth.save.unsloth_save_pretrained_gguf(model, "./outputs/gguf", tokenizer)`