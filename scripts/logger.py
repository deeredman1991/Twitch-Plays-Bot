""" Module to extend the functionality of the KivyLogger class..
"""

import os
import sys
import logging as real_logging
from functools import partial

from kivy.config import Config
from kivy.logger import Logger
from kivy.logger import FileHandler as KivyFileHandler
from kivy.logger import ConsoleHandler as KivyConsoleHandler
from kivy.logger import LoggerHistory as KivyLoggerHistory
from kivy.logger import ColoredFormatter as KivyColoredFormatter
from kivy.logger import LogFile as KivyLogFile
import kivy.logger as logging

class FileHandler(KivyFileHandler):
    """ Subclass of Kivy's File Handler to extend it's functionality.
    """

class ConsoleHandler(KivyConsoleHandler):
    """ Subclass of Kivy's Stream Handler to extend it's functionality.
    """

class LoggerHistory(KivyLoggerHistory):
    """ Subclass of Kivy's Logger History class to extend it's functionality.
    """

class ColoredFormatter(KivyColoredFormatter):
    """ Subclass of Kivy's Formatter to extend it's functionality.
    """

class LogFile(KivyLogFile):
    """ Subclass of Kivy's LogFile to extend it's functionality.
    """

def attach_handlers(logger, file_handler, console_handler, logger_history):
    """ attaches handlers to logger
    """
    logger.addHandler(logger_history())
    if 'KIVY_NO_FILELOG' not in os.environ:
        logger.addHandler(file_handler())

    # Use the custom handler instead of streaming one.
    if 'KIVY_NO_CONSOLELOG' not in os.environ:
        if hasattr(sys, '_tpb_logging_handler'):
            logger.addHandler(getattr(sys, '_tpb_handler'))
        else:
            use_color = (
                os.name != 'nt' and
                os.environ.get('KIVY_BUILD') not in ('android', 'ios') and
                os.environ.get('TERM') in (
                    'rxvt',
                    'rxvt-256color',
                    'rxvt-unicode',
                    'rxvt-unicode-256color',
                    'xterm',
                    'xterm-256color',
                )
            )
            if not use_color:
                # No additional control characters will be inserted inside the
                # levelname field, 7 chars will fit "WARNING"
                color_fmt = logging.formatter_message(
                    '[%(levelname)-7s] %(message)s', use_color)
            else:
                # levelname field width need to take into account the length of the
                # color control codes (7+4 chars for bold+color, and reset)
                color_fmt = logging.formatter_message(
                    '[%(levelname)-18s] %(message)s', use_color)
            formatter = ColoredFormatter(color_fmt, use_color=use_color)
            console = console_handler()
            console.setFormatter(formatter)
            logger.addHandler(console)

#Sets the logfiles to go into %cd%/logs
#Config.set('kivy', 'logdir', os.path.dirname(os.path.abspath(__file__)))

#Creates a logger and sets it's debug level.
LOGGER = Logger.getChild('tpb')
LOGGER.level = logging.LOG_LEVELS['debug']


#Tells the logger not to send it's messages to kivy's logger's handler.
#LOGGER.propagate = False

#LOGGER.logfile_activated = None
#LOGGER.trace = partial(LOGGER.log, real_logging.TRACE)

#attach_handlers(LOGGER, FileHandler, ConsoleHandler, LoggerHistory)

#sys.stderr = LogFile('stderr', Logger.warning)

#LoggerHistory = LoggerHistory
