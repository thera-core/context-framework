# Context-Aware Data Structure API Reference

## Overview

In the **Context-Tracking Framework**, the `ContextAwareDataStructure` interface defines the fundamental operations required to **attach, retrieve, and remove** context (i.e., metadata) from various data structures. This API reference provides details on:

- The **`ContextAwareDataStructure`** interface methods and usage  
- The **`BaseContextAdapter`** abstract class (if used)  
- Basic examples and signatures for each method

The goal is to provide a **consistent** contract for all adapters—regardless of the underlying data structure—so that the rest of the framework (e.g., the **context store** and higher-level orchestrators) can manage metadata in a **uniform** way.

---

## 1. `ContextAwareDataStructure` Interface

```python
class ContextAwareDataStructure(Protocol):
    """
    Defines the interface for a data structure that can store and retrieve context (metadata).
    """

    def add_context(self, key: Any, metadata: dict) -> None:
        """
        Store context/metadata for a specific key.

        :param key: 
            The identifier used to reference a portion of the data structure. 
            Could be a string, tuple, or any hashable object that uniquely identifies 
            rows, columns, or other elements of the data structure.
        :param metadata: 
            A dictionary containing metadata to associate with 'key'. 
            This metadata can include transformation provenance, annotations, 
            notes, or any relevant context.

        :raises ContextStoreError:
            If the underlying context store is unavailable or fails to write.
        :raises ContextKeyError:
            If the key is invalid or conflicts with the data structure's constraints.
        :return: None
        """

    def get_context(self, key: Any) -> Optional[dict]:
        """
        Retrieve the metadata associated with a specific key.

        :param key: 
            The identifier for which context data is requested.
        :return:
            A dictionary of metadata if the key exists, or None if the key has no context.
        :raises ContextStoreError:
            If the underlying context store is unavailable or fails to read.
        :raises ContextKeyError:
            If the key is invalid (adapter-specific).
        """

    def remove_context(self, key: Any) -> None:
        """
        Remove the metadata associated with a specific key.

        :param key:
            The identifier for which context data is to be removed.
        :raises ContextStoreError:
            If the underlying context store fails to remove the data.
        :raises ContextKeyError:
            If the key does not exist or is invalid.
        :return: None
        """

    def list_context_keys(self) -> List[Any]:
        """
        List all keys for which context metadata is currently stored.

        :return:
            A list of keys that have metadata in the underlying context store.
        :raises ContextStoreError:
            If the underlying context store fails to read.
        """

```

### Key Points

1. **Key Parameter**:  
   - Represents the portion of the data structure to which the metadata applies.  
   - Could be `(“column”, col_name)`, `(“row”, row_index, “column”, col_name)`, or any custom structure defined by the adapter.

2. **Metadata**:  
   - A dictionary containing arbitrary key-value pairs.  
   - The **framework** does not impose strict requirements on metadata content—it can hold any JSON-serializable structure (e.g., strings, numbers, lists).

3. **Exceptions**:
   - **`ContextStoreError`**: Thrown if the underlying storage layer encounters an error (e.g., lost DB connection).  
   - **`ContextKeyError`**: Thrown if the key is invalid for the adapter’s domain or not found (depending on the operation).

---

## 2. `BaseContextAdapter` (Abstract Class)

Many implementations may choose to derive from an optional **`BaseContextAdapter`** class that implements the `ContextAwareDataStructure` interface. This abstract class is **not** strictly required, but it can reduce boilerplate by:

- Storing a reference to a **`ContextStore`**  
- Providing default method implementations that simply **delegate** to the store

Below is a **sample** structure; actual code may differ slightly:

```python
from abc import ABC, abstractmethod
from typing import Any, Optional, List
from context_framework.context_store import ContextStore, InMemoryContextStore
from context_framework.exceptions import ContextStoreError, ContextKeyError

class BaseContextAdapter(ABC):
    """
    Optional abstract adapter that implements core delegation to a ContextStore.
    Subclasses can override methods to add data-structure-specific logic or validation.
    """

    def __init__(self, context_store: Optional[ContextStore] = None):
        self.context_store = context_store or InMemoryContextStore()

    def add_context(self, key: Any, metadata: dict) -> None:
        # Subclasses may validate or transform the key before storing
        self.context_store.set(key, metadata)

    def get_context(self, key: Any) -> Optional[dict]:
        return self.context_store.get(key)

    def remove_context(self, key: Any) -> None:
        self.context_store.delete(key)

    def list_context_keys(self) -> List[Any]:
        return self.context_store.list_keys()

    @abstractmethod
    def validate_key(self, key: Any) -> None:
        """
        Optional method for subclasses to enforce domain-specific rules on keys.
        Raise ContextKeyError if the key is invalid.
        """
        pass
```

### Usage

