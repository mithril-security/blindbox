__all__ = []

try:
    from . import requests

    __all__ += ["requests"]
except ImportError:
    pass
