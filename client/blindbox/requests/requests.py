from .secured_session import SecuredSession
from urllib.parse import urlparse

def _parse_url(url):
    url_split = urlparse(url)
    root = url_split.scheme + "://" + url_split.netloc
    endpoint = f"{url_split.path}" + (f"?{url_split.query}" if len(url_split.query) > 0 else "")
    return root, endpoint

def post(url, data=None, json=None, **kwargs):
    r"""Sends a POST request. Returns :class:`Response` object.
    :param url: URL for the new :class:`Request` object.
    :param data: (optional) Dictionary, list of tuples, bytes, or file-like
         object to send in the body of the :class:`Request`.
    :param json: (optional) json to send in the body of the :class:`Request`.
    :param \*\*kwargs: Optional arguments that ``request`` takes.
    :rtype: requests.Response
    """

    root, endpoint = _parse_url(url)
    with SecuredSession(root) as secure_session:
        return secure_session.post(endpoint, data, json, **kwargs)


def get(url, **kwargs):
    r"""Sends a GET request. Returns :class:`Response` object.
    :param url: URL for the new :class:`Request` object.
    :param \*\*kwargs: Optional arguments that ``request`` takes.
    :rtype: requests.Response
    """
    
    root, endpoint = _parse_url(url)
    with SecuredSession(root) as secure_session:
        return secure_session.get(endpoint, **kwargs)
    

def options(url, **kwargs):
    r"""Sends a OPTIONS request. Returns :class:`Response` object.
    :param url: URL for the new :class:`Request` object.
    :param \*\*kwargs: Optional arguments that ``request`` takes.
    :rtype: requests.Response
    """

    root, endpoint = _parse_url(url)
    with SecuredSession(root) as secure_session:
        return secure_session.options(endpoint, **kwargs)


def head(url, **kwargs):
    r"""Sends a HEAD request. Returns :class:`Response` object.
    :param url: URL for the new :class:`Request` object.
    :param \*\*kwargs: Optional arguments that ``request`` takes.
    :rtype: requests.Response
    """

    root, endpoint = _parse_url(url)
    with SecuredSession(root) as secure_session:
        return secure_session.head(endpoint, **kwargs)
    
def put(url, data=None, **kwargs):
    r"""Sends a PUT request. Returns :class:`Response` object.
    :param url: URL for the new :class:`Request` object.
    :param data: (optional) Dictionary, list of tuples, bytes, or file-like
        object to send in the body of the :class:`Request`.
    :param \*\*kwargs: Optional arguments that ``request`` takes.
    :rtype: requests.Response
    """

    root, endpoint = _parse_url(url)
    with SecuredSession(root) as secure_session:
        return secure_session.put(endpoint, data=data, **kwargs)
    
def patch(url, data=None, **kwargs):
    r"""Sends a PATCH request. Returns :class:`Response` object.
    :param url: URL for the new :class:`Request` object.
    :param data: (optional) Dictionary, list of tuples, bytes, or file-like
        object to send in the body of the :class:`Request`.
    :param \*\*kwargs: Optional arguments that ``request`` takes.
    :rtype: requests.Response
    """

    root, endpoint = _parse_url(url)
    with SecuredSession(root) as secure_session:
        return secure_session.patch(endpoint, data=data, **kwargs)
    
def delete(url, **kwargs):
    r"""Sends a DELETE request. Returns :class:`Response` object.
    :param url: URL for the new :class:`Request` object.
    :param \*\*kwargs: Optional arguments that ``request`` takes.
    :rtype: requests.Response
    """

    root, endpoint = _parse_url(url)
    with SecuredSession(root) as secure_session:
        return secure_session.delete(endpoint, **kwargs)