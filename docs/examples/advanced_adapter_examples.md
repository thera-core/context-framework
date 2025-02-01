# 2. `advanced_adapter_examples.md`

## Advanced Adapter Examples

### Introduction

This document showcases **more complex** adapters and usage patterns, including:

1. **Row-level** context in Pandas  
2. **Partition-level** context in Spark or Dask  
3. **Domain-specific** keys for specialized data structures (e.g., genomic data)

These examples build on the **basic** usage from the quick start tutorial but demonstrate how to handle **additional complexity** in real-world scenarios.

---

## 1. Row-Level Context in Pandas

Sometimes you need to associate metadata with **specific rows** or even individual cells. Below is a snippet that extends `PandasContextAdapter` to handle row-level keys:

```python
class PandasRowContextAdapter(PandasContextAdapter):
    def add_context(self, key, metadata: dict) -> None:
        """
        key format for row-level context: ("row", row_index, "column", column_name)
        """
        if isinstance(key, tuple) and key[0] == "row":
            row_idx = key[1]
            col_name = key[3] if len(key) > 3 else None
            if col_name and col_name not in self.df.columns:
                raise ContextKeyError(f"Column {col_name} not found.")
            if row_idx not in self.df.index:
                raise ContextKeyError(f"Row index {row_idx} not found.")
        super().add_context(key, metadata)

# Usage:
row_adapter = PandasRowContextAdapter(df)
row_adapter.add_context(("row", 0, "column", "GeneSymbol"), {"verified": True})
```

---

## 2. Partition-Level Context in Spark

**Apache Spark** partitions large DataFrames across multiple executors. Below is a **theoretical** Spark adapter:

```python
from pyspark.sql import DataFrame as SparkDataFrame
from context_framework.context_store import ContextStore
from context_framework.context_aware_data_structure import ContextAwareDataStructure

class SparkContextAdapter(ContextAwareDataStructure):
    def __init__(self, spark_df: SparkDataFrame, context_store: ContextStore):
        self.spark_df = spark_df
        self.context_store = context_store

    def add_context(self, key, metadata: dict) -> None:
        """
        Example key: ("partition", partition_id, "column", col_name)
        """
        self.context_store.set(key, metadata)

    def get_context(self, key):
        return self.context_store.get(key)

    def remove_context(self, key):
        self.context_store.delete(key)

    def list_context_keys(self):
        return self.context_store.list_keys()
```

**Partition Identification**:

- You might not have a direct concept of “partition_id.” Instead, you could assign each partition an ID during a Spark job, or rely on Spark’s internal partitioning info.  
- Each executor could call `adapter.add_context(("partition", partition_id, ...), {...})`.

**Consider** concurrency: if multiple executors write to the same store, use a **distributed** store like Redis or a database.

---

## 3. Domain-Specific (Genomic Data) Adapter

Consider a `GenomicData` class that organizes data by **chromosome** and **positions**:

```python
class GenomicData:
    def __init__(self, chromosome_data):
        # dictionary: {chr_id: {"positions": [...], "annotations": [...]}}
        self.data = chromosome_data

class GenomicContextAdapter(ContextAwareDataStructure):
    def __init__(self, genomic_data: GenomicData, context_store: ContextStore):
        self.genomic_data = genomic_data
        self.context_store = context_store

    def add_context(self, key, metadata: dict) -> None:
        # key format: ("chromosome", chr_id, "position_range", (start, end))
        if key[0] == "chromosome":
            chr_id = key[1]
            if chr_id not in self.genomic_data.data:
                raise ContextKeyError(f"Chromosome {chr_id} not found")
        self.context_store.set(key, metadata)

    def get_context(self, key):
        return self.context_store.get(key)

    def remove_context(self, key):
        self.context_store.delete(key)

    def list_context_keys(self):
        return self.context_store.list_keys()
```

This adapter **validates** chromosome IDs before storing metadata, ensuring domain consistency.

---

## 4. Summary

These examples illustrate how to:

- **Extend** or **customize** adapters for row-level, partition-level, or domain-specific metadata tracking.  
- **Validate** keys to ensure they align with the data structure’s domain.  
- **Delegate** actual storage to a `ContextStore`.

With these patterns, you can adapt the **Context-Tracking Framework** to **virtually any** data structure or computational environment.

---

**End of `advanced_adapter_examples.md`**

