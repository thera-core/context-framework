
# 3. `performance_benchmarks.md`

## Performance & Benchmarking Guide

### Introduction

This document focuses on **performance considerations** for the Context-Tracking Framework. We’ll outline:

- **Benchmark scenarios**: single-process vs. multi-process  
- **Testing** different store backends (in-memory, Redis, database)  
- **Tips** for enhancing throughput and minimizing overhead

---

## 1. Why Benchmark?

Context tracking is often used in **large-scale** data workflows (e.g., HPC, Spark). If your pipeline frequently **adds** or **retrieves** context, store performance can affect the overall throughput. By benchmarking, you can:

1. Identify the **best** store backend for your use case.  
2. Understand **scalability** limits (number of context operations per second, memory usage, etc.).  
3. Optimize or switch to **batch** or **bulk** operations if needed.

---

## 2. Benchmark Setup

1. **Hardware**:  
   - A local machine or a cluster node (e.g., 4-8 CPU cores, SSD, 16+ GB RAM).  
   - For distributed testing, a multi-node environment with a shared or distributed store (Redis cluster, etc.).

2. **Test Framework**:  
   - We recommend Python’s `pytest-benchmark` or a simple custom script with timing logic (using `time` or `timeit`).

3. **Data**:  
   - Use a dataset of moderate size (e.g., a Pandas DataFrame with 100K rows) for local tests.  
   - For HPC / Spark tests, scale up to millions of rows across partitions.

---

## 3. Single-Process Benchmark Example

Below is a **simple** single-process benchmark script that measures **write** and **read** performance for the in-memory store vs. a Redis store:

```python
import time
import pandas as pd
from context_framework.context_store import InMemoryContextStore
from context_framework.adapters.pandas_adapter import PandasContextAdapter
# from my_redis_store import RedisContextStore  # hypothetical

def benchmark_store(adapter, num_ops=10000):
    """
    Measures the time to perform num_ops add_context and get_context calls.
    """
    start = time.time()
    # Add context
    for i in range(num_ops):
        adapter.add_context(("row", i), {"meta": f"value_{i}"})
    mid = time.time()
    # Get context
    for i in range(num_ops):
        adapter.get_context(("row", i))
    end = time.time()

    add_time = mid - start
    get_time = end - mid
    print(f"Add time: {add_time:.4f}s, Get time: {get_time:.4f}s")

if __name__ == "__main__":
    df = pd.DataFrame({"A": range(100000)})  # example data

    # 1. InMemory store
    mem_store = InMemoryContextStore()
    mem_adapter = PandasContextAdapter(df, context_store=mem_store)
    print("Benchmarking InMemoryContextStore...")
    benchmark_store(mem_adapter, num_ops=10000)

    # 2. Redis store (commented out if not available)
    # redis_store = RedisContextStore(host="localhost", port=6379)
    # redis_adapter = PandasContextAdapter(df, context_store=redis_store)
    # print("Benchmarking RedisContextStore...")
    # benchmark_store(redis_adapter, num_ops=10000)
```

**Sample Results** (example, approximate):
```
Benchmarking InMemoryContextStore...
Add time: 0.15s, Get time: 0.10s

Benchmarking RedisContextStore...
Add time: 1.02s, Get time: 0.80s
```

- The in-memory store is faster **locally** because it avoids network and serialization overhead.  
- Redis might be slower in local tests but can scale better in **multi-process** scenarios.

---

## 4. Multi-Process / Distributed Benchmarks

### Spark or Dask

- Configure your Spark job to run on multiple executors.  
- Each executor performs context operations (e.g., per-partition metadata writes).  
- Measure total job time or partial latencies.

### HPC with MPI

- Launch multiple ranks (`mpirun -n 4 python my_script.py`).  
- Each rank tries to write 10K keys.  
- Use a **shared store** (Redis, DB) to measure concurrency overhead.

---

## 5. Tuning & Optimization

1. **Batching Operations**:  
   - If your store supports `set_many` or multi-key pipelines, reduce overhead by grouping multiple writes into one operation.
2. **Reduce Key / Value Size**:  
   - Overly long strings or large metadata dictionaries slow down serialization.  
   - Use short keys or hashed keys if possible.
3. **Connection Pooling**:  
   - For Redis / DB, re-use connections instead of creating new ones for each operation.
4. **Local Caching**:  
   - If reads are frequent, consider an in-process cache. Sync the cache with the store periodically or on certain triggers.

---

## 6. Example Results & Interpretation

| Store                | Num Ops (Add+Get) | Time (Seconds) | Ops/Second Approx |
|----------------------|-------------------|----------------|-------------------|
| InMemoryContextStore | 10,000           | 0.25           | 40,000 ops/sec    |
| RedisContextStore    | 10,000           | 1.80           | ~5,500 ops/sec    |
| DBContextStore (SQL) | 10,000           | 2.20           | ~4,500 ops/sec    |

**Observations**:

- InMemory is best for **single-process**.  
- Redis or DB is crucial for **persistence** and **multi-process** concurrency, despite higher overhead.  
- For extremely large HPC scenarios, consider **sharding** or **clustering** Redis or databases.

---

## 7. Conclusion

Benchmarking helps you **choose** or **configure** the right store backend for your performance needs. For small-scale or testing, **in-memory** might suffice. For production or large HPC/ Spark jobs, you may opt for **Redis** or a **database** with advanced concurrency controls and horizontal scaling. Always re-run benchmarks when you change:

- **Hardware** environment  
- **Data scale** or distribution  
- **Serialization** or **batch logic**

…to ensure your context-tracking layer remains **efficient** and **reliable**.

**End of `performance_benchmarks.md`**