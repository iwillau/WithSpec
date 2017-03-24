

class RegistryManager(object):
    def __init__(self):
        self._context_stack = []  # The 'current' context
        self._all_contexts = []   # All contexts in the order they appear
        self.contexts = []        # The 'tree' of contexts, contains 'top'
                                  # level contexts

    def add_context(self, context):
        if len(self._context_stack) == 0:
            self.contexts.append(context)
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


