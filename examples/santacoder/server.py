from transformers import AutoModelForCausalLM, AutoTokenizer
from fastapi import FastAPI
from pydantic import BaseModel
import intel_extension_for_pytorch as ipex  # optional: optimize for cpu inference
import uvicorn

model_name = "bigcode/santacoder"
# get tokenizer
tokenizer = AutoTokenizer.from_pretrained(model_name)
device = "cuda" # for GPU usage or cpu for CPU usage

# get model and call eval
model = AutoModelForCausalLM.from_pretrained(model_name).eval()

# optional: optimize for cpu inference
model = ipex.optimize(model)


class GenerateRequest(BaseModel):
    input_text: str
    max_new_tokens: int = 128


app = FastAPI()


@app.post("/generate")
def generate(req: GenerateRequest):

    # We go from string to token lists
    inputs = tokenizer(req.input_text, return_tensors="pt").to(device)

    outputs = model.generate(inputs)

    # Convert tokens back to a string
    text = tokenizer.decode(outputs[0])

    return {"text": text}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80)