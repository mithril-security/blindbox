from requests.adapters import HTTPAdapter, Retry
from urllib3 import poolmanager


class _HostNameCheckingAdapter(HTTPAdapter):
    def __init__(
        self,
        hostname: str,
        pool_connections: int = 10,
        pool_maxsize: int = 10,
        max_retries: Retry | int | None = 0,
        pool_block: bool = False,
    ) -> None:
        super().__init__(pool_connections, pool_maxsize, max_retries, pool_block)
        self.hostname = hostname

    def cert_verify(self, conn, url, verify, cert):
        conn.assert_hostname = self.hostname
        return super(_HostNameCheckingAdapter, self).cert_verify(
            conn, url, verify, cert
        )


class _FingerprintAdapter(HTTPAdapter):
    """
    A HTTPS Adapter for Python Requests that verifies certificate fingerprints,
    instead of certificate hostnames.
    Example usage:
    .. code-block:: python
        import requests
        import ssl
        from requests_toolbelt.adapters.fingerprint import FingerprintAdapter
        twitter_fingerprint = '...'
        s = requests.Session()
        s.mount(
            'https://twitter.com',
            FingerprintAdapter(twitter_fingerprint)
        )
    The fingerprint should be provided as a hexadecimal string, optionally
    containing colons.
    """

    __attrs__ = HTTPAdapter.__attrs__ + ['fingerprint']

    def __init__(self, fingerprint: str, **kwargs):
        self.fingerprint = fingerprint

        super(_FingerprintAdapter, self).__init__(**kwargs)

    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = poolmanager.PoolManager(
            num_pools=connections,
            maxsize=maxsize,
            block=block,
            assert_fingerprint=self.fingerprint)
