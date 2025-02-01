import pytest
from context_framework.in_memory_context_store import InMemoryContextStore
from context_framework.exceptions import ContextStoreError

def test_in_memory_store_basic_operations():
    store = InMemoryContextStore()

    # Test set
    store.set("key1", {"info": "value1"})
    store.set("key2", {"info": "value2"})

    # Test get
    assert store.get("key1") == {"info": "value1"}
    assert store.get("nonexistent") is None

    # Test list_keys
    keys = store.list_keys()
    assert "key1" in keys
    assert "key2" in keys

    # Test delete
    store.delete("key1")
    assert store.get("key1") is None

def test_in_memory_store_exceptions():
    store = InMemoryContextStore()
    # It's unlikely to fail in memory, but we can still confirm no unexpected exception is raised
    try:
        store.set("key", {"test": "data"})
    except ContextStoreError:
        pytest.fail("Setting a key should not raise ContextStoreError in normal usage.")
