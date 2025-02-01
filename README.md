# Context-Tracking Framework

A **lightweight, extensible** library for **attaching, managing, and retrieving metadata** (context) associated with various data structures (e.g., Pandas DataFrames, Spark DataFrames, domain-specific objects). This framework makes it easy to **log provenance, transformation details, and user annotations**—and is particularly beneficial for large-scale or long-running processes where **context** must remain accessible, even if the main data or the calling agent (e.g., an LLM) moves beyond its immediate “memory window.”

## Table of Contents
1. [Overview](#1-overview)  
2. [Key Features](#2-key-features)  
3. [Why Context Tracking?](#3-why-context-tracking)  
   - 3.1. [LLM-Friendly Context Management](#31-llm-friendly-context-management)  
   - 3.2. [Data Provenance & Auditing](#32-data-provenance--auditing)  
   - 3.3. [Modular & Extensible](#33-modular--extensible)  
4. [Core Concepts](#4-core-concepts)  
   - 4.1. [Context Store](#41-context-store)  
   - 4.2. [Context-Aware Adapters](#42-context-aware-adapters)  
   - 4.3. [Metadata / Context Keys](#43-metadata--context-keys)  
5. [Installation](#5-installation)  
6. [Basic Usage](#6-basic-usage)  
7. [Advanced Use Cases](#7-advanced-use-cases)  
   - 7.1. [LLM Integration for Long-Running Analyses](#71-llm-integration-for-long-running-analyses)  
   - 7.2. [Row-Level or Partition-Level Context](#72-row-level-or-partition-level-context)  
   - 7.3. [HPC or Multi-Process Environments](#73-hpc-or-multi-process-environments)  
8. [Adapters & Store Backends](#8-adapters--store-backends)  
9. [Contributing](#9-contributing)  
10. [License](#10-license)  
11. [FAQ: Do We Need to Change Anything for LLM Use Cases?](#11-faq-do-we-need-to-change-anything-for-llm-use-cases)

---

## 1. Overview

The **Context-Tracking Framework** makes it possible to tag (or “annotate”) any **portion** of a data structure with **key-value metadata**. This metadata might include:

- **Data provenance**: “Normalized with method X on date Y.”  
- **Transformation logs**: “Aggregated columns A and B into column C.”  
- **User annotations**: “Tag this row as outlier.”  
- **LLM-related context**: “Initial problem statement,” “Intermediate analysis steps,” or even “LLM chain-of-thought metadata (private).”

By **decoupling** this metadata from the data’s actual representation (e.g., a DataFrame in memory, a file on disk), you ensure a **unified** way to store and retrieve context no matter how or where the data is used.

---

## 2. Key Features

1. **Adapter Pattern**: Simple interface (`ContextAwareDataStructure`) for data structures; easy to add new adapters.  
2. **Pluggable Stores**: Choose an **in-memory** store for small tests or a **Redis / database** backend for multi-process or HPC environments.  
3. **Fine-Grained Context**: Annotate entire datasets, columns, rows, or even specific cells.  
4. **LLM Compatibility**: Ideal for large language models that can only hold a limited “context window” in memory; the framework provides an “external memory” of sorts.  
5. **Extensible**: Integrate with advanced HPC tasks, multi-agent orchestrators, or domain-specific data formats.

---

## 3. Why Context Tracking?

### 3.1. LLM-Friendly Context Management

Large Language Models (LLMs) have **limited context windows**, so long-running analyses can cause important details to fall out of scope (“forgetting”). Using this framework, you can:

- **Attach** relevant notes or transformation logs directly to your data or intermediate artifacts.  
- **Allow** the LLM to “call an API” to retrieve any needed context from the metadata store, even if it’s not in its immediate conversation buffer.

Result: The LLM’s “memory” can be **extended** in a structured, queryable manner—crucial for **complex** data workflows or iterative analysis.

### 3.2. Data Provenance & Auditing

For HPC tasks, data pipelines, or compliance scenarios (e.g., healthcare, finance), it’s essential to track:

- **When** data was transformed  
- **Which** algorithm or tool was used  
- **Who** (which user or system) authorized the change

The framework solves this by logging **metadata** at each step—no more confusion over how your data got from point A to point B.

### 3.3. Modular & Extensible

You can:

- **Swap out** the store backend (e.g., from in-memory to Redis) with minimal code changes.  
- **Implement** new adapters for custom data structures (genomic data, domain-specific objects, Spark DataFrames).  
- **Incorporate** the framework into bigger orchestrators or multi-agent systems (like TheraLab).

---

## 4. Core Concepts

### 4.1. Context Store

A **Context Store** is where all metadata is actually **persisted** or retrieved. Examples include:

- **`InMemoryContextStore`** (default, ephemeral)  
- **`RedisContextStore`** (multi-process, persistent, suitable for HPC or distributed tasks)  
- **`DatabaseContextStore`** (SQL or NoSQL)  

Each must implement the `ContextStore` interface:  
- `set(key, value)`  
- `get(key)`  
- `delete(key)`  
- `list_keys()`

### 4.2. Context-Aware Adapters

**Adapters** wrap an underlying data structure (like a Pandas DataFrame) and implement the `ContextAwareDataStructure` interface:

- `add_context(key, metadata)`  
- `get_context(key)`  
- `remove_context(key)`  
- `list_context_keys()`

They interpret **which** key identifies a column, row, or any sub-element. For instance, `(“column”, “GeneSymbol”)` might store context about a specific column.

### 4.3. Metadata / Context Keys

Keys can be:

- **Simple**: a string like `"column_GeneSymbol"`.  
- **Complex**: a tuple `("row", row_index, "column", col_name)`.  
- **Domain-Specific**: `("chromosome", chr_id, "locus", start_end)` for genomic data.

**Metadata** is usually a dictionary, e.g., `{"source": "PubMed", "description": "Normalized gene names"}`.

---

## 5. Installation

1. **Install from PyPI** (if available):
   ```bash
   pip install context-framework
   ```
2. **Local Installation**:
   ```bash
   git clone https://github.com/thera-core/context-framework.git
   cd context-framework
   pip install .
   # or: python setup.py install
   ```

3. **Dependencies**:
   - Python 3.8+  
   - Optional: `redis` or a DB driver if you plan to use external stores.

---

## 6. Basic Usage

Below is a minimal example using **Pandas** and the **in-memory** store:

```python
import pandas as pd
from context_framework.context_store import InMemoryContextStore
from context_framework.adapters.pandas_adapter import PandasContextAdapter

# 1) Create data
df = pd.DataFrame({
    'GeneSymbol': ['BRCA1', 'TP53', 'EGFR'],
    'Expression': [12.3, 8.4, 9.1]
})

# 2) Wrap it with an adapter
store = InMemoryContextStore()
adapter = PandasContextAdapter(df, context_store=store)

# 3) Add context
adapter.add_context(
    ("column", "GeneSymbol"),
    {"source": "tutorial", "notes": "Gene symbol column for demonstration"}
)

# 4) Retrieve context
metadata = adapter.get_context(("column", "GeneSymbol"))
print(metadata)
# -> {'source': 'tutorial', 'notes': 'Gene symbol column for demonstration'}

# 5) List keys
print(adapter.list_context_keys())
# -> [('column', 'GeneSymbol')]
```

---

## 7. Advanced Use Cases

### 7.1. LLM Integration for Long-Running Analyses

When using an **LLM** that can only handle a limited textual context, you can:

1. **Store** relevant data transformations, prompts, or partial “chain-of-thought” logs as metadata on the data structure.  
2. Whenever the LLM needs to recall older context, it calls a **function** or **API** that fetches metadata from the store.  
3. The LLM then merges or references that data as needed to proceed with the analysis.

This approach acts like an **“external memory”** for the LLM, preventing critical details from being “forgotten” in lengthy workflows.

### 7.2. Row-Level or Partition-Level Context

For complex data analysis, you may want:

- **Row-level**: `("row", 42)` or `("row", 42, "column", "GeneSymbol")`.  
- **Partition-level**: In Spark or Dask, each partition could have a unique partition ID. You can store transformations or aggregator logs per partition.

### 7.3. HPC or Multi-Process Environments

- Use a **distributed store** (Redis or a DB).  
- Multiple processes can safely **add**, **retrieve**, or **remove** context concurrently.  
- This is critical in large HPC or cluster-based data analytics pipelines.

---

## 8. Adapters & Store Backends

You’ll find or can create:

- **Adapters**:
  - `PandasContextAdapter` (bundled example)  
  - `SparkContextAdapter` (custom or community)  
  - Domain-specific (e.g., `GenomicDataAdapter`)
- **Store Backends**:
  - `InMemoryContextStore`  
  - `RedisContextStore` (example extension)  
  - `DatabaseContextStore` (example for SQL)

Check the `api/` and `examples/` folders for more details on building or using custom adapters and stores.

---

## 9. Contributing

We welcome contributions!  
1. **Fork** the repo  
2. **Create** a branch (e.g. `feature/my-new-adapter`)  
3. Write tests + docstrings  
4. Open a **pull request**  

Please see [our testing plan](./test/testing_plan.md) and [contributing guidelines](./CONTRIBUTING.md) for more details.

---

## 10. License

This project is licensed under the [MIT License](./LICENSE) (or insert your chosen license here). See the [LICENSE file](./LICENSE) for details.

---

## 11. FAQ: Do We Need to Change Anything for LLM Use Cases?

**Short answer**: *Not necessarily.* The framework’s core design—**attaching metadata** to data structures via **keys** and storing it in a **pluggable store**—already supports LLM usage. The “metadata” can simply be **LLM prompts**, **analysis steps**, or any text needed to reconstruct context. 

- LLMs can “forget” details in their **limited context window**.  
- By using the **Context-Tracking Framework**, you systematically log crucial steps or references.  
- The LLM can then **re-fetch** whichever context it needs by calling a function or API that queries the underlying context store.  

Hence, no fundamental changes are required. The existing architecture—**adapters** plus **context store**—is flexible enough to serve as a “long-term memory” for LLM-based or multi-agent workflows.

If you foresee specialized features (e.g., **semantic retrieval** of context, or **embedding-based** lookups), you could create custom store logic or new modules, but the **core** remains the same.

---

**Happy Context Tracking!**  

If you have questions, file an issue or join the discussion in our community channels.