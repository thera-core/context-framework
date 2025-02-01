# 1. `quick_start_tutorial.md`

## Quick Start Tutorial

### Overview

This tutorial walks you through the **basic steps** of using the Context-Tracking Framework with a **Pandas** data structure, demonstrating how to:

1. **Install / Set Up** the framework  
2. **Create** an instance of the **in-memory context store**  
3. **Wrap** a Pandas DataFrame with a context-aware adapter  
4. **Add**, **retrieve**, and **remove** metadata  
5. **List all** context keys for auditing

By the end, you’ll understand **how** and **why** to attach metadata to a data structure, and how to **extend** these concepts to more advanced scenarios.

---

### 1. Installation & Setup

1. **Clone or Install** the `context-framework` repository (assuming local or a package manager).  
2. Ensure you have **Python 3.8+** and a **virtual environment** set up (optional but recommended).  
3. Install **dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

> **Note**: If the library is published on PyPI, you could run:  
> ```bash
> pip install context-framework
> ```

---

### 2. Creating a Simple Data Structure

For this tutorial, we’ll use **Pandas**. Install Pandas if you haven’t:

```bash
pip install pandas
```

```python
import pandas as pd

# Sample DataFrame
df = pd.DataFrame({
    'GeneSymbol': ['BRCA1', 'TP53', 'EGFR'],
    'Expression': [12.3, 8.4, 9.1]
})
```

---

### 3. Wrapping the DataFrame with an Adapter

```python
from context_framework.context_store import InMemoryContextStore
from context_framework.adapters.pandas_adapter import PandasContextAdapter

# Create an in-memory store and adapter
store = InMemoryContextStore()
adapter = PandasContextAdapter(df, context_store=store)
```

- `InMemoryContextStore` will store metadata in a simple Python dictionary (ephemeral).  
- `PandasContextAdapter` is a context-aware wrapper around the `df`.

---

### 4. Adding Context Metadata

You can **attach** metadata to any portion of the DataFrame. Let’s attach a simple dictionary to the `GeneSymbol` column:

```python
adapter.add_context(
    ("column", "GeneSymbol"),
    {"source": "tutorial", "notes": "Gene symbol column for demonstration"}
)
```

**Explanation**:  
- The **key** `(“column”, “GeneSymbol”)` indicates that we’re storing metadata for a specific column.  
- The **metadata** dictionary can hold any information (provenance, transformations, etc.).

---

### 5. Retrieving Metadata

```python
col_metadata = adapter.get_context(("column", "GeneSymbol"))
print("Retrieved Metadata:", col_metadata)
```

Expected output might be:

```
Retrieved Metadata: {'source': 'tutorial', 'notes': 'Gene symbol column for demonstration'}
```

---

### 6. Listing All Keys

Sometimes you need to **audit** or **inspect** what context has been stored:

```python
all_keys = adapter.list_context_keys()
print("All context keys:", all_keys)
```

Expected output:

```
All context keys: [('column', 'GeneSymbol')]
```

---

### 7. Removing Context

If you no longer need the metadata for a certain key:

```python
adapter.remove_context(("column", "GeneSymbol"))

# Confirm removal
print("After removal:", adapter.get_context(("column", "GeneSymbol")))
# Should print 'None'
```

---

### 8. Summary & Next Steps

You’ve successfully **created** an adapter, **attached** metadata, and performed **basic** context operations. Next steps might include:

- Using a **Redis** or **Database** store for persistence.  
- Defining **custom adapters** for your own data structures.  
- Integrating the framework into a **larger** multi-agent or HPC pipeline.

---

**End of `quick_start_tutorial.md`**