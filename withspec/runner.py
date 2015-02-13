import logging

log = logging.getLogger(__name__)


def exception_formatter(ex):
    lines = []
    text = str(ex)
    for line in text.splitlines():
        if len(lines) == 0:
            line = 'Failure/Error: %s' % line
        else:
            line = '  %s' % line
        lines.append(line)
    return lines


class TestManager(object):
    def __init__(self, hooks):
        self.hooks = hooks
        self.error = None
        self.output = []

    def __enter__(self):
        for hook in self.hooks:
            if hasattr(hook, 'before'):
                log.debug('Running %s before', str(hook))
                hook.before()
        return self

    def __exit__(self, exc, exv, bt):
        # Run the 'after' hooks in reverse
        if exc is not None:
            self.error = exc.__name__
            self.output.append(exception_formatter(exv))
        for hook in reversed(self.hooks):
            if hasattr(hook, 'after'):
                log.debug('Running %s after', str(hook))
                output = hook.after(exc, exv, bt)
                if output is not None:
                    self.output.append(output)

        if exc == KeyboardInterrupt:
            return False  # User wants out, we'll leave.
                          # We just had to 'unhook' first
        return True


class WithSpecRunner(object):
    def __init__(self, hooks, fail_fast=False, dryrun=False):
        self.fail_fast = fail_fast
        self.dryrun = dryrun
        self.hooks = hooks
        self.failed = []
        self.skipped = []
        self.pending = []

    def run(self, tests, printer):
        for test in tests:
            if 'pending' in test.tags:
                self.pending.append(test)
                printer.warn(test)
                continue
            if 'skip' in test.tags:
                self.skipped.append(test)
                printer.warn(test)
                continue
            # Actually do a test!
            with TestManager(self.hooks) as manager:
                test.run()

            if manager.error is None:
                printer.success(test)
            else:
                self.failed.append((test, manager.output))
                printer.error(test, manager.error)
                if self.fail_fast:
                    break
        
        printer.new_line()
        if len(self.failed) > 0:
            printer.new_line()
            printer.line('Failures:')
            printer.new_line()

            colours = ['red', 'cyan', 'yellow', 'blue', 'magenta']

            for i, (test, output) in enumerate(self.failed):
                printer.line('  {:d}) {}', i+1, test.fullname())
                for hook_number, error in enumerate(output):
                    colour = colours[hook_number%len(colours)]
                    for line in error:
                        printer.line(line, level=2, colour=colour)
                printer.new_line()


