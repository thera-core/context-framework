# Context-Framework: Architecture & Design Specification

## Table of Contents
1. [Introduction](#1-introduction)  
2. [High-Level Overview](#2-high-level-overview)  
3. [Core Components](#3-core-components)  
   - 3.1. [Context-Aware Data Structure Interfaces](#31-context-aware-data-structure-interfaces)  
   - 3.2. [Context Store](#32-context-store)  
   - 3.3. [Adapters](#33-adapters)  
   - 3.4. [Exceptions and Error Handling](#34-exceptions-and-error-handling)  
4. [Data Flow & Interactions](#4-data-flow--interactions)  
   - 4.1. [Storing Context](#41-storing-context)  
   - 4.2. [Retrieving Context](#42-retrieving-context)  
   - 4.3. [Removing or Updating Context](#43-removing-or-updating-context)  
5. [UML Class Diagram (Conceptual)](#5-uml-class-diagram-conceptual)  
6. [Design Patterns and Principles](#6-design-patterns-and-principles)  
   - 6.1. [Adapter Pattern](#61-adapter-pattern)  
   - 6.2. [Interface Segregation](#62-interface-segregation)  
   - 6.3. [Separation of Concerns](#63-separation-of-concerns)  
7. [Extensibility](#7-extensibility)  
   - 7.1. [Adding New Context Stores](#71-adding-new-context-stores)  
   - 7.2. [Creating New Adapters](#72-creating-new-adapters)  
8. [Concurrency & Scalability Considerations](#8-concurrency--scalability-considerations)  
9. [Versioning & Compatibility](#9-versioning--compatibility)  
10. [Example Usage](#10-example-usage)  
11. [Future Enhancements](#11-future-enhancements)  
12. [Conclusion](#12-conclusion)  

---

## 1. Introduction

The **Context-Tracking Framework** is a lightweight library designed to **attach, manage, and retrieve metadata**—collectively referred to as “context”—for various data structures. Its primary objective is to provide a standard interface to track *how* and *why* certain data transformations or annotations were made. This metadata can include:

- Provenance information (e.g., “normalized with method X on date Y”)  
- Annotations (e.g., tags indicating data quality or user-defined labels)  
- Transformation history

**Key Goals**:
- **Lightweight**: Keep minimal dependencies and overhead.  
- **Extensible**: Accommodate new data structures and storage backends easily.  
- **Simple API**: Provide straightforward methods for storing, retrieving, and deleting metadata.  

---

## 2. High-Level Overview

At a high level, the Context-Tracking Framework consists of **two main layers**:

1. **Context Store**: A pluggable mechanism for persisting and retrieving context. By default, an in-memory store is provided.  
2. **Adapters / Interfaces**: An abstraction layer that wraps around data structures to provide standardized methods (`add_context`, `get_context`, etc.).  

The library’s architecture encourages the addition of new **adapters** for different data structure types (e.g., Pandas, Spark DataFrame, domain-specific objects) and new **context stores** (e.g., Redis, SQL databases, file-based) without altering the rest of the framework.

---

## 3. Core Components

### 3.1. Context-Aware Data Structure Interfaces

**`ContextAwareDataStructure`** is the central interface that any adapter must implement to be recognized as “context-aware.” It declares methods such as:
- `add_context(key, metadata)`: Store metadata for a specific key.  
- `get_context(key) -> dict|None`: Retrieve metadata for a specific key.  
- `remove_context(key)`: Delete metadata for a specific key.  
- `list_context_keys() -> List[Any]`: Return all known keys in the store.

**Key Points**:
- **Key Granularity**: A “key” can be anything that logically identifies a portion of the data—e.g., a column name, a tuple `(“row_index”, “col_name”)`, or a fully qualified path.  
- **Metadata Format**: Typically a Python dictionary containing any relevant information.

### 3.2. Context Store

The **Context Store** is an abstraction that defines how metadata is ultimately saved. An implementation must satisfy these minimal operations:
- **`set(key, value)`**  
- **`get(key)`**  
- **`delete(key)`**  
- **`list_keys()`**

#### 3.2.1 InMemoryContextStore
- The default store. Uses an internal dictionary to map `key -> value`.
- **Pros**: Simple, no external dependencies, fast for small/medium data.  
- **Cons**: Not shareable across processes or machines; limited by local memory.

#### 3.2.2 Potential External Stores
- **RedisContextStore** (example extension): Connects to a Redis instance to store metadata for multi-process or multi-machine scenarios.
- **DatabaseContextStore** (example extension): Persists context in a relational or NoSQL database.

### 3.3. Adapters

Adapters are **classes** that wrap a specific data structure (e.g., a Pandas DataFrame) and implement the `ContextAwareDataStructure` interface. They maintain an internal reference to a **Context Store**.

Example: **`PandasContextAdapter`**:
- **Constructor**: Takes a `pd.DataFrame` and an optional `ContextStore`.
- **`add_context(key, metadata)`**: Usually interprets the `key` as `(“column”, column_name)` or `(“row”, row_index, “column”, column_name)`, then delegates storage to the context store.
- **`get_context(key)`**: Looks up the metadata from the context store and returns it.

### 3.4. Exceptions and Error Handling

- **`ContextKeyError`**: Thrown when a requested key does not exist in the store or is invalid.  
- **`ContextStoreError`**: Thrown for general failures in the storage layer, such as connection issues or write errors.  

---

## 4. Data Flow & Interactions

### 4.1. Storing Context

1. **Adapter** (e.g., `PandasContextAdapter`) receives a call `add_context(key, metadata)`.  
2. Adapter may validate the `key` or map it to an internal representation.  
3. Adapter forwards the call to its `ContextStore` instance’s `set()` method, e.g., `set(key, metadata)`.  
4. The store writes the metadata to memory (or external DB).

### 4.2. Retrieving Context

1. **Adapter** receives a call `get_context(key)`.  
2. It invokes the `ContextStore.get(key)`.  
3. The store returns the metadata (or `None` if the key does not exist).  
4. Adapter returns the metadata to the caller.

### 4.3. Removing or Updating Context

- Removing is straightforward: `adapter.remove_context(key)` -> `store.delete(key)`.  
- Updating context typically means calling `adapter.add_context(key, new_metadata)` again; the old metadata is overwritten by the new entry.

---

## 5. UML Class Diagram (Conceptual)

Below is a simplified UML diagram illustrating the main classes and relationships:

```
+-----------------------------------------+
|            ContextAwareDataStructure    |  (Interface)
|-----------------------------------------|
| + add_context(key, metadata)           |
| + get_context(key) -> metadata         |
| + remove_context(key)                  |
| + list_context_keys() -> List[key]     |
+-----------------------------------------+

             implements
                 ^
                 |
+-----------------------------------------+
|           BaseContextAdapter           |  (Abstract / optional helper)
|-----------------------------------------|
| - context_store: ContextStore          |
|-----------------------------------------|
| + constructor(context_store)           |
| + add_context(key, metadata)           |
| + get_context(key)                     |
| + remove_context(key)                  |
| + list_context_keys()                  |
+-----------------------------------------+
                 ^
                 |
                 |
+-----------------------------------------+
|         PandasContextAdapter           |
|-----------------------------------------|
| - df: pd.DataFrame                     |
| - context_store: ContextStore          |
|-----------------------------------------|
| + constructor(df, context_store=None)  |
| + (override or extend if necessary)    |
+-----------------------------------------+

+-----------------------------------------+
|            ContextStore (Interface)    |
|-----------------------------------------|
| + set(key, value)                      |
| + get(key) -> value                    |
| + delete(key)                          |
| + list_keys() -> List[key]             |
+-----------------------------------------+
                 ^
                 |
+-----------------------------------------+
|         InMemoryContextStore           |
|-----------------------------------------|
| - store: dict                          |
|-----------------------------------------|
| + set(key, value)                      |
| + get(key) -> value                    |
| + delete(key)                          |
| + list_keys() -> List[key]             |
+-----------------------------------------+
```

**Notes**:  
- `BaseContextAdapter` is optional but can be used to reduce boilerplate if multiple adapters share the same logic.  
- Each adapter is free to store data structure references (e.g., Pandas DataFrame) in any manner that suits its needs.

---

## 6. Design Patterns and Principles

### 6.1. Adapter Pattern

This framework makes explicit use of the **Adapter Pattern** by creating a uniform interface (`ContextAwareDataStructure`) over varied data structures (Pandas, Spark, domain-specific objects).

### 6.2. Interface Segregation

The **Context Store** and **Context-Aware Data Structure** interfaces are kept small, adhering to the principle of **Interface Segregation**: each interface has a clear, singular responsibility (i.e., storing metadata vs. exposing it to the user).

### 6.3. Separation of Concerns

- The **Context Store** is responsible solely for *how* metadata is persisted.  
- The **Adapter** is responsible for *interpreting the data structure’s context keys* and delegating to the store.  
- **Data transformations** or domain-specific logic are deliberately **excluded** from this library, ensuring minimal coupling.

---

## 7. Extensibility

### 7.1. Adding New Context Stores

To add a new storage mechanism:
1. **Create a class** (e.g., `RedisContextStore`) that implements the `ContextStore` interface.  
2. **Implement the methods**: `set`, `get`, `delete`, and `list_keys`.  
3. **Pass an instance of this store** to any adapter’s constructor. Example:  
   ```python
   store = RedisContextStore(host="localhost", port=6379)
   adapter = PandasContextAdapter(df, context_store=store)
   ```

### 7.2. Creating New Adapters

To support a new data structure type:
1. **Implement the `ContextAwareDataStructure`** methods, or inherit from a base adapter if desired.  
2. **Ensure `add_context`, `get_context`, etc.** map keys in a way that makes sense for the new data structure.  
3. **Maintain a reference** to a `ContextStore` so the metadata is consistently stored.

---

## 8. Concurrency & Scalability Considerations

- **In-Memory Store**: Thread-safety is limited to the Python GIL. For multi-process or distributed usage, the recommended approach is an external store (like Redis) that can handle concurrent writes.  
- **Large Datasets**: Keys can proliferate if you store context for millions of rows. In such scenarios, consider **aggregate context** or external, scalable context stores.  
- **Locking / Atomic Updates**: If needed, external stores can be configured for atomic operations (e.g., Redis transactions or row-level DB locks).

---

## 9. Versioning & Compatibility

- **Semantic Versioning**: The library follows **SemVer** (MAJOR.MINOR.PATCH).  
- **Backward Compatibility**: Breaking changes to the interface or base classes should only occur in a MAJOR version release.  
- **Adapter Independence**: Adapters in separate repositories (or in the `data-augmentation-framework`) must pin a compatible version of the context framework.

---

## 10. Example Usage

```python
from context_framework.context_store import InMemoryContextStore
from context_framework.adapters.pandas_adapter import PandasContextAdapter
import pandas as pd

# 1. Create or load some data
df = pd.DataFrame({
    'GeneSymbol': ['BRCA1', 'TP53', 'EGFR'],
    'Expression': [12.3, 8.4, 9.1]
})

# 2. Instantiate an adapter
store = InMemoryContextStore()
adapter = PandasContextAdapter(df, context_store=store)

# 3. Add context
adapter.add_context(('column', 'GeneSymbol'), {
    'source': 'PubMed',
    'description': 'Gene symbol column loaded from CSV'
})

# 4. Retrieve context
metadata = adapter.get_context(('column', 'GeneSymbol'))
print(metadata)
# Output: {'source': 'PubMed', 'description': 'Gene symbol column loaded from CSV'}

# 5. List all context keys
keys = adapter.list_context_keys()
print(keys)
# Output: [('column', 'GeneSymbol')]

# 6. Remove context
adapter.remove_context(('column', 'GeneSymbol'))
```

---

## 11. Future Enhancements

- **Custom Key Mappers**: Provide a system for more complex key transformations, e.g., mapping row/column to stable identifiers across sessions.  
- **Batch/Transactional Updates**: Some use cases may require grouping multiple context additions/deletions in an atomic operation.  
- **Immutable Context Snapshots**: Ability to capture “point-in-time” context snapshots, useful in compliance or auditing scenarios.  
- **Search Index**: Integrate a text-based index or advanced queries (in external store) to find context by key patterns or metadata content.

---

## 12. Conclusion

The **Context-Tracking Framework** provides a **lightweight, extensible**, and **highly modular** solution for attaching metadata to various data structures. By separating the responsibilities of **context storage** and **context-aware adapters**, the library ensures **ease of integration** and **flexibility** for diverse use cases.

This architecture specification should guide contributors and integrators alike in understanding, maintaining, and extending the framework. Future enhancements can build on the existing interfaces without disrupting the core logic, making the **context-framework** a robust cornerstone for context-aware data workflows.
