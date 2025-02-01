"""
context_store.py

Defines the ContextStore Protocol, which represents a storage layer for
persisting context metadata. All store backends (in-memory, Redis, DB) must
implement these methods.
"""

from typing import Protocol, Any, Dict, Optional, List
from .exceptions import ContextStoreError

class ContextStore(Protocol):
    """
    A protocol defining how metadata is persisted and retrieved in the
    Context-Tracking Framework. Each method can raise ContextStoreError on failure.
    """

    def set(self, key: Any, value: Dict[str, Any]) -> None:
        """
        Persist a metadata dictionary under 'key'. Overwrite if key exists.

        :param key:
            A hashable identifier for the context entry.
        :param value:
            A dictionary containing context metadata.
        :raises ContextStoreError:
            If the store cannot write the data (network, disk, or DB error).
        """
        ...

    def get(self, key: Any) -> Optional[Dict[str, Any]]:
        """
        Retrieve the metadata stored under 'key'.

        :param key:
            A hashable identifier for the context entry.
        :return:
            The stored dictionary, or None if not found.
        :raises ContextStoreError:
            If the store fails to read data.
        """
        ...

    def delete(self, key: Any) -> None:
        """
        Remove the metadata associated with 'key'.

        :param key:
            The identifier for which we want to remove metadata.
        :raises ContextStoreError:
            If the store fails to delete the data.
        """
        ...

    def list_keys(self) -> List[Any]:
        """
        Return all keys that currently have metadata in this store.

        :return:
            A list of keys.
        :raises ContextStoreError:
            If the store fails to list keys.
        """
        ...
