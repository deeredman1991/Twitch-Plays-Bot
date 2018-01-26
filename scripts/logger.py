""" Module to extend the functionality of the KivyLogger class..
"""

import os
from logging import Formatter as PSLFormatter

from kivy.config import Config
from kivy.logger import Logger as KivyLogger
from kivy.logger import FileHandler as KivyFileHandler
from kivy.logger import ConsoleHandler as KivyConsoleHandler
import kivy.logger as logging


#TODO: Set up to automatically include type() of logged vars.
verbose_formatter = PSLFormatter('| [%(asctime)-22s] | LOGGER: %(name)-10s | '\
                                 'THREAD: %(thread)5d | PATH: %(pathname)-100s'\
                                 ' | FUNCTION: %(funcName)-15s |'\
                                 'LINE: %(lineno)4d | MESSAGE: %(message)-300s')

#TODO: Also: include a DatagramHandler disabled by default and
#      .gitignore a config file with the dev server ip.
#      CONSIDER: not hiding dev server and sending log of any bot that crashes.
file_handler = KivyFileHandler()
file_handler.setFormatter(verbose_formatter)

for handler in KivyLogger.handlers:
    handler.setFormatter(verbose_formatter)

#TODO: instead of using KivyLogger.getChild; use the Logger Subclass.
#Creates a logger and sets it's debug level.
#Config.set('kivy', 'log_enable', 1)
LOGGER = KivyLogger.getChild('tpb')
LOGGER.level = logging.LOG_LEVELS['debug']
