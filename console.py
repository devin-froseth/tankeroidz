import pygame
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
    
def log(message, e=None):
    record = ConsoleRecord(message, TYPE_INFO, e)
    records.append(record)
    
    for console_ in consoles:
        console_.log(record)

def warn(message, e=None):
    log(message, e)
    
class ConsoleRecord(object):
    def __init__(self, message='', level=TYPE_INFO, e=None):
        self.message = message
        self.level = level
        self.e = e
        
    def __str__(self):
        return TITLE[self.level] + self.message
        
class Console(object):
  
    messages = []

    def info(self, message, e=None):
        self.messages.append([message, 0])
        print "> " + str(message)
  
    def debug(self, message, e=None):
        self.messages.append([message, 1])
        print "Debug: " + message
    
    def warning(self, message, e=None):
        self.messages.append([message, 2])
        print "Warning: " + message
    
    def error(self, message, e=None):
        self.messages.append([message, 3])
        print "Error" + error

class StdConsole(Console):
    """Standard terminal console."""
    def log(self, record):
        print record
        
consoles.append(StdConsole())