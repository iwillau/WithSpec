from withspec import describe, context
from coffee import (
    CoffeeMachine, 
    EspressoCup,
    CappuccinoCup,
    LatteGlass,
    )


with describe(CoffeeMachine):
    def before(subject, cups):
        print 'BEFORE ONE'
        subject.turn_on()
        print 'PLACING %s' % cups
        subject.place_cups(cups)

    def after(subject):
        print 'AFTER ONE'
        subject.turn_off()

    def result(subject):
        print 'RESULT'
        return subject.take_cup()

    with context('one cup of espresso'):
        def cups():
            print 'CUPS ARE HERE'
            return [EspressoCup()]

        def filled_cup(result):
            print 'FILLED CUP'
            return result

        def it_can_sleep(filled_cup):
            print 'TEST ONE'
            print 'wtf omg bbg'
            print filled_cup
            assert 1 == 1

        def it_can_take_two_cups():
            pass

        with context('when pressing espresso'):
            def before(subject):
                subject.press('Espresso')

            def it_has_one_cup(result):
                result.assert_length(1)

            def it_has_no_milk(result):
                print result.subject
                result.not_contains('milk')

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
                print 'whos a what now?'
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


with describe('Filters'):
    def subject(coffee_filter):
        return Machine(filter=coffee_filter)
