

class RegistryManager(object):
    def __init__(self):
        self._contexts = []
        self.shared = {}

    def add_context(self, context):
        self._contexts.append(context)

    def pop_context(self):
        return self._contexts.pop()

    def current_context(self):
        if len(self._contexts) == 0:
            return None
        return self._contexts[-1]


_registry = RegistryManager()


def get_registry():
    return _registry


