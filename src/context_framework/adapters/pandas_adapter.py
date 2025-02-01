"""
pandas_adapter.py

An example adapter for Pandas DataFrame objects. This adapter interprets
keys as something like ("column", column_name) or ("row", row_index, "column", col_name).
"""

import pandas as pd
from typing import Any, Dict, Optional
from context_framework.adapters.base_adapter import BaseContextAdapter
from context_framework.exceptions import ContextKeyError

class PandasContextAdapter(BaseContextAdapter):
    """
    A context-aware adapter for Pandas DataFrames. By default, we interpret
    keys as either ("column", col_name) or ("row", row_index, "column", col_name).
    """

    def __init__(self, df: pd.DataFrame, context_store=None) -> None:
        """
        :param df:
            The Pandas DataFrame to wrap.
        :param context_store:
            An optional ContextStore for metadata persistence.
        """
        super().__init__(context_store)
        self.df = df

    def validate_key(self, key: Any) -> None:
        """
        Checks whether 'key' references a valid column or row in the DataFrame.
        Raise ContextKeyError if invalid.

        Typical key patterns:
          ("column", "GeneSymbol")
          ("row", 42, "column", "Expression")
        """
        if isinstance(key, tuple) and len(key) >= 2:
            key_type = key[0]
            if key_type == "column":
                # Example: ("column", "GeneSymbol")
                col_name = key[1]
                if col_name not in self.df.columns:
                    raise ContextKeyError(f"Column '{col_name}' not found in DataFrame.")
            elif key_type == "row":
                # Example: ("row", 10, "column", "GeneSymbol")
                if len(key) < 4:
                    # We might just accept ("row", index), or require ("row", index, "column", col_name)
                    # Depending on your domain. Let's do a simple check.
                    row_index = key[1]
                    if row_index not in self.df.index:
                        raise ContextKeyError(f"Row index '{row_index}' not found in DataFrame.")
                else:
                    row_index = key[1]
                    if row_index not in self.df.index:
                        raise ContextKeyError(f"Row index '{row_index}' not found in DataFrame.")
                    if key[2] == "column":
                        col_name = key[3]
                        if col_name not in self.df.columns:
                            raise ContextKeyError(f"Column '{col_name}' not found in DataFrame.")
                    else:
                        raise ContextKeyError(f"Invalid key pattern for row-level context: {key}")
            else:
                # If the first element is not recognized, raise an error
                raise ContextKeyError(f"Unrecognized key pattern: {key}")
        else:
            # If it's not a tuple or doesn't have enough elements, let's raise an error
            raise ContextKeyError(f"Key '{key}' is not a valid Pandas context reference.")
