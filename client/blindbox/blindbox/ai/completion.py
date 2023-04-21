from pydantic import BaseModel
from typing import Optional

from .connection import NitroConnection


class PredictionMsg(BaseModel):
    input_text: str


DEFAULT_API_HOST = "nitro.mithrilsecurity.io"


class Completion:
    @classmethod
    def create(
        cls,
        prompt: str,
        connection: Optional[NitroConnection] = None,
    ) -> str:
        prompt = f"<human>: {prompt}\n<bot>: "
        
        if connection is None:
            connection = NitroConnection(
                host=DEFAULT_API_HOST,
                expected_pcr0=None,
                server_fqdn=DEFAULT_API_HOST,
                fingerprint_pinning=True,
            )

        with connection as req:
            res = req.api(
                "post",
                "/open-chat-kit/predict",
                data=PredictionMsg(input_text=prompt).json(),
            )

        return res
