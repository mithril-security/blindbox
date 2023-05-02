from requests import Session, exceptions
import warnings
from urllib.parse import urljoin

class BlindBoxDebugModeWarning(Warning):
    pass

class SecuredSession(Session):
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
            raise exceptions.MissingSchema(
                "Missing URL for the Secured Session instance"
            )

        self.base_url = addr

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

    def request(self, method, url, *args, **kwargs):
        joined_url = urljoin(self.base_url, url)
        return super().request(method, joined_url, *args, **kwargs)

