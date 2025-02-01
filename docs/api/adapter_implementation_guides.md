# Adapter Implementation Guides

## Table of Contents
1. [Introduction](#1-introduction)  
2. [Adapter Fundamentals](#2-adapter-fundamentals)  
3. [Implementing a Pandas Adapter](#3-implementing-a-pandas-adapter)  
   - 3.1. [Key Conventions](#31-key-conventions)  
   - 3.2. [Validation Example](#32-validation-example)  
   - 3.3. [Usage Example](#33-usage-example)  
4. [Implementing a Spark Adapter](#4-implementing-a-spark-adapter)  
   - 4.1. [Key Conventions](#41-key-conventions)  
   - 4.2. [Dealing with Partitions](#42-dealing-with-partitions)  
   - 4.3. [Potential Challenges](#43-potential-challenges)  
5. [Implementing a Domain-Specific Adapter (Example: Genomic Data)](#5-implementing-a-domain-specific-adapter-example-genomic-data)  
   - 5.1. [Identifying Logical Keys](#51-identifying-logical-keys)  
   - 5.2. [Integration with HPC or External Services](#52-integration-with-hpc-or-external-services)  
6. [Testing and Validation](#6-testing-and-validation)  
7. [Performance Considerations](#7-performance-considerations)  
8. [Conclusion](#8-conclusion)  

---

## 1. Introduction

In the **Context-Tracking Framework**, an **adapter** wraps a data structure (like a DataFrame) to provide **uniform methods** for **attaching, retrieving, and removing** metadata (context). This document offers **step-by-step** guides for implementing adapters for:

- **Pandas**: A widely used Python DataFrame library.  
- **Spark**: A distributed DataFrame environment for large-scale data processing.  
- **Domain-Specific** structures (e.g., genomic data, custom classes).

---

## 2. Adapter Fundamentals

All adapters should:

1. **Implement** or **inherit** from the `ContextAwareDataStructure` interface (or a `BaseContextAdapter` if desired).  
2. **Map** user-provided keys to internal parts of the data structure (e.g., columns, rows, partitions).  
3. **Delegate** metadata storage to a chosen **ContextStore** (e.g., `InMemoryContextStore`, `RedisContextStore`, etc.).  
4. **Validate** or **transform** keys as needed to ensure they align with the data structure’s domain.

**Key methods** to implement:

- `add_context(key, metadata)`  
- `get_context(key)`  
- `remove_context(key)`  
- `list_context_keys()`

---

## 3. Implementing a Pandas Adapter

One of the most common data structures is the **`pd.DataFrame`**. Below is a **mini-guide** to implementing a Pandas-based adapter.

### 3.1. Key Conventions

Decide how you will reference **parts** of the DataFrame:

- **Columns**:  
  - A tuple like `("column", column_name)`, where `column_name` is a string.  
- **Row & Column**:  
  - A tuple like `("row", row_index, "column", column_name)`.  
- **Entire DataFrame**:  
  - A simple key like `("df",)`, `"entire_df"`, or any other consistent label.

It’s crucial to **document** these key conventions so that users know how to specify the portion of the DataFrame they want to attach context to.

### 3.2. Validation Example

```python
import pandas as pd
from context_framework.context_store import ContextStore, InMemoryContextStore
from context_framework.exceptions import ContextKeyError
from context_framework.context_aware_data_structure import ContextAwareDataStructure

class PandasContextAdapter(ContextAwareDataStructure):
    def __init__(self, df: pd.DataFrame, context_store: ContextStore = None):
        self.df = df
        self.context_store = context_store or InMemoryContextStore()

    def add_context(self, key, metadata: dict) -> None:
        # Validate key for columns
        if isinstance(key, tuple) and len(key) == 2 and key[0] == "column":
            column_name = key[1]
            if column_name not in self.df.columns:
                raise ContextKeyError(f"Column {column_name} not found in DataFrame.")
        # Additional checks for row-based keys, etc.

        # Delegate to store
        self.context_store.set(key, metadata)

    def get_context(self, key):
        return self.context_store.get(key)

    def remove_context(self, key) -> None:
        self.context_store.delete(key)

    def list_context_keys(self):
        return self.context_store.list_keys()
```

### 3.3. Usage Example

```python
import pandas as pd
from context_framework.adapters.pandas_adapter import PandasContextAdapter

df = pd.DataFrame({
    'GeneSymbol': ['BRCA1', 'TP53', 'EGFR'],
    'Expression': [12.3, 8.4, 9.1]
})

adapter = PandasContextAdapter(df)

# Add context to a column
adapter.add_context(("column", "GeneSymbol"), {
    "source": "CSV import",
    "description": "Gene symbol column"
})

# Retrieve context
metadata = adapter.get_context(("column", "GeneSymbol"))
print(metadata)

# List all keys
print(adapter.list_context_keys())
```

---

## 4. Implementing a Spark Adapter

**Spark DataFrames** are distributed across multiple executors, making them more complex. However, the core principle remains the same.

### 4.1. Key Conventions

Possible key patterns:

- `("column", column_name)` for referencing a column’s metadata across the entire DataFrame.  
- `("partition", partition_id, "column", column_name)` if you need to store context at a partition level.  
- If row-level context is needed, you might store it in a separate index or rely on a unique row identifier—though row-level context in Spark can be tricky due to shuffling.

### 4.2. Dealing with Partitions

In Spark, data is **partitioned**. You might:

- **Store** partition-specific metadata in a separate key:  
  - e.g., `(“partition”, partition_id, “column”, “GeneSymbol”)`.  
- **Aggregate** metadata after processing each partition. Each partition’s executor can call `add_context`, referencing that partition ID.  

**Important**: If multiple executors use the **same** context store (e.g., Redis), concurrency must be managed carefully. You could:

- Use **unique** partition IDs.  
- Potentially lock or use atomic ops if multiple executors write the same key.

### 4.3. Potential Challenges

- **Driver vs. Executors**: The adapter may live on the **driver**. If you need context writes from executors, you might have to pass a reference to the store or an RPC handle.  
- **Serialization**: Spark serializes functions/objects it sends to executors. Ensure the store client is serializable or can be re-initialized on the executor side.

---

## 5. Implementing a Domain-Specific Adapter (Example: Genomic Data)

**Domain-specific** data structures (like a custom `GenomicData` class) often require specialized key conventions or validations.

### 5.1. Identifying Logical Keys

- If your data structure organizes data by **chromosome** and **locus**:  
  - A key could be `(“chromosome”, chr_id, “position”, start:end)`.  
- If your data has named **genes** or **transcripts**:  
  - A key might be `(“gene”, gene_id)`.

### 5.2. Integration with HPC or External Services

- For HPC pipelines, each step might produce partial results for certain **genes** or **chromosomes**—the adapter can store context about how those results were generated.  
- If you fetch external annotations (e.g., from a reference genome database), you can log them as metadata with `add_context`.

**Example** (simplified snippet):

```python
class GenomicDataAdapter(ContextAwareDataStructure):
    def __init__(self, genomic_obj, context_store=None):
        self.genomic_obj = genomic_obj
        self.context_store = context_store or InMemoryContextStore()

    def add_context(self, key, metadata: dict) -> None:
        # Example: Validate ("gene", GENE_ID)
        if isinstance(key, tuple) and key[0] == "gene":
            gene_id = key[1]
            if gene_id not in self.genomic_obj.genes:
                raise ContextKeyError(f"No such gene: {gene_id}")
        self.context_store.set(key, metadata)

    # get_context, remove_context, list_context_keys follow similar patterns
```

---

## 6. Testing and Validation

Regardless of **which** adapter you implement:

1. **Unit Tests**:  
   - Test each method (`add_context`, `get_context`, `remove_context`, `list_context_keys`) with valid and invalid keys.  
   - Ensure the correct exceptions (`ContextKeyError`, etc.) are raised.

2. **Integration Tests**:  
   - Use real data structures (like a DataFrame or custom object) to verify the adapter’s logic.  
   - Consider concurrency tests if multiple threads/processes share the same adapter/store.

3. **Performance Benchmarks** (if relevant):  
   - For large DataFrames or HPC usage, measure overhead of frequently calling context methods.

---

## 7. Performance Considerations

- **Batch Operations**: If you need to add context for many keys at once, you might benefit from store-level bulk operations (if available).  
- **Key Serialization**: For large or complex keys (e.g., nested tuples), ensure this does not become a bottleneck.  
- **Minimal Validation**: Overly complex key validation can slow down repeated calls. Strive for a balance between validation accuracy and speed.

---

## 8. Conclusion

By following these **mini-guides**, you can create adapters for:

- **Pandas**: The simplest and most direct example, using tuples like `("column", column_name)`.  
- **Spark**: Requires more care around **distributed** usage and concurrency.  
- **Domain-Specific** data structures: The adapter design remains the same—just tailor **key conventions** and **validation** to your domain.

With a well-implemented adapter, the rest of the **Context-Tracking Framework** (including the chosen **ContextStore**) seamlessly provides **metadata management** and **provenance tracking** for your data structure, no matter how large or specialized it may be.

**End of `adapter_implementation_guides.md`**