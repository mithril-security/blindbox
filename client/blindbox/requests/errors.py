class AttestationException(Exception):
    """
    A custom exception class for wrapping attestation errors.
    """

    def __init__(self, code, payload=None):
        self.code = code
        self.payload = payload
    def __str__(self):
        return f"{self.code} \n{self.payload}" 