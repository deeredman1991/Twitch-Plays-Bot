""" Module to extend the functionality of the KivyLogger class..
"""

import os
import sys
from threading import Lock as ThreadLock
import logging as real_logging
from functools import partial

from kivy.config import Config
from kivy.logger import Logger as KivyLogger
from kivy.logger import FileHandler as KivyFileHandler
from kivy.logger import ConsoleHandler as KivyConsoleHandler
from kivy.logger import LoggerHistory as KivyLoggerHistory
from kivy.logger import ColoredFormatter as KivyColoredFormatter
from kivy.logger import LogFile as KivyLogFile
import kivy.logger as logging

#NOTE: Needs to inherit from Logger...
class Logger():
    """ Subclass of Kivy's Logger to extend it's functionality.
    """

    #Config Options
    in_file = None
    in_class = None
    in_method = None
    method_args = None
    method_kwargs = None

    #Threadding lock.
    logging_lock = ThreadLock()

    @classmethod
    def _config_good(self):
        #Check to make sure there is a file.
        file_is_good = self.in_file is not None
        #Check to make sure there is a class.
        class_is_good = self.in_class is not None
        #Check to make sure there is a method.
        method_is_good = self.in_method is not None

        #Scream and yell if any Config Option is None.
        assert file_is_good,  'LOGGER.in_file is not defined. Did you call '\
                              'LOGGER.config_logger(__file__, self, method)?'
        assert class_is_good, 'LOGGER.in_class is not defined. Did you call '\
                              'LOGGER.config_logger(__file__, self, method)?'
        assert method_is_good,'LOGGER.in_method is not defined. Did you call '\
                              'LOGGER.config_logger(__file__, self, method)?'

        #Let whoever called us know that everything is ok.
        _is_good = file_is_good and class_is_good and method_is_good
        return _is_good

    @classmethod
    def config_logger(cls, in_file, in_class, in_method, *args, **kwargs):
        cls.in_file = in_file
        cls.in_class = in_class
        cls.in_method = in_method
        cls.method_args = args
        cls.method_kwargs = kwargs

        if cls._config_good():
            return cls.in_file, cls.in_class,\
                   cls.method, cls.method_args, cls.method_kwargs

    @classmethod
    def log_enter_method(cls, in_file, in_class, in_method, *args, **kwargs):
        cls.logging_lock.acquire()
        cls.config_logger(in_file, in_class, in_method, *args, **kwargs)

        #TODO: test this line. not sure if info(value, value2, args) is valid.
        return cls.info('Running', '%s(%s, %s)', in_method, *args, **kwargs)

    @classmethod
    def log_exit_method(cls, _return=None):
        #TODO: test this line. Not sure if info(value, value2, args) is valid.
        cls.info('Returning', '{0}({1})'.format(type(_return), _return))

        cls.in_file, cls.in_class = None, None
        cls.in_method, cls.method_args = None, None
        return cls.logging_lock.release()

    @classmethod
    def debug(cls, action, msg, *args, **kwargs):
        assert False, 'Trying to use unfinished method.'
        #Checks to make sure the config options are good.
        if cls._config_good():
            #NOTE: not finished.
            return super(Logger, cls).debug('')

    @classmethod
    def info(cls, action, msg, *args, **kwargs):
        assert False, 'Trying to use unfinished method.'
        #Checks to make sure the config options are good.
        if cls._config_goof():
            #NOTE: not finished.
            return super(Logger, cls).info( '' )
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

#TODO: instead of using KivyLogger.getChild; use the Logger Subclass.
#Creates a logger and sets it's debug level.
LOGGER = KivyLogger.getChild('tpb')
LOGGER.level = logging.LOG_LEVELS['debug']


#Tells the logger not to send it's messages to kivy's logger's handler.
#LOGGER.propagate = False

#LOGGER.logfile_activated = None
#LOGGER.trace = partial(LOGGER.log, real_logging.TRACE)

#attach_handlers(LOGGER, FileHandler, ConsoleHandler, LoggerHistory)

#sys.stderr = LogFile('stderr', Logger.warning)

#LoggerHistory = LoggerHistory
