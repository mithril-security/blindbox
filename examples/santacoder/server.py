from transformers import AutoModelForCausalLM, AutoTokenizer
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

model_name = "bigcode/santacoder"

# get tokenizer
tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)

device = "cpu" # cuda for GPU usage or cpu for CPU usage

# get model and call eval
model = AutoModelForCausalLM.from_pretrained(model_name, trust_remote_code=True).to(device).eval()

# instantiate API object
app = FastAPI()

class GenerateRequest(BaseModel):
    input_text: str
    max_new_tokens: int = 128

@app.post("/generate")
def generate(req: GenerateRequest):

    # We go from string to token lists
    inputs = tokenizer.encode(req.input_text, return_tensors="pt").to(device)
    
    # query model with inputs
    outputs = model.generate(inputs)
    
    # Convert tokens back to a string
    text = tokenizer.decode(outputs[0])

    return {"text": text}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80)
