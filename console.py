import time
import pygame
import sys
from pygame.locals import *

consoles = []
records = []

TYPE_INFO    = 0
TYPE_WARNING = 1
TYPE_ERROR   = 2

TITLE = {}
TITLE[TYPE_INFO]    = ""
TITLE[TYPE_WARNING] = "WARNING: "
TITLE[TYPE_ERROR]   = "ERROR: "
    
def log(message, e=None, level=TYPE_INFO):
    """Create a console record for a normal, informational message.
    
    Args:
        message: The message to attach to the record.
        e: The exception to attach to the record.
    """
    record = ConsoleRecord(message, TYPE_INFO, e)
    records.append(record)
    
    for console_ in consoles:
        console_.post(record)

def warn(message, e=None):
    """Create a console record for a warning.
    
    Args:
        message: The message to attach to the record.
        e: The exception to attach to the record.
    """
    log(message, e, TYPE_WARNING)
    
def error(message, e=None):
    """Create a console record for an error.
    
    Args:
        message: The message to attach to the record.
        e: The exception to attach to the record (optional).
    """
    log(message, e, TYPE_ERROR)
    
class ConsoleRecord(object):
    """A record containing a message, level of importance, timestamp, and
    exception (optional)."""
    def __init__(self, message='', level=TYPE_INFO, e=None):
        self.message = message
        self.level = level
        self.e = e
        self.timestamp = time.gmtime()
        
    def __str__(self):
        return TITLE[self.level] + self.message
        
class Console(object):
    """An abstract Console. Consoles can be used to display or store records
    that are logged by the application."""
    def post(self, record):
        if record.level == TYPE_INFO:
            self.info(record)
        elif record.level == TYPE_WARNING:
            self.warn(record)
        else:
            self.error(record)

    def info(self, message, e=None):
        pass
        
    def warn(self, message, e=None):
        pass
        
    def error(self, message, e=None):
        pass
        
class StdConsole(Console):
    """Standard terminal console."""
    def info(self, record):
        sys.stdout.write(TITLE[TYPE_INFO] + str(record) + "\n")
    def warn(self, record):
        sys.stdout.write(TITLE[TYPE_WARNING] + str(record) + "\n")
    def error(self, record):
        sys.stdout.write(TITLE[TYPE_ERROR] + str(record) + "\n")
        
consoles.append(StdConsole())