"""
# Prints Module

Shared ``print`` wrapper that defaults to ``flush=True``.

Standard ``print`` buffers stdout when it is not a TTY (pipes, Docker logs,
systemd, CI). This causes logs to appear delayed or out of order. Importing
this ``print`` instead of the builtin makes flushing the default, while still
allowing an explicit ``flush=False`` override.

Example:
    >>> from modules.prints import print
    >>> print("hello")  # flushed immediately
    >>> print("buffered", flush=False)  # opt-out

    To force flushing process-wide without touching every call site (e.g. in
    ``main.py`` entrypoint):
    >>> from modules.prints import enable_auto_flush
    >>> enable_auto_flush()
"""

import builtins
from typing import Any

_builtin_print = builtins.print


def print(*args: Any, flush: bool = True, **kwargs: Any) -> None:  # pylint: disable=redefined-builtin
    """
    Print wrapper with ``flush`` defaulting to ``True``.

    Args:
        *args (Any): Positional arguments forwarded to builtin ``print``.
        flush (bool, optional): Whether to flush stdout. Defaults to True.
        **kwargs (Any): Keyword arguments forwarded to builtin ``print``.

    Returns:
        None

    Example:
        >>> print("hello")
        >>> print("no flush", flush=False)
    """
    kwargs["flush"] = flush
    _builtin_print(*args, **kwargs)


def fprint(*args: Any, flush: bool = True, **kwargs: Any) -> None:
    """
    Alias of :func:`print` for callers that prefer not to shadow the builtin.

    Args:
        *args (Any): Positional arguments forwarded to builtin ``print``.
        flush (bool, optional): Whether to flush stdout. Defaults to True.
        **kwargs (Any): Keyword arguments forwarded to builtin ``print``.

    Returns:
        None
    """
    print(*args, flush=flush, **kwargs)


flush_print = fprint
"""Alias of :func:`fprint`."""


def enable_auto_flush() -> None:
    """
    Patch ``builtins.print`` process-wide so ``flush`` defaults to ``True``.

    Existing explicit ``flush=False`` arguments are still respected. Call this
    once at program startup if you do not want to add
    ``from modules.prints import print`` to every file.

    Returns:
        None

    Example:
        >>> enable_auto_flush()
        >>> print("flushed even without importing modules.prints")
    """
    original_print = builtins.print
    # Avoid double-wrapping if already enabled (or if already our wrapper).
    if getattr(original_print, "__ryuu_auto_flush__", False):
        return

    def _auto_flush_print(*args: Any, flush: bool = True, **kwargs: Any) -> None:
        kwargs["flush"] = flush
        # Use captured original to avoid recursion if enable is called twice
        # via different paths.
        if original_print is print:
            _builtin_print(*args, **kwargs)
        else:
            original_print(*args, **kwargs)

    _auto_flush_print.__ryuu_auto_flush__ = True  # type: ignore[attr-defined]
    builtins.print = _auto_flush_print  # type: ignore[assignment]


def disable_auto_flush() -> None:
    """
    Restore ``builtins.print`` to the original (buffered) behaviour.

    Only undoes :func:`enable_auto_flush`. Files using
    ``from modules.prints import print`` are unaffected.

    Returns:
        None
    """
    if getattr(builtins.print, "__ryuu_auto_flush__", False):
        # If the wrapper captured a custom original, prefer it; otherwise
        # fall back to the pristine builtin captured at import time.
        builtins.print = _builtin_print


__all__ = [
    "disable_auto_flush",
    "enable_auto_flush",
    "flush_print",
    "fprint",
    "print",
]
