from .context import Description, Context
from .registry import get_registry


def describe(described, **kwargs):
    registry = get_registry()
    parent = registry.current_context()
    return Description(described, 
                       parent=parent, 
                       **kwargs)


def context(description, **kwargs):
    registry = get_registry()
    parent = registry.current_context()
    return Context(description, 
                   parent=parent, 
                   **kwargs)
