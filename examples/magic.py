from withspec import describe, context, shared
from coffee import (
    CoffeeMachine, 
    CoffeeMachineException,
    Espresso,
    Cappuccino,
    CafeLatte,
    FlatWhite,
    CoffeeCup,
    )


with shared('coffee maker'):
    def make_a_latte(subject):
        subject.make_coffee(CafeLatte)

    def make_a_cappucino(subject):
        subject.make_coffee(Cappuccino)

    def make_a_flatwhite(subject):
        subject.make_coffee(FlatWhite)


with shared('coffee burner'):
    def make_a_latte(subject):
        subject.make_coffee(CafeLatte)

    def make_a_cappucino(subject):
        subject.make_coffee(Cappuccino)

    def make_a_flatwhite(subject):
        subject.make_coffee(FlatWhite)


with describe(CoffeeMachine) as expect:

    with context('has no cup'):
        def placing_cup(subject):
            subject.place_cup(CoffeeCup())
            expect(subject.cup).is_instance(CoffeeCup)

        def removing_cup_should_fail(subject):
            expect(subject.take_cup).raises(CoffeeMachineException)

    with context('has a cup'):
        def before(subject):
            subject.place_cup(CoffeeCup())

        def placing_cup_should_fail(subject):
            with expect.raises(CoffeeMachineException):
                subject.place_cup(CoffeeCup())

        def removing_cup(subject):
            cup = subject.take_cup()
            expect(cup).is_instance(CoffeeCup)
            expect(subject.cup).is_none()
 
    with context('when powered off'):
        def pressing_on_turns_on(subject):
            subject.press_on()
            expect(subject.on).is_true()

        def pressing_off_does_nothing(subject):
            subject.press_off()
            expect(subject.on).is_false()

        def making_coffee_does_nothing(subject):
            subject.make_coffee(CafeLatte)

    with context('when powered on'):
        def before(subject):
            subject.press_on()

        def pressing_on_does_nothing(subject):
            expect(subject.on).to.be_true()
            subject.press_on()
            expect(subject.on).is_true()

        def pressing_off_turns_off(subject):
            subject.press_off()
            expect(subject.on).is_false()

        with context('has no cup'):
            def making_coffee_raises_exception(subject):
                with expect.raises(CoffeeMachineException, 
                                 regex='Coffee Machine does not have a cup'):
                    subject.make_coffee(CafeLatte)

        with context('has a coffee cup'):
            def cup():
                return CoffeeCup()

            def before(subject, cup):
                subject.place_cup(CoffeeCup())

            def after(subject):
                cup = subject.take_cup()
                expect(cup.amount).is_greater(0)

            def will_it_fake(subject):
                subject.turn_off()

            def does_it_taste_good():
                # Not sure how we can test this in software ;-)
                pass

            it_behaves_like('coffee maker')


