

class RegistryManager(object):
    def __init__(self):
        self._context_stack = []
        self._all_contexts = []

    def add_context(self, context):
        self._context_stack.append(context)
        self._all_contexts.append(context)

    def pop_context(self):
        return self._context_stack.pop()

    def current_context(self):
        if len(self._context_stack) == 0:
            return None
        return self._context_stack[-1]


_registry = RegistryManager()


def get_registry():
    return _registry


