import typing as t
import importlib

class OptionalDependencyNotAvailable(Exception):
    """Error class for signalling an optional dependency was not found."""
    def __init__(self, unavailable: t.List[str]) -> None:
        super().__init__(f"The following pip dependencies must be installed in order to use this blindbox feature: {', '.join(unavailable)}")
        self._unavailable = unavailable


def assert_dependency_available(modules: t.List[str]):
    """Throw an exception if a given optional dependency is not installed."""

    unavailable = None
    for mod in modules:
        try:
            importlib.import_module(mod)
        except ImportError as e:
            if unavailable is None: unavailable = []
            unavailable.append(mod)

    if unavailable is not None:
        raise OptionalDependencyNotAvailable(unavailable)

__all__ = ["OptionalDependencyNotAvailable", "assert_dependency_available"]
