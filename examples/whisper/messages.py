from pydantic import BaseModel


class PredictionMsg(BaseModel):
    input_text: str
