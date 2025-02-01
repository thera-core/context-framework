import pytest
import pandas as pd
from context_framework.adapters.pandas_adapter import PandasContextAdapter
from context_framework.in_memory_context_store import InMemoryContextStore
from context_framework.exceptions import ContextKeyError

def test_pandas_adapter_column_context():
    df = pd.DataFrame({"GeneSymbol": ["BRCA1", "TP53"], "Expression": [12.3, 8.4]})
    store = InMemoryContextStore()
    adapter = PandasContextAdapter(df, context_store=store)

    adapter.add_context(("column", "GeneSymbol"), {"source": "fileA"})
    assert adapter.get_context(("column", "GeneSymbol")) == {"source": "fileA"}

    # Overwrite context
    adapter.add_context(("column", "GeneSymbol"), {"source": "fileB"})
    assert adapter.get_context(("column", "GeneSymbol")) == {"source": "fileB"}

    # Test removing context
    adapter.remove_context(("column", "GeneSymbol"))
    assert adapter.get_context(("column", "GeneSymbol")) is None

def test_pandas_adapter_invalid_column():
    df = pd.DataFrame({"ColA": [1,2], "ColB": [3,4]})
    adapter = PandasContextAdapter(df)

    with pytest.raises(ContextKeyError):
        adapter.add_context(("column", "Nonexistent"), {"test": "data"})

def test_pandas_adapter_row_context():
    df = pd.DataFrame({"GeneSymbol": ["BRCA1", "TP53"], "Expression": [12.3, 8.4]})
    adapter = PandasContextAdapter(df)

    # Suppose we want to store context at row 0 for 'Expression'
    adapter.add_context(("row", 0, "column", "Expression"), {"note": "High expression"})
    result = adapter.get_context(("row", 0, "column", "Expression"))
    assert result == {"note": "High expression"}

    # Check invalid row
    with pytest.raises(ContextKeyError):
        adapter.get_context(("row", 99, "column", "Expression"))
