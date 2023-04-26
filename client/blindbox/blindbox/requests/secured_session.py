import requests as rq

import warnings


class NitroDebugModeWarning(Warning):
    pass


class SecuredSession(rq.Session):
    """A class to represent a connection to a BlindBox server."""

    def __init__(
        self,
        addr: str,
        debug_mode: bool,
    ):
        """Connect to a BlindBox service hosted on a Nitro enclave.
        Please refer to the connect function for documentation.
        Args:
            addr (str):
            debug_mode (bool):
        Returns:
        """

        if addr == None or addr == "":
            raise rq.exceptions.MissingSchema(
                "Missing URL for the Secured Session instance"
            )

        self.addr = addr

        if debug_mode:
            warnings.warn(
                (
                    "BlindBox is running in debug mode. "
                    "This mode is provided solely for testing purposes. "
                    "It MUST NOT be used in production."
                ),
                NitroDebugModeWarning,
            )

        # s = rq.Session()
        # # Always raise an exception when HTTP returns an error code for the unattested connection
        # # Note : we might want to do the same for the attested connection ?

        # # TODO: Remove verify=False for production
        # s.hooks = {"response": lambda r, *args, **kwargs: r.raise_for_status()}
        # self.attestation_doc = s.get(
        #     f"{self.addr }/enclave/attestation", verify=False
        # ).content
        # self.cert = s.get(f"{self.addr }/enclave/cert", verify=False).content

        # # TODO: Set expected_pcr0 for production
        # if debug_mode:
        #     expected_pcr0 = 48 * b"\x00"
        # try:
        #     validate_attestation(
        #         attestation_doc, expected_pcr0=expected_pcr0, enclave_cert=cert
        #     )
        # except NitroAttestationError:
        #     raise
        # except Exception:
        #     raise NitroAttestationError("Attestation verification failed")

        # # rq (http library) takes a path to a file containing the CA
        # # there is no easy way to give the CA as a string/bytes directly
        # # therefore a temporary file with the certificate content
        # # has to be created.

        # cert_file = tempfile.NamedTemporaryFile(mode="wb")
        # cert_file.write(cert_der_to_pem(cert))
        # cert_file.flush()

        # # the file should not be close until the end of BlindAiConnection
        # # so we store it in the object (else it might get garbage collected)
        # self._cert_file = cert_file

        super(SecuredSession, self).__init__()
        # attested_conn = self
        # attested_conn.verify = cert_file.name

        # # This adapter makes it possible to connect
        # # to the server via a different hostname
        # # that the one included in the certificate i.e. blindai-srv
        # # For instance we can use it to connect to the server via the
        # # domain / IP provided to connect(). See below
        # from rq.adapters import HTTPAdapter

        # class CustomHostNameCheckingAdapter(HTTPAdapter):
        #     def cert_verify(self, conn, url, verify, cert):
        #         conn.assert_hostname = "example.com"
        #         return super(CustomHostNameCheckingAdapter, self).cert_verify(
        #             conn, url, verify, cert
        #         )

        # attested_conn.mount(self._addr, CustomHostNameCheckingAdapter())
        # attested_conn.hooks = {
        #     "response": lambda r, *args, **kwargs: r.raise_for_status()
        # }
        # try:
        #     attested_conn.get(f"{self._addr}/enclave").content
        # except Exception as e:
        #     raise NitroAttestationError(
        #         "Cannot establish secure connection to the enclave"
        #     )

    def get(self, endpoint: str = "", **kwargs):
        r"""Sends a GET request. Returns :class:`Response` object.

        :param endpoint: URL endpoint for the new :class:`Request` object.
        :param \*\*kwargs: Optional arguments that ``request`` takes.
        :rtype: requests.Response
        """

        kwargs.setdefault("allow_redirects", True)
        return self.request("GET", self.addr + endpoint, **kwargs)

    def options(self, endpoint: str = None, **kwargs):
        r"""Sends a OPTIONS request. Returns :class:`Response` object.

        :param url: URL endpoint for the new :class:`Request` object.
        :param \*\*kwargs: Optional arguments that ``request`` takes.
        :rtype: requests.Response
        """

        kwargs.setdefault("allow_redirects", True)
        return self.request("OPTIONS", self.addr + endpoint, **kwargs)

    def head(self, endpoint: str = "", **kwargs):
        r"""Sends a HEAD request. Returns :class:`Response` object.

        :param url endpoint: URL for the new :class:`Request` object.
        :param \*\*kwargs: Optional arguments that ``request`` takes.
        :rtype: requests.Response
        """

        kwargs.setdefault("allow_redirects", False)
        return self.request("HEAD", self.addr + endpoint, **kwargs)

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
            "POST", self.addr + endpoint, data=data, json=json, **kwargs
        )

    def put(self, endpoint: str = "", data=None, **kwargs):
        r"""Sends a PUT request. Returns :class:`Response` object.

        :param url: URL endpoint for the new :class:`Request` object.
        :param data: (optional) Dictionary, list of tuples, bytes, or file-like
            object to send in the body of the :class:`Request`.
        :param \*\*kwargs: Optional arguments that ``request`` takes.
        :rtype: requests.Response
        """

        return self.request("PUT", self.addr + endpoint, data=data, **kwargs)

    def patch(self, endpoint: str = "", data=None, **kwargs):
        r"""Sends a PATCH request. Returns :class:`Response` object.

        :param url: URL endpoint for the new :class:`Request` object.
        :param data: (optional) Dictionary, list of tuples, bytes, or file-like
            object to send in the body of the :class:`Request`.
        :param \*\*kwargs: Optional arguments that ``request`` takes.
        :rtype: requests.Response
        """

        return self.request("PATCH", self.addr + endpoint, data=data, **kwargs)

    def delete(self, endpoint: str = "", **kwargs):
        r"""Sends a DELETE request. Returns :class:`Response` object.

        :param url endpoint: URL for the new :class:`Request` object.
        :param \*\*kwargs: Optional arguments that ``request`` takes.
        :rtype: requests.Response
        """

        return self.request("DELETE", self.addr + endpoint, **kwargs)


def connect(addr: str, debug_mode: bool = False) -> SecuredSession:
    """Connect to a BlindBox service hosted on a Nitro enclave.
    Args:
        addr (str): The address of the BlindBox service (such as "enclave.com:8443" or "localhost:8443").
        debug_mode (bool): Whether to run in debug mode. This mode is provided
            solely for testing purposes. It MUST NOT be used in production. Defaults to False.
    Returns:
        SecuredSession: A connection to the BlindBox service.
    """
    return SecuredSession(addr, debug_mode)
