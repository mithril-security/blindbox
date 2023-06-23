from transformers import AutoModelForCausalLM, AutoTokenizer
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
from datasets import load_dataset
from trl import SFTTrainer
from transformers import AutoTokenizer, AutoModelForCausalLM
from fastapi.responses import JSONResponse
import torch

# get 7b model and tokenizer
model_id = "tiiuae/falcon-7b"
model = AutoModelForCausalLM.from_pretrained(model_id, trust_remote_code=True)
model.config.use_cache = False
tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
tokenizer.pad_token = tokenizer.eos_token

#falcon-40b-instruct model and tokenizer
model_id = "tiiuae/falcon-40b-instruct"
instruct_model = AutoModelForCausalLM.from_pretrained(model_id, trust_remote_code=True)
instruct_tokenizer = AutoTokenizer.from_pretrained(model_id)
instruct_tokenizer.pad_token = instruct_tokenizer.eos_token

# Select cpu for CPU device or cuda for GPU device
device = "cpu"

# instantiate API object
app = FastAPI()

# Define request input object
class GenerateRequest(BaseModel):
    input_text: str
    max_new_tokens: int = 128

# Initialization of the test endpoint
@app.post("/test")
def test(req: GenerateRequest):

    # we go from string to token lists
    inputs = instruct_tokenizer.encode(req.input_text, return_tensors="pt").to(device)

    # query model with inputs
    outputs = instruct_model.generate(
        inputs,
        max_new_tokens=req.max_new_tokens,
        do_sample=True,
        top_k=10,
        num_return_sequences=1,
        eos_token_id=tokenizer.eos_token_id
    )

    # convert tokens back to a string
    text = tokenizer.decode(outputs[0])

    return {"text": text}

# Define finetune request input object with necessary dataset fields
class FinetuneRequest(BaseModel):
    dataset_name: str
    question_column: str
    answer_column: str
    number_elements_for_training: int

# Initialization of the fine-tuning endpoint
@app.post("/finetune")
def finetune(req: FinetuneRequest):

    #load and trim the dataset
    if req.config_name == "":
        dataset = load_dataset(req.dataset_name)
    else:
        dataset = load_dataset(req.dataset_name, req.config_name)
    dataset= dataset['train'].select(range(req.number_elements_for_training))

    num_columns = dataset.num_columns
    column_names = dataset.column_names
    for i in range(num_columns):
        if column_names[i]!=req.question_column and column_names[i]!=req.answer_column:
          dataset = dataset.remove_columns(column_names[i])

    #format the data
    def formatting_prompts_func(example):
        text = f"### Question: {example['question']}\n ### Answer: {example['answer']}"
        return text

    #instantiate the trainer
    if req.question_column!=req.answer_column:
        trainer = SFTTrainer(
            model=model,
            tokenizer=tokenizer,
            train_dataset=dataset,
            dataset_text_field=req.question_column,
            max_seq_length=512,
            formatting_func=formatting_prompts_func,
            packing=True,
        )
    else:
        trainer = SFTTrainer(
            model=model,
            tokenizer=tokenizer,
            train_dataset=dataset,
            dataset_text_field=req.question_column,
            max_seq_length=512,
            packing=True,
        )

    #launch the training
    trainer.train()

    return JSONResponse(content={"text": "The model has successfully been fine-tuned using your dataset"})

# Initialization of the inference endpoint
@app.post("/inference")
def inference(req: GenerateRequest):

    # we go from string to token lists
    inputs = instruct_tokenizer.encode(req.input_text, return_tensors="pt").to(device)

    # query model with inputs
    outputs = model.generate(
        inputs,
        max_new_tokens=req.max_new_tokens,
        do_sample=True,
        top_k=10,
        num_return_sequences=1,
        eos_token_id=tokenizer.eos_token_id
    )

    # convert tokens back to a string
    text = tokenizer.decode(outputs[0])

    return {"text": text}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80)