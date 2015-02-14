
class CoffeeMachine(object):
    SERVES = {
        'Cappuccino': 3,
        'Latte': 2,
        'Espresso': 1,
    }
    def __init__(self):
        self.cups = []
        self.pressed = None

    def turn_on(self):
        pass

    def turn_off(self):
        pass

    def place_cups(self, cups):
        self.cups += cups

    def take_cup(self):
        return self.cups.pop()

    def press(self, label):
        self.pressed = label
        serve = self.SERVES[label]
        for cup in self.cups:
            if serve > 1:
                cup['milk'] = True
            if serve < cup.size:
                cup.full = False
                cup.spilt = False
            elif serve == cup.size:
                cup.full = True
                cup.spilt = False
            elif serve > cup.size:
                cup.full = True
                cup.spilt = True


class EspressoCup(dict):
    size = 1
    temperature = 94
    full = True


class CappuccinoCup(dict):
    temperature = 86
    size = 3


class LatteGlass(dict):
    size = 2


