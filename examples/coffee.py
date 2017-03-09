'''
This module contains objects that are used in the examples provided.

They are intended to cover as many use cases as possible
'''


class CoffeeMachineException(Exception):
    pass


class CupOverflowException(CoffeeMachineException):
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
        if self.cup is not None:
            raise CoffeeMachineException('Coffee Machine already has a cup')
        self.cup = cup

    def take_cup(self):
        if self.cup is None:
            raise CoffeeMachineException('Coffee Machine does not have a cup')
        cup = self.cup
        self.cup = None
        return cup

    def make_coffee(self, coffee_type):
        if self.on is False:
            return None
        if self.cup is None:
            raise CoffeeMachineException('Coffee Machine does not have a cup')

        # Firstly put in the coffee shots
        for shot in range(coffee_type.shot_count):
            self.cup.pour(coffee_type.shot_type.size)

        return None


class GenericCup():
    def __init__(self):
        self.amount = 0  # mL

    def pour(self, amount):
        self.amount += amount
        if self.amount > self.size:
            self.amount = self.size
            raise CupOverflowException(self, self.amount)


class CoffeeCup(GenericCup):
    size = 180  # mL


class CoffeeMug(GenericCup):
    size = 300  # mL


class CoffeeGlass(GenericCup):
    size = 240  # mL


class EspressoGlass(GenericCup):
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


