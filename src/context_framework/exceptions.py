"""
exceptions.py

Defines custom exception classes for the Context-Tracking Framework.
"""

class ContextStoreError(Exception):
    """
    Raised when a ContextStore fails to perform a read/write/delete operation,
    such as due to a database or network error.
    """
    pass

class ContextKeyError(Exception):
    """
    Raised when a key is invalid for the data structure or store.
    This might occur if the key doesn't exist or conflicts with domain rules.
    """
    pass
