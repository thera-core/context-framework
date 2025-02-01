"""
in_memory_context_store.py

Provides a simple in-memory implementation of the ContextStore interface.
Suitable for small-scale usage, testing, or local development. Not recommended
for multi-process concurrency or production environments with high availability
requirements.
"""

from typing import Any, Dict, Optional, List
from .context_store import ContextStore
from .exceptions import ContextStoreError

class InMemoryContextStore:
    """
    An in-memory dictionary-based implementation of the ContextStore. Stores key-value
    pairs in a local Python dict.
    """

    def __init__(self) -> None:
        """
        Initialize the in-memory store with an empty dictionary.
        """
        self._store: Dict[Any, Dict[str, Any]] = {}

    def set(self, key: Any, value: Dict[str, Any]) -> None:
        """
        Store 'value' under 'key'. Overwrites any existing entry for 'key'.

        :param key: The hashable identifier to store context data for.
        :param value: The dictionary of metadata to store.
        :raises ContextStoreError: (Rarely) if memory issues occur, or if usage is invalid.
        """
        # In practice, there's minimal risk of a "store error" in memory,
        # but we keep the try-except structure for consistency.
        try:
            self._store[key] = value
        except Exception as ex:
            raise ContextStoreError(f"Failed to set key {key}: {ex}")

    def get(self, key: Any) -> Optional[Dict[str, Any]]:
        """
        Retrieve the metadata for 'key' if it exists.

        :param key: The identifier whose metadata we want.
        :return: The context metadata dictionary, or None if not found.
        :raises ContextStoreError: If an unexpected error occurs.
        """
        try:
            return self._store.get(key, None)
        except Exception as ex:
            raise ContextStoreError(f"Failed to get key {key}: {ex}")

    def delete(self, key: Any) -> None:
        """
        Remove the metadata associated with 'key'.

        :param key: The identifier referencing the stored metadata to remove.
        :raises ContextStoreError: If a delete operation fails unexpectedly.
        """
        try:
            if key in self._store:
                del self._store[key]
        except Exception as ex:
            raise ContextStoreError(f"Failed to delete key {key}: {ex}")

    def list_keys(self) -> List[Any]:
        """
        List all keys currently stored in this in-memory dictionary.

        :return: A list of keys that have associated metadata.
        :raises ContextStoreError: If listing fails (unlikely in memory).
        """
        try:
            return list(self._store.keys())
        except Exception as ex:
            raise ContextStoreError(f"Failed to list keys: {ex}")
