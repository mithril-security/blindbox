from .secure_session import SecureSession
from urllib.parse import urlparse

DEFAULT_ATTESTER = "sharedeus2.eus2.test.attest.azure.net"

def _parse_url(url):
    url_split = urlparse(url)
    root = url_split.scheme + "://" + url_split.netloc
    endpoint = f"{url_split.path}" + (f"?{url_split.query}" if len(url_split.query) > 0 else "")
    return root, endpoint

def post(url, cce_policy, attestation_endpoint=None, data=None, json=None, **kwargs):
    r"""Sends a POST request. Returns :class:`Response` object.
    :param url: URL for the new :class:`Request` object.
    :param cce_policy: path to file containing cce policy (base64 encoded)
    :param attestation_endpoint: (optional) attestation service uri
    :param data: (optional) Dictionary, list of tuples, bytes, or file-like
         object to send in the body of the :class:`Request`.
    :param json: (optional) json to send in the body of the :class:`Request`.
    :param \*\*kwargs: Optional arguments that ``request`` takes.
    :rtype: requests.Response
    """

    root, endpoint = _parse_url(url)
    attestation_endpoint = attestation_endpoint or DEFAULT_ATTESTER
    with SecureSession(root,cce_policy,attestation_endpoint) as secure_session:
        return secure_session.post(endpoint, data, json, **kwargs)


def get(url, cce_policy, attestation_endpoint=None, **kwargs):
    r"""Sends a GET request. Returns :class:`Response` object.
    :param url: URL for the new :class:`Request` object.
    :param cce_policy: path to file containing cce policy (base64 encoded)
    :param attestation_endpoint: (optional) attestation service uri
    :param \*\*kwargs: Optional arguments that ``request`` takes.
    :rtype: requests.Response
    """
    
    root, endpoint = _parse_url(url)
    attestation_endpoint = attestation_endpoint or DEFAULT_ATTESTER
    with SecureSession(root,cce_policy,attestation_endpoint) as secure_session:
        return secure_session.get(endpoint, **kwargs)
    

def options(url, cce_policy, attestation_endpoint=None, **kwargs):
    r"""Sends a OPTIONS request. Returns :class:`Response` object.
    :param url: URL for the new :class:`Request` object.
    :param cce_policy: path to file containing cce policy (base64 encoded)
    :param attestation_endpoint: (optional) attestation service uri
    :param \*\*kwargs: Optional arguments that ``request`` takes.
    :rtype: requests.Response
    """

    root, endpoint = _parse_url(url)
    attestation_endpoint = attestation_endpoint or DEFAULT_ATTESTER
    with SecureSession(root,cce_policy,attestation_endpoint) as secure_session:
        return secure_session.options(endpoint, **kwargs)


def head(url, cce_policy, attestation_endpoint=None, **kwargs):
    r"""Sends a HEAD request. Returns :class:`Response` object.
    :param url: URL for the new :class:`Request` object.
    :param cce_policy: path to file containing cce policy (base64 encoded)
    :param attestation_endpoint: (optional) attestation service uri
    :param \*\*kwargs: Optional arguments that ``request`` takes.
    :rtype: requests.Response
    """

    root, endpoint = _parse_url(url)
    attestation_endpoint = attestation_endpoint or DEFAULT_ATTESTER
    with SecureSession(root,cce_policy,attestation_endpoint) as secure_session:
        return secure_session.head(endpoint, **kwargs)
    
def put(url, cce_policy, attestation_endpoint=None, data=None, **kwargs):
    r"""Sends a PUT request. Returns :class:`Response` object.
    :param url: URL for the new :class:`Request` object.
    :param cce_policy: path to file containing cce policy (base64 encoded)
    :param attestation_endpoint: (optional) attestation service uri
    :param data: (optional) Dictionary, list of tuples, bytes, or file-like
        object to send in the body of the :class:`Request`.
    :param \*\*kwargs: Optional arguments that ``request`` takes.
    :rtype: requests.Response
    """

    root, endpoint = _parse_url(url)
    attestation_endpoint = attestation_endpoint or DEFAULT_ATTESTER
    with SecureSession(root,cce_policy,attestation_endpoint) as secure_session:
        return secure_session.put(endpoint, data=data, **kwargs)
    
def patch(url, cce_policy, attestation_endpoint=None, data=None, **kwargs):
    r"""Sends a PATCH request. Returns :class:`Response` object.
    :param url: URL for the new :class:`Request` object.
    :param cce_policy: path to file containing cce policy (base64 encoded)
    :param attestation_endpoint: (optional) attestation service uri
    :param data: (optional) Dictionary, list of tuples, bytes, or file-like
        object to send in the body of the :class:`Request`.
    :param \*\*kwargs: Optional arguments that ``request`` takes.
    :rtype: requests.Response
    """

    root, endpoint = _parse_url(url)
    attestation_endpoint = attestation_endpoint or DEFAULT_ATTESTER
    with SecureSession(root,cce_policy,attestation_endpoint) as secure_session:
        return secure_session.patch(endpoint, data=data, **kwargs)
    
def delete(url, cce_policy, attestation_endpoint=None, **kwargs):
    r"""Sends a DELETE request. Returns :class:`Response` object.
    :param url: URL for the new :class:`Request` object.
    :param cce_policy: path to file containing cce policy (base64 encoded)
    :param attestation_endpoint: (optional) attestation service uri
    :param \*\*kwargs: Optional arguments that ``request`` takes.
    :rtype: requests.Response
    """

    root, endpoint = _parse_url(url)
    attestation_endpoint = attestation_endpoint or DEFAULT_ATTESTER
    with SecureSession(root,cce_policy,attestation_endpoint) as secure_session:
        return secure_session.delete(endpoint, **kwargs)