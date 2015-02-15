from withspec import describe, context


with describe('Mock'):
    def before(subject):
        subject.my_method()

    def something(subject):
        return subject.second()

    def the_test(subject, something):
        pass
        #assert subject called my_method once
        #assert subject called second one

