# Context-Framework: Adapter Design Decisions

## Table of Contents
1. [Introduction](#1-introduction)  
2. [What is an Adapter in this Context?](#2-what-is-an-adapter-in-this-context)  
3. [Core Motivations & Principles](#3-core-motivations--principles)  
4. [Design Trade-Offs](#4-design-trade-offs)  
   - 4.1. [Why Not Just Decorate the Data Structure?](#41-why-not-just-decorate-the-data-structure)  
   - 4.2. [Why Keep the Adapter Interface Small?](#42-why-keep-the-adapter-interface-small)  
   - 4.3. [Granularity of Context Keys](#43-granularity-of-context-keys)  
5. [Adapter Responsibilities](#5-adapter-responsibilities)  
   - 5.1. [Key Interpretation / Validation](#51-key-interpretation--validation)  
   - 5.2. [Delegating to the Context Store](#52-delegating-to-the-context-store)  
   - 5.3. [Maintaining Separation of Concerns](#53-maintaining-separation-of-concerns)  
6. [Common Patterns in Adapter Implementation](#6-common-patterns-in-adapter-implementation)  
   - 6.1. [BaseContextAdapter Abstract Class](#61-basecontextadapter-abstract-class)  
   - 6.2. [Direct Interface Implementation](#62-direct-interface-implementation)  
   - 6.3. [Optional Helper Methods](#63-optional-helper-methods)  
7. [Guidelines for Building New Adapters](#7-guidelines-for-building-new-adapters)  
   - 7.1. [Evaluate Data Structure Semantics](#71-evaluate-data-structure-semantics)  
   - 7.2. [Define Clear Key Conventions](#72-define-clear-key-conventions)  
   - 7.3. [Respect Read/Write Operations](#73-respect-readwrite-operations)  
8. [Example: PandasContextAdapter](#8-example-pandascontextadapter)  
9. [Future Directions & Potential Improvements](#9-future-directions--potential-improvements)  
10. [Conclusion](#10-conclusion)  

---

## 1. Introduction

The **Context-Tracking Framework** uses an **adapter** model to integrate different data structures (e.g., Pandas DataFrames, Spark DataFrames, domain-specific objects) with a **common metadata interface**. This document provides an in-depth look at **why** we chose an adapter-based design, the **trade-offs** we considered, and **how** to create or extend adapters to suit various data structures.

---

## 2. What is an Adapter in this Context?

An **adapter** in our framework is a class that:

1. **Implements** the `ContextAwareDataStructure` interface (or inherits from a base abstract adapter).  
2. **Wraps** a specific data structure (like `pd.DataFrame`).  
3. **Translates** context operations (`add_context`, `get_context`, etc.) into reads/writes to a **Context Store**.

In essence, the adapter is a **bridge** between:
- The user’s data structure (the “real” data)  
- The framework’s **metadata** logic (context store, context keys)

This design enables the framework to remain **agnostic** to the specifics of each data structure while still providing a **uniform** API to attach and retrieve metadata.

---

## 3. Core Motivations & Principles

1. **Consistency**: By standardizing how context is added or fetched across data structures, developers can easily switch from one data type to another.  
2. **Modularity**: Each adapter can be added or removed **without affecting** the rest of the system.  
3. **Simplicity**: We focus on a **small set of methods** (add, get, remove, list) that all adapters must implement—this lowers the barrier to creating new adapters.  
4. **Separation of Concerns**: The adapter handles the logic of mapping “keys” to the underlying data structure, while the **Context Store** handles the actual persistence of metadata.

---

## 4. Design Trade-Offs

### 4.1. Why Not Just Decorate the Data Structure?

An alternative approach could have been to **monkey-patch** or **decorate** a data structure directly (e.g., adding methods to a Pandas DataFrame). However, this raises several issues:

- **Invasive**: Modifying third-party objects can be brittle and may break with library updates.  
- **Namespace Conflicts**: Overriding or injecting methods into existing classes can lead to unexpected collisions.  
- **Testing / Maintenance**: Harder to maintain and reason about, as it ties the library’s internals to the data structure’s internal logic.

Using a separate **adapter** avoids these pitfalls. The data structure remains untouched, and the adapter simply **references** it.

### 4.2. Why Keep the Adapter Interface Small?

We deliberately chose a **minimal** interface—`add_context`, `get_context`, `remove_context`, `list_context_keys`—so the framework:

- **Remains easy to implement** for new data structures (less boilerplate).  
- **Doesn’t become domain-specific** (no built-in “normalize gene column” or “transform time series”).  
- **Keeps the boundary** between context management and data manipulation clear.

### 4.3. Granularity of Context Keys

Adapters must decide **how** to interpret “keys.” For instance, a Pandas adapter could allow:

- Keys like `(“column”, “GeneSymbol”)`  
- Keys like `(“row_index”, 42, “column”, “Expression”)`

A JSON adapter might allow string-based paths like `("/users/0/name")`. The **adapter** is the place to define these conventions, **not** the core framework. This keeps the framework flexible and domain-agnostic.

---

## 5. Adapter Responsibilities

### 5.1. Key Interpretation / Validation

The adapter ensures that **keys** make sense for its data structure. For example:
- **Pandas**: Validate that the column name exists, or the row index is within range.  
- **Spark**: Must handle distributed columns or partition references.  
- **Custom**: Could map keys to domain-specific identifiers (e.g., gene symbols).

### 5.2. Delegating to the Context Store

Once the adapter validates or transforms the key, it simply calls:
- `context_store.set(key, metadata)`  
- `context_store.get(key)`  
- `context_store.delete(key)`

The adapter does **not** need to know how or where data is stored (in-memory, Redis, DB, etc.). It only knows how to **refer** to the correct key.

### 5.3. Maintaining Separation of Concerns

Adapters **must not** handle:
- **Complex transformations** on the data (that’s for separate augmentation libraries).  
- **User interface** or orchestration logic (that’s for higher-level product code).  
- **Security or access control** beyond the basic store-level protections.

By focusing solely on bridging the gap between the data structure’s “key space” and the context store, adapters remain **clean** and **lightweight**.

---

## 6. Common Patterns in Adapter Implementation

### 6.1. BaseContextAdapter Abstract Class

Many adapter implementations share common code—for instance, storing a reference to the `context_store` and providing default implementations for `add_context`, `get_context`, `remove_context`, and `list_context_keys`.

A **BaseContextAdapter** abstract class can:
- **Hold** a protected reference to `context_store`.  
- Provide **basic** implementations for these methods, which child classes override or extend if needed.

This reduces **boilerplate** when creating new adapters.

### 6.2. Direct Interface Implementation

If an adapter’s logic is **highly specialized**, it may choose to **directly implement** `ContextAwareDataStructure`:
```python
class MyCustomAdapter(ContextAwareDataStructure):
    def __init__(self, custom_obj, context_store=None):
        self.custom_obj = custom_obj
        self.context_store = context_store or InMemoryContextStore()

    def add_context(self, key, metadata):
        # Custom logic for validating the key, etc.
        self.context_store.set(key, metadata)

    ...
```
This approach is flexible but can lead to **duplication** if multiple adapters share logic.

### 6.3. Optional Helper Methods

Some adapters define **helper methods** specific to the data structure. For instance, a Pandas adapter might have:
```python
def add_column_level_context(self, column_name, metadata):
    key = ("column", column_name)
    self.add_context(key, metadata)
```
These methods can make **caller code simpler**, but they are **not required** by the framework’s core interface.

---

## 7. Guidelines for Building New Adapters

### 7.1. Evaluate Data Structure Semantics

Ask:
- Does the data structure have a concept of “columns,” “rows,” or “cells”?  
- Does it have hierarchical components (e.g., nested JSON objects)?  
- Are keys typically strings, numeric indices, or structured tuples?

Based on these semantics, define how your adapter interprets **context keys**.

### 7.2. Define Clear Key Conventions

Establish a **consistent** system for key naming. If your data structure is hierarchical, you might adopt path-like keys (e.g., `(“level1”, “level2”, “attribute”)`). Document these conventions in the adapter’s docstrings to reduce confusion.

### 7.3. Respect Read/Write Operations

Ensure that `add_context`, `get_context`, `remove_context`, and `list_context_keys`:
1. Perform **minimal** logic—just enough to map or validate keys.  
2. Delegate the **actual** read/write to the `ContextStore`.  
3. Handle **exceptions** appropriately (e.g., raise `ContextKeyError` for invalid keys).

---

## 8. Example: PandasContextAdapter

**Quick illustration** of how an adapter can handle a popular data structure (Pandas DataFrame):

- **Key Conventions**: `(“column”, “ColumnName”)`, `(“row”, row_index, “column”, “ColumnName”)`.  
- **Validation**:  
  - Ensure column exists if the key references `(“column”, …)`.  
  - For row-based context, ensure the index is valid.  
- **Delegation**:  
  ```python
  def add_context(self, key, metadata):
      # Validate and transform the key if necessary
      if key[0] == "column" and key[1] not in self.df.columns:
          raise ContextKeyError(f"No such column: {key[1]}")
      self.context_store.set(key, metadata)
  ```

---

## 9. Future Directions & Potential Improvements

1. **Auto-Key Generation**: Some domain-specific adapters might automatically generate keys for each element (e.g., gene symbols in a genomic dataset).  
2. **Immutable Snapshots**: An adapter might maintain versioned references to the data structure for audit trails, though this adds complexity.  
3. **Batch Context Updates**: Particularly for large data structures, providing methods to add metadata for *multiple* keys in a single call could be more efficient.

---

## 10. Conclusion

Adapters are a **cornerstone** of the Context-Tracking Framework’s architecture. They **shield** the core library from the details of any particular data structure and provide a **consistent, minimal** interface for context operations. By following these **design decisions** and **implementation guidelines**, developers can seamlessly integrate new data structures into the framework while maintaining clarity, modularity, and ease of use.

**End of `adapter_design_decisions.md`**