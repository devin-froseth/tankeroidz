"""
    tankeroidz.console
    ~~~~~~~~~~~~~~~~~~

    Logging implementation for Tankeroidz.
"""

import time
import pygame
import sys

CONSOLES = []
RECORDS = []

TYPE_INFO = 0
TYPE_WARNING = 1
TYPE_ERROR = 2

TITLE = {}
TITLE[TYPE_INFO] = ""
TITLE[TYPE_WARNING] = "WARNING: "
TITLE[TYPE_ERROR] = "ERROR: "

def log(message, err=None, level=TYPE_INFO):
    """ Create a console record for a normal, informational message.

    Parameters
    ----------
        message : str
        err : exception
    """
    record = ConsoleRecord(message, level, err)
    RECORDS.append(record)

    for console in CONSOLES:
        console.log(record)

def warn(message, err=None):
    """Create a console record for a warning.

    Parameters
    -----------
        message : str
        err : exception
    """
    log(message, err, TYPE_WARNING)

def error(message, err=None):
    """Create a console record for an error.

    Parameters
    -----------
        message : str
        err : exception
    """
    log(message, err, TYPE_ERROR)

class ConsoleRecord(object):
    """A record containing a message, level of importance, timestamp, and
    exception (optional)."""
    def __init__(self, message='', level=TYPE_INFO, err=None):
        self.message = message
        self.level = level
        self.err = err
        self.timestamp = time.gmtime()

    def __str__(self):
        return TITLE[self.level] + self.message

class Console(object):
    """An abstract Console. Consoles can be used to display or store records
    that are logged by the application."""
    def __init__(self, recording_level=0):
        self.recording_level = recording_level

    def log(self, record):
        if self.recording_level < record.level:
            return

        if record.level == TYPE_INFO:
            self.info(record)
        elif record.level == TYPE_WARNING:
            self.warn(record)
        else:
            self.error(record)

    def post(self, message):
        pass

    def info(self, record):
        self.post(TITLE[TYPE_INFO] + str(record))
    def warn(self, record):
        self.post(TITLE[TYPE_WARNING] + str(record))
    def error(self, record):
        self.post(TITLE[TYPE_ERROR] + str(record))

class StdConsole(Console):
    """Standard terminal console."""
    def post(self, message):
        sys.stdout.write(message + "\n")

class IOConsole(Console):
    """Console that logs records to a .log file."""
    def __init__(self, log_file=None):
        Console.__init__(self)

        self._log_file = None
        self.log_file = log_file

    @property
    def log_file(self):
        return self._log_file

    @log_file.setter
    def log_file(self, log_file):
        if log_file is not None:
            self.log_file.close()

        if type(log_file) is str:
            self._log_file = open(log_file, 'rw')
        elif type(log_file) is file:
            self._log_file = log_file
        else:
            raise TypeError("Must be str or file.")

CONSOLES.append(StdConsole())
