"""Small utility to lazily import heavy modules with caching & background prefetch."""

from __future__ import annotations

import importlib
import threading
import types
from typing import Any, Dict, Optional, Iterable, Callable

__all__ = [
    "lazy_import",
    "prefetch_modules",
    "is_available",
    "import_optional",
    "get_cached",
    "get_import_error",
]

_CACHE: Dict[str, Any] = {}
_ERRORS: Dict[str, str] = {}
_LOCK = threading.RLock()


def _import(name: str) -> Any:
    with _LOCK:
        if name in _CACHE:
            return _CACHE[name]
        if name in _ERRORS:
            raise ImportError(_ERRORS[name])
        try:
            mod = importlib.import_module(name)
            _CACHE[name] = mod
            return mod
        except Exception as e:  # noqa: broad-except
            _ERRORS[name] = str(e)
            raise


def get_cached(name: str) -> Optional[Any]:
    with _LOCK:
        return _CACHE.get(name)


def get_import_error(name: str) -> Optional[str]:
    with _LOCK:
        return _ERRORS.get(name)


def is_available(name: str) -> bool:
    try:
        _import(name)
        return True
    except Exception:  # noqa: broad-except
        return False


class _LazyModule(types.ModuleType):
    def __init__(self, module_name: str):
        super().__init__(module_name)
        self._module_name = module_name
        self._real: Any = None

    def _load(self):
        if self._real is None:
            self._real = _import(self._module_name)
        return self._real

    def __getattr__(self, item):
        return getattr(self._load(), item)

    def __repr__(self):  # pragma: no cover
        return f"<_LazyModule {self._module_name} loaded={self._real is not None}>"


class _LazyAttr:
    def __init__(self, module_name: str, attr: str):
        self._module_name = module_name
        self._attr = attr
        self._obj: Any = None

    def _load(self):
        if self._obj is None:
            mod = _import(self._module_name)
            self._obj = getattr(mod, self._attr)
        return self._obj

    def __getattr__(self, item):
        return getattr(self._load(), item)

    def __call__(self, *a, **kw):
        return self._load()(*a, **kw)

    def __repr__(self):  # pragma: no cover
        return f"<_LazyAttr {self._module_name}:{self._attr} loaded={self._obj is not None}>"


def lazy_import(spec: str):
    if ":" in spec:
        m, a = spec.split(":", 1)
        return _LazyAttr(m.strip(), a.strip())
    return _LazyModule(spec.strip())


def import_optional(spec: str):
    try:
        if ":" in spec:
            m, a = spec.split(":", 1)
            return getattr(_import(m.strip()), a.strip())
        return _import(spec)
    except Exception:  # noqa: broad-except
        return None


def prefetch_modules(modules: Iterable[str], callback: Optional[Callable[[str, bool, Optional[str]], None]] = None, daemon: bool = True):
    def worker():
        for name in modules:
            try:
                _import(name)
                if callback:
                    callback(name, True, None)
            except Exception as e:  # noqa: broad-except
                if callback:
                    callback(name, False, str(e))

    t = threading.Thread(target=worker, name="lazy_prefetch", daemon=daemon)
    t.start()
    return t
