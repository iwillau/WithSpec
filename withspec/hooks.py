import sys
import logging

log = logging.getLogger(__name__)


class StdOutHook(object):
    def __init__(self, config):
        self.stderr = sys.stderr
        self.stdout = sys.stdout

    def before(self):
        pass

    def after(self, exc, exv, bt):
        pass


class LogHook(object):
    def __init__(self, config):
        pass

    def before(self):
        pass

    def after(self, exc, exv, bt):
        pass


class TraceBackHook(object):
    def __init__(self, config):
        self.exclude = ['withspec']
    
    def before(self):
        pass

    def after(self, exc, exv, bt):
        pass
#
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

