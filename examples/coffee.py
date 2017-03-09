'''
This module contains objects that are used in the examples provided.

They are intended to cover as many use cases as possible
'''


class CupOverflowException(Exception):
    def __init__(cup = None, size = None, *args):
        self.cup = cup
        self.size = size
        super().__init__('Cup overflow of MEP', *args)


class CoffeeMachine(object):
    def __init__(self):
        self.on = False
        self.cup = None

    def press_on(self):
        self.on = True

    def press_off(self):
        self.on = False

    def place_cup(self, cup):
        self.cup = cup

    def take_cup(self):
        cup = self.cup
        self.cup = None
        return cup

    def make_coffee(self, coffee_type):
        return None


class CoffeeCup():
    size = 180  # mL


class CoffeeMug():
    size = 300  # mL


class CoffeeGlass():
    size = 240  # mL


class EspressoGlass():
    size = 60  # mL


class CoffeeShot():
    pass


class Ristretto(CoffeeShot):
    size = 15  # mL


class Espresso(CoffeeShot):
    size = 30  # mL


class Lungo(CoffeeShot):
    size = 60  # mL


class Cappuccino():
    '''A Cappuccino is defined as having a double espresso,
    hot milk and steamed milk foam.

    It should be 180mL
    '''
    shot_type = Espresso
    shot_count = 2


class CafeLatte():
    '''A Latte is defined as having a single espresso,
    hot milk and steamed milk foam (12mm).

    It should be 240mL
    '''
    shot_type = Espresso
    shot_count = 1


class FlatWhite():
    '''A Flat White is defined as having a double ristretto
    hot milk and steamed milk foam (12mm).

    It should be 180mL
    '''
    shot_type = Ristretto
    shot_count = 2


