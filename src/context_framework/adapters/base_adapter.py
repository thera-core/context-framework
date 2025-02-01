"""
base_adapter.py

Provides an optional abstract base class that implements common adapter logic
(adding, retrieving, removing context) by delegating to a ContextStore.
Subclasses can override or extend methods to handle data-structure-specific
validations or key transformations.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List
from context_framework.context_store import ContextStore
from context_framework.in_memory_context_store import InMemoryContextStore
from context_framework.exceptions import ContextStoreError, ContextKeyError
from context_framework.context_aware_data_structure import ContextAwareDataStructure

class BaseContextAdapter(ABC, ContextAwareDataStructure):
    """
    An optional base adapter that delegates storage to a ContextStore.
    Subclasses can customize key validation or domain logic.
    """

    def __init__(self, context_store: Optional[ContextStore] = None) -> None:
        """
        :param context_store:
            The storage backend that implements set/get/delete/list_keys.
            Defaults to InMemoryContextStore if none is provided.
        """
        self.context_store = context_store or InMemoryContextStore()

    @abstractmethod
    def validate_key(self, key: Any) -> None:
        """
        Subclasses should override this method to raise ContextKeyError if
        the key does not conform to the data structure's domain.
        """
        pass

    def add_context(self, key: Any, metadata: Dict[str, Any]) -> None:
        """
        Store metadata for 'key', after validating the key.
        """
        self.validate_key(key)
        try:
            self.context_store.set(key, metadata)
        except ContextStoreError as ex:
            raise ex  # re-raise the store error

    def get_context(self, key: Any) -> Optional[Dict[str, Any]]:
        """
        Retrieve metadata associated with 'key', after validating the key.
        """
        self.validate_key(key)
        try:
            return self.context_store.get(key)
        except ContextStoreError as ex:
            raise ex

    def remove_context(self, key: Any) -> None:
        """
        Remove metadata associated with 'key'.
        """
        self.validate_key(key)
        try:
            self.context_store.delete(key)
        except ContextStoreError as ex:
            raise ex

    def list_context_keys(self) -> List[Any]:
        """
        Return all known keys from the underlying context store.
        """
        try:
            return self.context_store.list_keys()
        except ContextStoreError as ex:
            raise ex
