

class WithSpecRunner(object):
    def __init__(self, printer, wrappers, fail_fast=False, dryrun=False):
        self.fail_fast = fail_fast
        self.dryrun = dryrun
        self.printer = printer
        self.wrappers = wrappers
        self.failed = []
        self.skipped = []
        self.pending = []

    def run(self, tests):
        for test in tests:
            print test

        if len(self.failed) > 0:
            printer.new_line()
            printer.line('Failures:')
            printer.new_line()

            for i, test in enumerate(self.failed):
                printer.line('  {:d}) {}', i+1, test.full_name())
                for error in test.errors:
                    error.line(printer)
                printer.new_line()


#import os
#import sys
#import traceback
#import logging
#import time
#from StringIO import StringIO
#
#
#COLOR_NAMES = ["grey", "red", "green", "yellow", "blue", "magenta", "cyan",
#               "white"]
#COLOR_CODES = dict(zip(COLOR_NAMES, list(range(30, 38))))
#COLOR_FMT = "\033[%dm%s\033[0m"
#
#log = logging.getLogger('pyspec.runner')
#
#def color(string, color):
#    return COLOR_FMT % (COLOR_CODES[color], string)
#
#
#def run_spec():
#    pyspec_logs = StringIO()
#    pyspec_handler = logging.StreamHandler(pyspec_logs)
#    pyspec_logger = logging.getLogger('pyspec')
#    pyspec_logger.addHandler(pyspec_handler)
#    pyspec_logger.propagate = False
#    pyspec_logger.setLevel(logging.NOTSET)
#    pyspec_logger.info('Starting a run')
#
#    log_formatter = logging.Formatter('%(filename)-25s %(lineno)4d %(levelname)-8s %(message)s', None)
#    root_logger = logging.getLogger()
#    # load up dir/file here
#    time_start = time.time()
#    cwd = os.getcwd()
#    for root, dirs, files in os.walk('spec'):
#        os.chdir(root)
#        for filename in files:
#            if filename.endswith('.py'):
#                filepath = os.path.join('.', root, filename)
#                log.debug('Loading file %s' % filepath)
#                with open(filename, 'r') as fh:
#                    file_globals = {}
#                    file_locals = {}
#                    code = compile(fh.read(), filepath, 'exec')
#                    exec(code, file_globals, file_locals)
#                except SyntaxError, e:
#                except TypeError, e:  # File was empty
#
#        os.chdir(cwd)
#
#    time_loading = time.time() - time_start
#
#    from river.pyspec import TEST_STACK
#    current_path = []
#    pending_count = 0
#    skip_count = 0
#    test_count = 0
#    failures = []
#    print ''
#    time_start = time.time()
#    for test in TEST_STACK:
#        test_count += 1
#        test_path = [loc.name for loc in test.location()]
#        test_path.reverse()
#        if test_path != current_path:
#            while len(current_path) > 0:
#                if current_path == test_path[:len(current_path)]:
#                    break
#                current_path.pop()
#            while len(current_path) < len(test_path):
#                current_path.append(test_path[len(current_path)])
#                print '%s%s' % ('  ' * (len(current_path)-1),
#                                current_path[-1])
#
#        if test.pending:
#            pending_count += 1
#            print '%s%s' % ('  ' * len(current_path), 
#                            color(test.name, 'yellow'))
#        else:
#            if test.skip:
#                skip_count += 1
#                # Filter by tag/name/line_number here
#                continue
#            log.debug('Preparing to run test %s' % '>'.join(reversed([parent.name for parent in test.location()])) + '>' + test.name)
#            stdout_buf = StringIO()
#            stderr_buf = StringIO()
#            log_buf = StringIO()
#
#            stdout = sys.stdout
#            stderr = sys.stderr
#
#
#            log_handler = logging.StreamHandler(log_buf)
#            log_handler.setFormatter(log_formatter)
#            root_logger.addHandler(log_handler)
#            root_logger.setLevel(logging.NOTSET)
#
#            sys.stdout = stdout_buf
#            sys.stderr = stderr_buf
#
#            error = None
#
#            try:
#                test.before()
#                test.run()
#                test.after()
#            except KeyboardInterrupt:
#                raise
#            except Exception, e:
#                error = sys.exc_info()  # class, value, traceback
#
#
#            sys.stdout = stdout
#            sys.stderr = stderr
#
#            root_logger.removeHandler(log_handler)
#            log_handler.close()
#            del log_handler
#
#            if error:
#                log_buf.seek(0)
#                stdout_buf.seek(0)
#                stderr_buf.seek(0)
#                failures.append((test, stdout_buf.readlines(), stderr_buf.readlines(), log_buf.readlines(), error))
#                error_string = '%s (%s)' % (test.name, str(error[0].__name__))
#                print '%s%s' % ('  ' * len(current_path), 
#                                color(error_string, 'red'))
#            else:
#                print '%s%s' % ('  ' * len(current_path), 
#                                color(test.name, 'green'))
#
#    time_testing = time.time() - time_start
#    if len(failures) > 0:
#        print '\nFailures:\n'
#        for i, (test, stdout, stderr, logs, error) in enumerate(failures):
#            print '  %d) %s' % (i+1, ' '.join(reversed([parent.name for parent in test.location()])) + ' ' + test.name)
#            first_line = True
#            for line in ('Failure/Error: %s' % str(error[1])).splitlines():
#                if first_line:
#                    first_line = False
#                    print color('     %s' % line, 'red')
#                else:
#                    print color('       %s' % line, 'red')
#            for filename, lineno, name, line in reversed(traceback.extract_tb(error[2])):
#                if filename.startswith(cwd):
#                    filename = '.' + filename[len(cwd):]
#                # We could possibly filter out pyspec from this output (if we wanted to)
#                print color('     # %s:%d:in %s' % (filename,lineno,name), 'cyan')
#
#            if len(stdout) > 0:
#                print color('     >> stdout <<', 'green')
#                for line in stdout:
#                    print color('     %s' % line[:-1], 'green')
#            if len(stderr) > 0:
#                print color('     >> stderr <<', 'yellow')
#                for line in stderr:
#                    print color('     %s' % line[:-1], 'yellow')
#            if len(logs) > 0:
#                print color('     >> logs <<', 'blue')
#                for line in logs:
#                    print color('     %s' % line[:-1], 'blue')
#            print ''
#
#    print '\nFinished in %.3f seconds (specs took %.3f seconds to load)' % (time_testing, time_loading)
#    print color('%d tests, %d pending, %d failures, %d skipped\n' % (test_count, pending_count, len(failures), skip_count), 'red')
#
#    if len(failures) > 0:
#        print ''
#        print 'Failed Tests:\n'
#        for test, stdout, stderr, logs, error in failures:
#            print color(test.definition(), 'red'), 
#            print color(' # %s' % ' '.join(reversed([parent.name for parent in test.location()])) + ' ' + test.name, 'cyan')
#        print ''
#
#    if False:
#        print 'PySpec Logs'
#        pyspec_logs.seek(0)
#        for line in pyspec_logs.readlines():
#            print line.strip()
#        print ''
#
#
#
#if __name__ == '__main__':
#    run_spec()
