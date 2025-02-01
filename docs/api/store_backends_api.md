# Context Store Backends API Reference

## Table of Contents
1. [Introduction](#1-introduction)  
2. [ContextStore Interface](#2-contextstore-interface)  
   - 2.1. [Required Methods](#21-required-methods)  
3. [Common Context Store Implementations](#3-common-context-store-implementations)  
   - 3.1. [InMemoryContextStore](#31-inmemorycontextstore)  
   - 3.2. [RedisContextStore (Example Extension)](#32-rediscontextstore-example-extension)  
   - 3.3. [DatabaseContextStore (Example Extension)](#33-databasecontextstore-example-extension)  
4. [Usage & Instantiation](#4-usage--instantiation)  
5. [Configuration & Connection Parameters](#5-configuration--connection-parameters)  
6. [Concurrency & Thread Safety](#6-concurrency--thread-safety)  
7. [Error Handling & Exceptions](#7-error-handling--exceptions)  
8. [Extending with New Store Backends](#8-extending-with-new-store-backends)  
   - 8.1. [Sharding or Partitioning](#81-sharding-or-partitioning)  
   - 8.2. [Batch / Bulk Operations](#82-batch--bulk-operations)  
9. [Example Usage](#9-example-usage)  
10. [Best Practices](#10-best-practices)  
11. [Conclusion](#11-conclusion)  

---

## 1. Introduction

The **Context Store** is a core building block of the Context-Tracking Framework. It defines *how* and *where* metadata (context) is persisted. By default, the framework provides an **in-memory store** suitable for small-scale or local usage. However, for more robust or distributed setups, developers can create **custom store backends** (e.g., Redis, SQL, NoSQL).

This document explains the **ContextStore** interface, describes its **required methods**, and illustrates **common backend** implementations.

---

## 2. ContextStore Interface

All store backends must implement the **`ContextStore`** interface. It typically resides in a file like `context_store.py` within the framework. Although the exact syntax may vary (e.g., using Python’s `Protocol` or a base class), each store must provide the following methods.

### 2.1. Required Methods

```python
class ContextStore(Protocol):
    """
    Defines the interface for storing and retrieving context metadata.
    """

    def set(self, key: Any, value: dict) -> None:
        """
        Persist the given 'value' under 'key'.
        If 'key' already exists, overwrite it.

        :param key:
            A hashable identifier for the context entry.
        :param value:
            A dictionary containing context metadata.
        :raises ContextStoreError:
            If the store fails to write the data (e.g., network error, DB failure).
        """

    def get(self, key: Any) -> Optional[dict]:
        """
        Retrieve the context metadata stored under 'key'.

        :param key:
            A hashable identifier for the context entry.
        :return:
            The dictionary stored under 'key', or None if not found.
        :raises ContextStoreError:
            If the store fails to read the data.
        """

    def delete(self, key: Any) -> None:
        """
        Remove the context metadata associated with 'key'.

        :param key:
            The identifier to remove.
        :raises ContextStoreError:
            If the store fails to delete the data.
        """

    def list_keys(self) -> List[Any]:
        """
        Retrieve all keys that have associated metadata in the store.

        :return:
            A list of keys.
        :raises ContextStoreError:
            If the store fails to read the data.
        """
```

**Key Points**:

1. **Atomic Operations**: Each method should either succeed in its entirety or fail with a `ContextStoreError`.  
2. **No Domain Logic**: The store doesn’t interpret the meaning of the keys or values—it only stores them.  
3. **Thread Safety**: Implementation detail depends on your use case (see [Concurrency & Thread Safety](#6-concurrency--thread-safety)).

---

## 3. Common Context Store Implementations

### 3.1. InMemoryContextStore

**File**: `in_memory_context_store.py`

**Purpose**: A simple in-memory key-value mapping using a Python dictionary. Ideal for small demos, unit tests, or single-process usage.

```python
class InMemoryContextStore(ContextStore):
    def __init__(self) -> None:
        self._store: Dict[Any, dict] = {}

    def set(self, key: Any, value: dict) -> None:
        self._store[key] = value

    def get(self, key: Any) -> Optional[dict]:
        return self._store.get(key, None)

    def delete(self, key: Any) -> None:
        if key in self._store:
            del self._store[key]

    def list_keys(self) -> List[Any]:
        return list(self._store.keys())
```

**Pros**:
- Very simple to implement and use  
- No external dependencies

**Cons**:
- Not suitable for multi-process usage (data not shared across processes)  
- Data is lost if the process ends or restarts

---

### 3.2. RedisContextStore (Example Extension)

**File**: `redis_context_store.py` (hypothetical extension)

**Purpose**: Persists keys in a Redis database, allowing distributed or multi-process usage.

```python
import redis
from typing import Any, Optional, List
from context_framework.exceptions import ContextStoreError

class RedisContextStore(ContextStore):
    def __init__(self, host: str, port: int, db: int = 0):
        try:
            self._client = redis.Redis(host=host, port=port, db=db)
        except redis.RedisError as e:
            raise ContextStoreError(f"Failed to connect to Redis: {str(e)}")

    def set(self, key: Any, value: dict) -> None:
        try:
            # Redis typically stores bytes, so we might need to serialize
            # e.g., using JSON or pickle:
            self._client.set(key, json.dumps(value))
        except redis.RedisError as e:
            raise ContextStoreError(f"Redis set operation failed: {str(e)}")

    def get(self, key: Any) -> Optional[dict]:
        try:
            data = self._client.get(key)
            if data is None:
                return None
            return json.loads(data)
        except redis.RedisError as e:
            raise ContextStoreError(f"Redis get operation failed: {str(e)}")

    def delete(self, key: Any) -> None:
        try:
            self._client.delete(key)
        except redis.RedisError as e:
            raise ContextStoreError(f"Redis delete operation failed: {str(e)}")

    def list_keys(self) -> List[Any]:
        try:
            # Redis does not have a direct command for listing all keys in a large production system.
            # "KEYS *" might be sufficient for dev or small-scale.
            keys = self._client.keys('*')
            return [key.decode('utf-8') for key in keys]
        except redis.RedisError as e:
            raise ContextStoreError(f"Redis list_keys operation failed: {str(e)}")
```

**Pros**:
- Allows multiple processes or machines to share context data  
- Supports advanced features like clustering, replication

**Cons**:
- Requires running a Redis server  
- Potential overhead in serializing/deserializing JSON for each operation

---

### 3.3. DatabaseContextStore (Example Extension)

**File**: `database_context_store.py` (hypothetical extension)

**Purpose**: Stores context in a relational or NoSQL database table, supporting robust queries, persistence, and concurrency.

```python
import sqlite3
from context_framework.exceptions import ContextStoreError

class DatabaseContextStore(ContextStore):
    def __init__(self, db_path: str = "context.db"):
        # Example with SQLite for demo; can adapt to Postgres, MySQL, etc.
        self.connection = sqlite3.connect(db_path)
        self._init_table()

    def _init_table(self):
        cursor = self.connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS context_store (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)
        self.connection.commit()

    def set(self, key: Any, value: dict) -> None:
        try:
            serialized = json.dumps(value)
            cursor = self.connection.cursor()
            cursor.execute("REPLACE INTO context_store (key, value) VALUES (?, ?)", (str(key), serialized))
            self.connection.commit()
        except Exception as e:
            raise ContextStoreError(f"Database set failed: {str(e)}")

    def get(self, key: Any) -> Optional[dict]:
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT value FROM context_store WHERE key = ?", (str(key),))
            row = cursor.fetchone()
            if row is None:
                return None
            return json.loads(row[0])
        except Exception as e:
            raise ContextStoreError(f"Database get failed: {str(e)}")

    def delete(self, key: Any) -> None:
        try:
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM context_store WHERE key = ?", (str(key),))
            self.connection.commit()
        except Exception as e:
            raise ContextStoreError(f"Database delete failed: {str(e)}")

    def list_keys(self) -> List[Any]:
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT key FROM context_store")
            rows = cursor.fetchall()
            return [row[0] for row in rows]
        except Exception as e:
            raise ContextStoreError(f"Database list_keys failed: {str(e)}")
```

**Pros**:
- Data is persistently stored  
- Mature transaction support, concurrency controls

**Cons**:
- Performance overhead compared to in-memory or Redis  
- Requires schema management, connection handling

---

## 4. Usage & Instantiation

**Context Stores** are typically instantiated in user code or passed into an **adapter**:

```python
# Using the in-memory store
from context_framework.context_store import InMemoryContextStore
store = InMemoryContextStore()

# Using the hypothetical Redis store
store = RedisContextStore(host="localhost", port=6379)

# Using the hypothetical Database store
store = DatabaseContextStore(db_path="/var/data/context.db")
```

An **adapter** (e.g., `PandasContextAdapter`) can then be constructed with the chosen store:

```python
adapter = PandasContextAdapter(df, context_store=store)
```

---

## 5. Configuration & Connection Parameters

**For distributed or production usage**, store backends may expose additional parameters:

- **Redis**: cluster node addresses, passwords, SSL, timeouts  
- **Databases**: connection URLs, credentials, pool sizing, transaction levels  

Configuration can be **hard-coded** or **supplied** via environment variables, config files, or a DI (dependency injection) framework.

---

## 6. Concurrency & Thread Safety

- **InMemoryContextStore**: Basic Python dict operations are atomic under the GIL for single-threaded writes, but not for **multi-process** concurrency.  
- **Redis**: Thread-safe when using a single Redis client instance, but watch out for pipeline or transaction nuances.  
- **Databases**: May require transaction isolation or row-level locking to handle concurrent writes.

**Recommendation**: Use a store that **naturally supports multi-process concurrency** (e.g., Redis, DB) if your environment is distributed. Locking or synchronization may be needed to ensure consistency if multiple adapters share the same store.

---

## 7. Error Handling & Exceptions

All **Context Store** methods can raise a **`ContextStoreError`** for failures (network errors, DB write failures, etc.). Other possible errors:

- **`ContextKeyError`** is usually raised by adapters (for invalid keys) rather than by the store.  
- **Driver/Library-Specific Exceptions**: Wrap or convert them to `ContextStoreError` to maintain a consistent interface.

---

## 8. Extending with New Store Backends

### 8.1. Sharding or Partitioning

For extremely large datasets, you may need to shard the context store across multiple backends or nodes:
- Create a **ShardManager** that routes `set/get/delete` calls to different store instances based on hashing the key.  
- Each shard implements the `ContextStore` interface but stores only a subset of keys.

### 8.2. Batch / Bulk Operations

Some HPC or high-throughput scenarios might benefit from **bulk** additions or deletions of context data. You can extend `ContextStore` with optional methods (e.g., `set_many`, `delete_many`) for performance. Adapters can then use these if they detect large batches of context updates.

---

## 9. Example Usage

```python
from context_framework.context_store import InMemoryContextStore
from context_framework.adapters.pandas_adapter import PandasContextAdapter
import pandas as pd

# 1. Create a store backend
store = InMemoryContextStore()

# 2. Wrap your data structure with an adapter, providing the store
df = pd.DataFrame({
    'ColumnA': [1, 2, 3],
    'ColumnB': [4, 5, 6],
})
adapter = PandasContextAdapter(df, context_store=store)

# 3. Add or retrieve context
adapter.add_context(('column', 'ColumnA'), {'desc': 'Integer values'})
print(adapter.get_context(('column', 'ColumnA')))  # => {'desc': 'Integer values'}

# 4. Inspect store contents directly (not typical, just for debugging)
print(store.list_keys())  # => [('column', 'ColumnA')]
```

---

## 10. Best Practices

1. **Choose a Store Based on Use Case**:  
   - Small scale or local dev → **InMemoryContextStore**  
   - Production or multi-process → **RedisContextStore** or **DatabaseContextStore**

2. **Connection Pooling**:  
   - For DB or Redis in high-throughput scenarios, use a **connection pool** to avoid overhead in establishing connections repeatedly.

3. **Serialization**:  
   - If storing complex metadata, ensure a consistent format (JSON, Pickle).  
   - Watch for performance or security implications (e.g., use JSON for better portability vs. Pickle for faster writes).

4. **Error Handling**:  
   - Always catch driver-specific exceptions and re-raise them as `ContextStoreError`.

5. **Performance Monitoring**:  
   - In HPC or large-scale environments, monitor store performance (latency, CPU/memory usage).  
   - Add caching or local shards if needed.

---

## 11. Conclusion

The **Context Store** abstraction is critical for **flexibility** and **scalability** in the Context-Tracking Framework. By adhering to the **`ContextStore`** interface, developers can **swap** or **add** new backends (in-memory, Redis, SQL, etc.) without impacting adapters or higher-level logic. Understanding each store’s **strengths** and **limitations**—especially around concurrency, persistence, and performance—is key to building **robust context-aware** applications.

**End of `store_backends_api.md`**