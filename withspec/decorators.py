from .context import Description, Context, SharedExamples
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


def shared(description, **kwargs):
    registry = get_registry()
    parent = registry.current_context()
    return SharedExamples(description, 
                          parent=parent, 
                          **kwargs)


def it_behaves_like(name, **kwargs):
    registry = get_registry()
    context = registry.current_context()
    context.behaves_like(name, **kwargs)
