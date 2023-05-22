from requests import Session, exceptions
import warnings
from urllib.parse import urljoin
from .errors import *

class BlindBoxDebugModeWarning(Warning):
    pass

class SecureSession(Session):
    """A class to represent a connection to a BlindBox server."""

    def __init__(
        self,
        addr: str,
        cce_file: str = None,
        attestation_endpoint: str = "sharedeus2.eus2.test.attest.azure.net",
        debug_mode: bool = False,
    ):
        """Connect to a BlindBox service.
        Please refer to the connect function for documentation.
        Args:
            addr (str):
            cce_file (str):
            attestation_endpoint (str):
            debug_mode (bool):
        Returns:
        """

        if addr == None or addr == "":
            raise exceptions.MissingSchema(
                "Missing URL for the Secure Session instance"
            )

        self.base_url = addr

        if debug_mode:
            warnings.warn(
                (
                    "BlindBox is running in debug mode. "
                    "This mode is provided solely for testing purposes. "
                    "It MUST NOT be used in production. "
                    "Attestation is bypassed. "
                ),
                BlindBoxDebugModeWarning,
            )

        super(SecureSession, self).__init__()
        
        if not debug_mode:
            if not cce_file:
                raise exceptions.ContentDecodingError("A cce policy needs to be provided when you are not using the debug mode")
            try:
                policy = open(cce_file,"rb")
                policy = policy.read()
            except:
                raise exceptions.ContentDecodingError("Unable to read cce policy")
            self.attestation(policy, attestation_endpoint)

    def get(self, endpoint: str = "", **kwargs):
        r"""Sends a GET request. Returns :class:`Response` object.

        :param endpoint: URL endpoint for the new :class:`Request` object.
        :param \*\*kwargs: Optional arguments that ``request`` takes.
        :rtype: requests.Response
        """

        kwargs.setdefault("allow_redirects", True)
        return self.request("GET", endpoint, **kwargs)

    def options(self, endpoint: str = None, **kwargs):
        r"""Sends a OPTIONS request. Returns :class:`Response` object.

        :param url: URL endpoint for the new :class:`Request` object.
        :param \*\*kwargs: Optional arguments that ``request`` takes.
        :rtype: requests.Response
        """

        kwargs.setdefault("allow_redirects", True)
        return self.request("OPTIONS", endpoint, **kwargs)

    def head(self, endpoint: str = "", **kwargs):
        r"""Sends a HEAD request. Returns :class:`Response` object.

        :param url endpoint: URL for the new :class:`Request` object.
        :param \*\*kwargs: Optional arguments that ``request`` takes.
        :rtype: requests.Response
        """

        kwargs.setdefault("allow_redirects", False)
        return self.request("HEAD", endpoint, **kwargs)

    def post(self, endpoint: str = "", data=None, json=None, **kwargs):
        r"""Sends a POST request. Returns :class:`Response` object.

        :param url endpoint: URL for the new :class:`Request` object.
        :param data: (optional) Dictionary, list of tuples, bytes, or file-like
            object to send in the body of the :class:`Request`.
        :param json: (optional) json to send in the body of the :class:`Request`.
        :param \*\*kwargs: Optional arguments that ``request`` takes.
        :rtype: requests.Response
        """

        return self.request(
            "POST", endpoint, data=data, json=json, **kwargs
        )

    def put(self, endpoint: str = "", data=None, **kwargs):
        r"""Sends a PUT request. Returns :class:`Response` object.

        :param url: URL endpoint for the new :class:`Request` object.
        :param data: (optional) Dictionary, list of tuples, bytes, or file-like
            object to send in the body of the :class:`Request`.
        :param \*\*kwargs: Optional arguments that ``request`` takes.
        :rtype: requests.Response
        """

        return self.request("PUT", endpoint, data=data, **kwargs)

    def patch(self, endpoint: str = "", data=None, **kwargs):
        r"""Sends a PATCH request. Returns :class:`Response` object.

        :param url: URL endpoint for the new :class:`Request` object.
        :param data: (optional) Dictionary, list of tuples, bytes, or file-like
            object to send in the body of the :class:`Request`.
        :param \*\*kwargs: Optional arguments that ``request`` takes.
        :rtype: requests.Response
        """

        return self.request("PATCH", endpoint, data=data, **kwargs)

    def delete(self, endpoint: str = "", **kwargs):
        r"""Sends a DELETE request. Returns :class:`Response` object.

        :param url endpoint: URL for the new :class:`Request` object.
        :param \*\*kwargs: Optional arguments that ``request`` takes.
        :rtype: requests.Response
        """

        return self.request("DELETE", endpoint, **kwargs)

    def request(self, method, endpoint, *args, **kwargs):
        joined_url = urljoin(self.base_url, endpoint)
        return super().request(method, joined_url, *args, **kwargs)

    def attestation(self, policy, attestation_endpoint):
        """
        The attestation is performed as follows:
        1) A nonce is generated.
        2) The attestation API is called on the blindbox and the nonce and attestation service (MAA) endpoint are passed to it.
        3) The response contains an attestation token generated by the Microsoft Azure Attestation Service (MAA).
        4) The token is a JWT which is decoded and validated using certificates from the MAA endpoint.
        5) If the validation of the JWT passes, the attestation report is validated by the MAA.
        6) The values in the attestation report are verified against the expected values. 
        """
        
        import base64
        import hashlib
        import json
        import jwt
        import secrets

        decoded_policy = base64.b64decode(policy)
        h = hashlib.new('sha256')
        h.update(decoded_policy)
        cce_policy = h.hexdigest()

        nonce = {"nonce":secrets.token_hex(16)}
        b64nonce = base64.b64encode(json.dumps(nonce).encode()).decode()

        # Make a request to the attestation service for an MAA token
        attest_url = ":".join(self.base_url.split(":")[:-1])
        res = super().request("POST",f"{attest_url}:8080/attest/maa", json={"maa_endpoint":attestation_endpoint,"runtime_data":b64nonce})
        maa_token = json.loads(res.content)["token"]
        header = maa_token.split(".")[0]

        # Ensure header is appropriate length to be base64 decoded
        if len(header)%4 != 0:
            header += "="*(len(header)%4)

        header = json.loads(base64.b64decode(header))
        kid = header["kid"]
        if header["jku"] != f"https://{attestation_endpoint}/certs":
            raise WrongAttester("Attestation token not generated by expected attester")

        jwt_certs = self.request("GET",header["jku"]).json()

        for iter in jwt_certs["keys"]:
            if iter["kid"] == kid:
                x5c = iter["x5c"][0] #Wrap cert as pem
                x5c = "-----BEGIN CERTIFICATE-----" + x5c + "-----END CERTIFICATE-----"

        from cryptography.x509 import load_pem_x509_certificate

        cert_obj = load_pem_x509_certificate(x5c.encode())
        public_key = cert_obj.public_key()
        
        # Decodes jwt and validates signature and expiry
        payload = jwt.decode(maa_token,public_key,algorithms=["RS256"],)

        # Add further checks for issued at time (iat) and issuer (iss) 
        if payload["x-ms-attestation-type"] != "sevsnpvm":
            raise NotAnEnclaveError("Attestation validation failed (not sev-snp report). Exiting.")
        if payload["x-ms-compliance-status"] != "azure-compliant-uvm":
            raise NonCompliantUvm("Attestation validation failed (non-compliant uvm). Exiting.")
        if payload["x-ms-sevsnpvm-hostdata"] != cce_policy:
            raise InvalidEnclaveCode("Attestation validation failed (cce policy mismatch). Exiting.")
        if payload["x-ms-runtime"] != nonce:
            raise FalseAttestationReport("Attestation validation failed (nonce mismatch). Exiting.")
        if payload["x-ms-sevsnpvm-is-debuggable"] == "false":
            raise DebugMode("Attestation validation failed (enclave is in debug mode). Exiting.")
        
        print("Attestation validated")


def connect(addr: str, cce_file: str, attestation_endpoint: str = "sharedeus2.eus2.test.attest.azure.net", debug_mode: bool = False) -> SecureSession:
    """Connect to a BlindBox service.
    Args:
        addr (str): The address of the BlindBox service (such as "enclave.com:8443" or "localhost:8443").
        cce_file (str): The path to the a file containing the cce_policy (base64 encoded)
        attestation_endpoint (str): The url of the MAA attestation endpoint
        debug_mode (bool): Whether to run in debug mode. This mode is provided
            solely for testing purposes. It MUST NOT be used in production. Attestation is bypassed in this mode.
            Defaults to False.
    Returns:
        SecureSession: A connection to the BlindBox service.
    """
    return SecureSession(addr, cce_file, attestation_endpoint, debug_mode)
