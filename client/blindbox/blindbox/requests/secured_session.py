import requests as rq
import warnings

class BlindBoxDebugModeWarning(Warning):
    pass

class SecuredSession(rq.Session):
    """A class to represent a connection to a BlindBox server."""

    def __init__(
        self,
        addr: str,
        debug_mode: bool = False,
    ):
        """Connect to a BlindBox service.
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
                BlindBoxDebugModeWarning,
            )

        super(SecuredSession, self).__init__()

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
    """Connect to a BlindBox service.
    Args:
        addr (str): The address of the BlindBox service (such as "enclave.com:8443" or "localhost:8443").
        debug_mode (bool): Whether to run in debug mode. This mode is provided
            solely for testing purposes. It MUST NOT be used in production. Defaults to False.
    Returns:
        SecuredSession: A connection to the BlindBox service.
    """
    return SecuredSession(addr, debug_mode)
