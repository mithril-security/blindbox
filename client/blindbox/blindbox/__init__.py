__all__ = []

try:
    from . import ai

    __all__.append("ai")
except ImportError:
    pass
