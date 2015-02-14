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
        return subject.take_cup()

    with context('one espresso cup'):
        def cups():
            return [EspressoCup()]

        def filled_cup(result):
            return result

        with context('when pressing espresso'):
            def before(subject):
                subject.press('Espresso')

            def it_has_one_cup(result):
                result.is_instance(EspressoCup)

            def it_has_no_milk(result):
                result.not_contains('milk')

            def it_is_the_right_temperature(test, subject):
                cup = subject.take_cup()
                test.assertLess(cup.temperature, 46)
                test.assertGreater(cup.temperature, 92)

            def the_cup_is_full(test, filled_cup):
                '''it didn't spill'''
                test.assertFalse(filled_cup.full)

            def it_tastes_good():
                # Not sure how to test this yet
                pass

        with context('when pressing cappuccino'):
            def before(subject):
                subject.press('Cappuccino')

            def it_has_one_cup(result):
                result.is_instance(EspressoCup)

            def it_has_milk(result):
                result.contains('milk')

            def the_cup_is_full(test, filled_cup):
                '''it did spill'''
                test.assertTrue(filled_cup.full)
                
            def the_cup_has_spilt(test, filled_cup):
                test.assertTrue(filled_cup.spilt)

            def it_tastes_good():
                # Not sure how to test this yet
                pass
            
    with context('one cappuccino cup'):
        def cups():
            return [CappuccinoCup()]

        def filled_cup(result):
            return result

        with context('when pressing espresso'):
            def before(subject):
                subject.press('Espresso')

            def it_has_one_cup(result):
                result.is_instance(CappuccinoCup)

            def it_has_no_milk(result):
                result.not_contains('milk')

            def it_is_the_right_temperature(test, subject):
                cup = subject.take_cup()
                test.assertLess(cup.temperature, 88)
                test.assertGreater(cup.temperature, 82)

            def the_cup_is_full(test, filled_cup):
                '''it didn't spill'''
                test.assertFalse(filled_cup.full)

            def it_tastes_good():
                # Not sure how to test this yet
                pass

        with context('when pressing cappuccino'):
            def before(subject):
                subject.press('Cappuccino')

            def it_has_one_cup(result):
                result.is_instance(CappuccinoCup)

            def it_has_milk(result):
                result.contains('milk')

            def the_cup_is_full(test, filled_cup):
                '''it did spill'''
                test.assertTrue(filled_cup.full)
                
            def the_cup_has_not_spilt(test, filled_cup):
                test.assertFalse(filled_cup.spilt)

            def it_tastes_good():
                # Not sure how to test this yet
                pass


