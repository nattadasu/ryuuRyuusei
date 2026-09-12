"""
# File Cache Module

In-memory memoization for file-derived data, invalidated by file mtime.

Several hot paths (autocomplete handlers, per-command lookups) re-read and
re-parse the same TSV/CSV/JSON files on every invocation. This module caches
the parsed result in memory and only re-runs the loader when the file's
mtime changes (or when an optional ``max_age`` TTL elapses).

Notes:
    * Loaders run synchronously; keep them fast and free of network I/O.
    * The bot is single-threaded asyncio, so plain dict operations here
      need no locking.
    * Cached entries hold references to the parsed data for the process
      lifetime (until invalidated). Only cache data that is small or
      frequently reused.

Example:
    >>> from modules.filecache import cached_file
    >>> def _load_ids() -> list[int]:
    ...     with open("database/mal.csv", encoding="utf-8") as f:
    ...         return [int(line.split("\\t")[0]) for line in f]
    >>> ids = cached_file("database/mal.csv", _load_ids)
"""

import os
import time
from collections.abc import Callable
from typing import Any, TypeVar

T = TypeVar("T")

_entries: dict[str, tuple[float, float, Any]] = {}
"""path -> (mtime, load_time, data)"""


def cached_file(
    path: str,
    loader: Callable[[], T],
    max_age: float | None = None,
) -> T:
    """
    Return memoized ``loader()`` result for ``path``.

    Args:
        path (str): Path of the source file. Its mtime invalidates the entry.
        loader (Callable[[], T]): Zero-argument callable producing the data.
            Called on cache miss (missing/changed file, expired TTL) and its
            result is memoized.
        max_age (float | None, optional): Maximum age in seconds of a memoized
            entry before it is recomputed even if the file is unchanged.
            Defaults to None (mtime alone governs freshness).

    Returns:
        T: The memoized loader result.

    Raises:
        FileNotFoundError: If ``path`` does not exist, the stale entry (if
            any) is dropped and ``loader`` is invoked, preserving the
            loader's original error behaviour.

    Example:
        >>> ids = cached_file("database/mal.csv", _load_ids)
    """
    now = time.time()
    try:
        mtime = os.path.getmtime(path)
    except FileNotFoundError:
        _entries.pop(path, None)
        return loader()
    entry = _entries.get(path)
    if entry is not None:
        cached_mtime, load_time, data = entry
        if cached_mtime == mtime and (max_age is None or now - load_time < max_age):
            return data
    data = loader()
    try:
        mtime = os.path.getmtime(path)
    except FileNotFoundError:
        mtime = now
    _entries[path] = (mtime, now, data)
    return data


def drop_cached_file(path: str) -> None:
    """
    Drop the memoized entry for ``path``, if present.

    Args:
        path (str): Path whose memoized entry should be discarded.

    Returns:
        None
    """
    _entries.pop(path, None)


__all__ = ["cached_file", "drop_cached_file"]
