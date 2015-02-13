from withspec import describe, context
from coffee import (
    CoffeeMachine, 
    EspressoCup,
    CappuccinoCup,
    LatteGlass,
    )


with describe(CoffeeMachine):
    def before(subject, cups):
        subject.turn_on()
        subject.place_cups(cups)

    def after(subject):
        subject.turn_off()

    def result(subject):
        return subject.take_cups()

    with context('one cup of espresso'):
        def cups():
            return [EspressoCup()]

        def filled_cup(result):
            return result[0]

        def it_can_sleep(result):
            assert 1 == 2

        def it_can_take_two_cups():
            pass

        with context('when pressing espresso'):
            def before(subject):
                subject.press('Espresso')

            def it_has_one_cup(result):
                result.assert_length(1)

            def it_has_no_milk(result):
                result.assert_not_contains('milk')

            def it_is_the_right_temperature(test, result):
                test.assert_smaller(result.temperature, 96)
                test.assert_larger(result.temperature, 92)

            def the_cup_is_full(filled_cup):
                '''it didn't spill'''
                filled_cup.assert_response('full', True)

            def it_tastes_good():
                # Not sure how to test this yet
                pass

        with context('when pressing cappuccino'):
            def before(subject):
                subject.press('Cappuccino')

            def it_has_one_cup(result):
                result.assert_length(1)

            def it_has_milk(filled_cup):
                result.assert_contains('milk')

            def the_cup_is_full(filled_cup):
                '''it didn't spill'''
                filled_cup.assert_response('full', True)

            def the_cup_has_spilt(filled_cup):
                filled_cup.assert_response('spilt', True)

            def it_tastes_good():
                # Not sure how to test this yet
                pass
            
    with context('one cappuccino cup'):
        def cups():
            return [Cappuccino()]

        def filled_cup(result):
            return result[0]

        def around(test):
            # Do A MOCK HERE
            pass


with describe('Filters'):
    def subject(coffee_filter):
        return Machine(filter=coffee_filter)
