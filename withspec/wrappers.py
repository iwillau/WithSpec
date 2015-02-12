

class TestWrapper(object):
    def mep(self):
        pass


class StdOutWrapper(TestWrapper):
    def __init__(self):
        pass


class LogWrapper(TestWrapper):
    def __init__(self):
        pass


class TraceBackWrapper(TestWrapper):
    def __init__(self, exclude=None):
        self.exclude = exclude
    

