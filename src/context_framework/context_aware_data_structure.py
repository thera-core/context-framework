"""
context_aware_data_structure.py

Defines the interface (Protocol) that any "context-aware" data structure adapter
must implement to integrate with the Context-Tracking Framework.
"""

from typing import Protocol, Any, Dict, List, Optional

class ContextAwareDataStructure(Protocol):
    """
    Defines the interface for a data structure that can store and retrieve
    context (metadata). All adapters must conform to these method signatures.
    """

    def add_context(self, key: Any, metadata: Dict[str, Any]) -> None:
        """
        Add metadata for a specific key in the data structure.

        :param key:
            The identifier referencing part of the data structure. Could be
            a string, tuple, or any hashable object that uniquely identifies
            rows, columns, or other sub-elements.
        :param metadata:
            A dictionary containing context data (e.g., provenance, annotations).
        :raises ContextStoreError:
            If the underlying context store fails to write (network, disk, etc.).
        :raises ContextKeyError:
            If the key is invalid for the adapter's domain.
        :return: None
        """
        ...

    def get_context(self, key: Any) -> Optional[Dict[str, Any]]:
        """
        Retrieve the metadata associated with a given key.

        :param key:
            The identifier referencing part of the data structure.
        :return:
            The metadata dictionary, or None if no metadata exists for that key.
        :raises ContextStoreError:
            If the underlying context store fails to read.
        :raises ContextKeyError:
            If the key is invalid or out of domain.
        """
        ...

    def remove_context(self, key: Any) -> None:
        """
        Remove the metadata associated with a given key.

        :param key:
            The identifier referencing part of the data structure.
        :raises ContextStoreError:
            If the underlying context store fails to delete.
        :raises ContextKeyError:
            If the key does not exist or is invalid.
        :return: None
        """
        ...

    def list_context_keys(self) -> List[Any]:
        """
        List all keys for which metadata is currently stored.

        :return:
            A list of keys that have metadata associated in the underlying store.
        :raises ContextStoreError:
            If the underlying context store fails to read keys.
        """
        ...
