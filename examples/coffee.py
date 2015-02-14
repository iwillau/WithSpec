
class CoffeeMachine(object):
    def __init__(self):
        self.cups = []

    def turn_on(self):
        pass

    def turn_off(self):
        pass

    def place_cups(self, cups):
        self.cups += cups

    def take_cup(self):
        return self.cups.pop()


class EspressoCup(object):
    pass


class CappuccinoCup(object):
    pass


class LatteGlass(object):
    pass


