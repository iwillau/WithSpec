import sys
import os
import logging
from traceback import extract_tb
from cStringIO import StringIO

log = logging.getLogger(__name__)


class StdOutHook(object):
    def __init__(self, config):
        self.stdout = sys.stdout
        self.stderr = sys.stderr
        self.out_buffer = StringIO()
        self.err_buffer = StringIO()

    def before(self):
        sys.stdout = self.out_buffer
        sys.stderr = self.err_buffer

    def after(self, exc, exv, bt):
        # As we are restoring things to sys, 
        # We cannot be a generator
        sys.stdout = self.stdout
        sys.stderr = self.stderr

        self.out_buffer.seek(0)
        out = [line.strip() for line in self.out_buffer.readlines()]
        self.err_buffer.seek(0)
        err = [line.strip() for line in self.err_buffer.readlines()]

        self.out_buffer.seek(0)
        self.out_buffer.truncate()
        self.err_buffer.seek(0)
        self.err_buffer.truncate()

        response = []
        if len(out) > 0:
            response.append('>> stdout <<')
            response += out
        if len(err) > 0:
            response.append('>> stderr <<')
            response += err
        if len(response) > 0:
            return response


class LogHook(object):
    def __init__(self, config):
        self.root_logger = logging.getLogger()
        self.buffer = StringIO()
        self.handler = logging.StreamHandler(self.buffer)
        self.handler.setFormatter(
            logging.Formatter('%(levelname)-5.6s '\
                              '[%(name)s] %(message)s')
        )
        

    def before(self):
        self.root_logger.addHandler(self.handler)
        # We may have to clear out the handlers here ??
        # Or let the StdOut Hook deal with it ?
        self.level = self.root_logger.getEffectiveLevel()
        self.root_logger.setLevel(logging.NOTSET)


    def after(self, exc, exv, bt):
        # Restore the Level
        self.root_logger.setLevel(self.level)
        # Remove the Handler
        self.root_logger.removeHandler(self.handler)

        # We don't use generator here, as we need to clear out the buffer
        self.buffer.seek(0)
        lines = [line.strip() for line in self.buffer.readlines()]

        self.buffer.seek(0)
        self.buffer.truncate()
        if len(lines) > 0:
            return ['>> logs <<'] + lines


class TraceBackHook(object):
    '''
    Alternatively, we could throw and catch an exception in the 
    `before` hook, and store the back trace, and exclude all of that.
    That would neatly exclude anything not related to the test, without
    hardcoding `withspec`.
    '''
    def __init__(self, config):
        if not config['backtrace']:
            module = sys.modules['withspec']
            self.exclude = os.path.dirname(module.__file__)
        else:
            self.exclude = None
    
    def after(self, exc, exv, bt):
        if exc is not None:
            for filename, lineno, name, line in reversed(extract_tb(bt)):
                if filename.startswith(self.exclude):
                    break
                yield '# %s:%d:in %s' % (filename, lineno, name)

