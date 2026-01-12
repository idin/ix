"""
Agent exceptions.
"""


class SpecialObjectKeyError(KeyError):
    """
    Exception raised when a special object is not found.
    
    This is a subclass of KeyError to maintain compatibility while allowing
    specific error handling for special object lookups.
    """
    pass