- **Subclasses** (e.g., `PandasContextAdapter`) can override any of the base methods to add data-structure-specific logic:
  ```python
  class PandasContextAdapter(BaseContextAdapter):
      def __init__(self, df: pd.DataFrame, context_store: Optional[ContextStore] = None):
          super().__init__(context_store)
          self.df = df

      def add_context(self, key: Any, metadata: dict) -> None:
          # Validate the key, e.g., check if column exists
          if isinstance(key, tuple) and key[0] == "column":
              column_name = key[1]
              if column_name not in self.df.columns:
                  raise ContextKeyError(f"Column {column_name} not found.")
          super().add_context(key, metadata)
  ```

---

## 3. Method-by-Method Reference

### `add_context(key: Any, metadata: dict) -> None`

**Description**: Stores metadata for a given key.

1. **Parameters**  
   - `key`: A hashable identifier for part of the data.  
   - `metadata`: A dict with the context data.

2. **Behavior**  
   - Adapter may validate the key (check if a column exists, etc.).  
   - If valid, the adapter delegates to its underlying `ContextStore`.  
   - If invalid, the adapter should raise `ContextKeyError`.

3. **Returns**  
   - `None` if successful.  
   - Could raise `ContextStoreError` for storage errors or `ContextKeyError` for invalid keys.

### `get_context(key: Any) -> Optional[dict]`

**Description**: Retrieves metadata for a given key.

1. **Parameters**  
   - `key`: The identifier whose metadata is requested.

2. **Behavior**  
   - Adapter may do partial validation.  
   - Delegates to `ContextStore.get(key)`.  
   - If no metadata is found, returns `None` (or raises an exception, depending on the store’s design).

3. **Returns**  
   - A dictionary with the metadata if present, otherwise `None`.

### `remove_context(key: Any) -> None`

**Description**: Deletes metadata associated with a given key.

1. **Parameters**  
   - `key`: The identifier whose metadata is to be removed.

2. **Behavior**  
   - Adapter may validate the key.  
   - Calls `ContextStore.delete(key)` to remove from the store.

3. **Returns**  
   - `None` if removal succeeds.  
   - Raises `ContextStoreError` if the store operation fails.  
   - May raise `ContextKeyError` if the key does not exist (adapter-specific choice).

### `list_context_keys() -> List[Any]`

**Description**: Enumerates all keys in the context store that currently have metadata.

1. **Parameters**  
   - None.

2. **Behavior**  
   - Returns a list of keys. The store must track all keys internally.  
   - Useful for debugging or auditing which parts of the data structure have context.

3. **Returns**  
   - A list of keys (`List[Any]`).  
   - Could raise `ContextStoreError` if the store fails to retrieve the key listing.

---

## 4. Example Usage

```python
from context_framework.adapters.pandas_adapter import PandasContextAdapter
from context_framework.context_store import InMemoryContextStore
import pandas as pd

# 1. Create a Pandas DataFrame
df = pd.DataFrame({
    'GeneSymbol': ['BRCA1', 'TP53', 'EGFR'],
    'Expression': [12.3, 8.4, 9.1]
})

# 2. Instantiate an adapter with an in-memory store
store = InMemoryContextStore()
adapter = PandasContextAdapter(df, context_store=store)

# 3. Add context to a column
adapter.add_context(('column', 'GeneSymbol'), {
    'source': 'CSV file',
    'description': 'Gene symbol column loaded from external dataset'
})

# 4. Retrieve context
context_data = adapter.get_context(('column', 'GeneSymbol'))
print(context_data)
# Output: {'source': 'CSV file', 'description': 'Gene symbol column loaded from external dataset'}

# 5. Remove context
adapter.remove_context(('column', 'GeneSymbol'))

# 6. Verify removal
print(adapter.get_context(('column', 'GeneSymbol')))  # None
```

---

## 5. Summary of Responsibilities

- **Adapters**:  
  - Validate or transform keys specific to their data structure.  
  - Delegate metadata operations to a chosen `ContextStore`.  
  - Raise errors if the key is invalid or the store operation fails.

- **Context Store**:  
  - Handle the actual persistence or retrieval of metadata.  
  - Remain oblivious to the data structure’s internal logic or domain specifics.

---

## 6. Best Practices

1. **Keep Adapters Simple**: Avoid adding domain-specific logic (like transformations) in the adapter—only do what's necessary for **key validation** and **delegation**.  
2. **Document Key Conventions**: For instance, if you allow `(“column”, col_name)` or `(“row”, row_idx)`, note this clearly in your adapter docstrings.  
3. **Handle Exceptions Carefully**: Decide whether your adapter returns `None` or raises a `ContextKeyError` when a key doesn’t exist. Consistency across your codebase is crucial.  
4. **Minimize Overhead**: If you frequently add context, consider **batching** or using more efficient store methods (if supported).  
5. **Thread-Safety**: If your environment is multithreaded, ensure the chosen `ContextStore` is thread-safe or use synchronization primitives as needed.

---

## 7. Conclusion

The **`ContextAwareDataStructure`** interface (along with optional **`BaseContextAdapter`**) is the **foundation** of the Context-Tracking Framework’s design. By adhering to these APIs and conventions, developers can create **powerful, flexible** adapters that integrate metadata tracking into any data structure—allowing for consistent, transparent **context management** across diverse use cases.

**End of `context_aware_data_structure_api.md`**