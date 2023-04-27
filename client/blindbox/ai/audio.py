from io import BytesIO, BufferedIOBase
from typing import Union, Optional

from .connection import NitroConnection


DEFAULT_API_HOST = "nitro.mithrilsecurity.io"


class Audio:
    @classmethod
    def transcribe(
        cls,
        file: Union[str, bytes],
        connection: Optional[NitroConnection] = None,
    ) -> str:
        """
        Whisper API which converts speech to text based on the model passed.

        Args:
            file: str, bytes
                Audio file to transcribe. It may also receive serialized bytes of wave file.
            connection: Optional[NitroConnection]
                The AWS Nitro Enclave connection object. Defaults to None.
        Returns:
            Dict:
                The transcription object containing, text and the tokens
        """
        buff: BufferedIOBase
        if isinstance(file, str):
            buff = open(file, "rb")
        else:
            buff = BytesIO()
            buff.write(file)
            buff.seek(0)

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
                "/whisper/predict",
                files={
                    "audio": buff,
                },
            )

        return res
