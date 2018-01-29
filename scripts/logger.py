""" Module to extend the functionality of the KivyLogger class..
"""
# pylint: disable=locally-disabled, invalid-name, too-few-public-methods
from logging import Formatter as PSLFormatter
import inspect

from kivy.logger import Logger as KivyLogger
import kivy.logger as logging

verbose_formatter = PSLFormatter('| [%(asctime)-22s] | LOGGER: %(name)-35s | '\
                                 'THREAD: %(thread)5d | PATH: %(pathname)-100s'\
                                 ' | FUNCTION: %(funcName)-18s |'\
                                 'LINE: %(lineno)4d | MESSAGE: %(message)-300s')

#TODO: Also: include a DatagramHandler disabled by default and
#      .gitignore a config file with the dev server ip.
#      Need to create a devserver to accept packets sent by the
#      DatagramHandler.
#      CONSIDER: not hiding dev server and sending log of any bot that crashes.
#                enabled by default but with the option to disable.
for handler in KivyLogger.handlers:
    handler.setFormatter(verbose_formatter)

#Uncomment this line to enable the kivy logger. Warning: This might hurt
#   the logging developer's feeling. :'(
#Config.set('kivy', 'log_enable', 1)

#Creates a logger and sets it's debug level.
LOGGER = KivyLogger.getChild('Twitch-Plays-Bot')
LOGGER.level = logging.LOG_LEVELS['debug']

AUTOLOGGER = LOGGER.getChild('AutoLogger')
AUTOLOGGER.level = logging.LOG_LEVELS['debug']

#TODO: Have AutoLogger push events out to a queue then a seperate thread
#           should pull events off the queue and write them to a file.
#           this will hopefully speed up logging. As the logger wont
#           have to wait on the user's hard drive to continue on.
#           #NOTE: If we impliment this approach we will have to
#           log the AutoLogger's logs in a seperate file as the
#           AutoLogger and the manual logger could easily fall
#           out of sync using this method. (Unless we create a
#           custom handler to push logging events onto the queue
#           for the manual logger.(which sounds like the best option.))
class AutoLogger(object):
    """ AutoLogger class adds logging to the __setattr__
        methods to help make logging easier and more through
        at the same time.

        AutoLogger also emits a warning when changing an attribute
        from one type to another.
        To disable this functionality(Not Recommended!):
        set 'self.auto_logger_ignore_type_change = True'.

        Kivy makes a LOT of calls to __getattribute__ and on
        instantiation a lot of calls are made to 'self.__class__' as
        a result; we do not log __getattribute__ calls if they are
        coming from a kivy module not do we log __getattribute__ calls
        that are trying to get __class__. You can however enable this
        functionality if you set 'self.auto_logger_extremely_verbose = True'
        (The irony of this variable name is not lost on the developer of
        this module) WARNING!!! Enabling this feature will result in
        a massive performance hit, especially on startup! You have
        been warned!
    """

    #TODO: move these out to a config file.
    _ignore_type_change = False
    _extremely_verbose = False
    _is_setting = False
    _is_getting = False
    _is_disabled = True

    @property
    def auto_logger_ignore_type_change(self):
        """ _ignore_type_change getter method """
        return super(AutoLogger, self).__getattribute__('_ignore_type_change')

    @auto_logger_ignore_type_change.setter
    def ignore_type_change(self, value):
        """ _ignore_type_change setter method """
        super(AutoLogger, self).__setattr__('_ignore_type_change', value)

    @property
    def auto_logger_extremely_verbose(self):
        """ _extremely_verbose getter method """
        return super(AutoLogger, self).__getattribute__('_extremely_verbose')

    @auto_logger_extremely_verbose.setter
    def auto_logger_extremely_verbose(self, value):
        """ _extremely_verbose setter method """
        super(AutoLogger, self).__setattr__('_extremely_verbose', value)

    def __getattribute__(self, name):
        value = super(AutoLogger, self).__getattribute__(name)
        if not super(AutoLogger, self).__getattribute__('_is_disabled'):
            if name != '_is_setting' and \
               not super(AutoLogger, self).__getattribute__('_is_setting') and\
               not super(AutoLogger, self).__getattribute__('_is_getting') and\
               (name != '__class__' or super(AutoLogger,
                                             self).__getattribute__(
                                                 '_extremely_verbose')):
                super(AutoLogger, self).__setattr__('_is_getting', True)

                # Gets the currentframe and the call frame off the stack.
                curframe = inspect.currentframe()
                calframe = inspect.getouterframes(curframe, 2)

                # Gets a bunch of information about the object calling
                #    __setattr__ from the call frame.
                real_path = calframe[1][1]

                if '\\kivy\\' not in real_path or \
                  super(AutoLogger, self).__getattribute__('_extremely_verbose'):
                    real_line_no = calframe[1][2]
                    real_func = calframe[1][3]
                    previous_line = calframe[1][4][0].split('\n')[0]
                    real_line = calframe[1][4][1].split('\n')[0]

                    # If you are inheriting from AutoLogger;
                    #    __setattr__ should do sufficient logging
                    #    on it's own, and so we don't need to log.
                    # Calls the function that normally gets called when you
                    #    print(or log) 'self'
                    myself = super(AutoLogger, self).__repr__()

                    # Logs a message to let the log file know
                    #     we are about to start logging.
                    AUTOLOGGER.debug('')
                    AUTOLOGGER.debug('###AutoLogger### Starting: '\
                                     '\'__getattribute__\' '\
                                     'for %s.%s',
                                     super(AutoLogger, self).__repr__(),
                                     name)

                    #NOTE: Consider just iterating over the call frame and sending
                    #           it all out to the log.
                    # Logs some information about
                    #    the object calling __getattribute__.
                    AUTOLOGGER.debug(' + REALPATH ~ %-100s | REALFUNC ~ %-18s | ',
                                     real_path, real_func)
                    AUTOLOGGER.debug('Last two lines: ')
                    AUTOLOGGER.debug('REALLINENO: %5d | %s', real_line_no-1, previous_line)
                    AUTOLOGGER.debug('REALLINENO: %5d | %s', real_line_no, real_line)

                    # Log the some information about the object actually being
                    #    gotten.
                    AUTOLOGGER.debug('Getting -  %s.%s = %s(%s)',
                                     myself, name,
                                     type(value), value)
                    AUTOLOGGER.debug('###AutoLogger### Finishing: '\
                                     '\'__getattribute__\' '\
                                     'for %s.%s',
                                     super(AutoLogger, self).__repr__(),
                                     name)
                    AUTOLOGGER.debug('')
                super(AutoLogger, self).__setattr__('_is_getting', False)

        #Actually retuns the attribute i.e.(where the magic happens).
        return value

    def __setattr__(self, name, value):
        if not super(AutoLogger, self).__getattribute__('_is_disabled'):
            super(AutoLogger, self).__setattr__('_is_setting', True)
            myself = super(AutoLogger, self).__getattribute__('__repr__')()

            # Gets the currentframe and the call frame off the stack.
            curframe = inspect.currentframe()
            calframe = inspect.getouterframes(curframe, 2)

            # Gets a bunch of information about the object calling
            #    __setattr__ from the call frame.
            real_path = calframe[1][1]
            real_line_no = calframe[1][2]
            real_func = calframe[1][3]
            previous_line = calframe[1][4][0].split('\n')[0]
            real_line = calframe[1][4][1].split('\n')[0]

            # Logs a message to let the log file know we are about to start logging.
            AUTOLOGGER.debug('')
            AUTOLOGGER.debug('###AutoLogger### Starting: \'__setattr__\' '\
                             'for %s.%s', self, name)

            #NOTE: Consider just iterating over the call frame and sending
            #           it all out to the log.
            # Logs some information about the object calling __setattr__.
            AUTOLOGGER.debug(' + REALPATH ~ %s', real_path)
            AUTOLOGGER.debug(' + REALFUNC ~ %s', real_func)
            AUTOLOGGER.debug('Last two lines: ')
            AUTOLOGGER.debug('%5d : %s', real_line_no-1, previous_line)
            AUTOLOGGER.debug('%5d : %s', real_line_no, real_line)

            # Checks to see if we are setting an
            #   existing attribute, or creating a new one.
            if hasattr(self, name):
                # Logs the setting action about to occur.
                AUTOLOGGER.debug('Setting - %s.%s from %s(%s) to %s(%s)',
                                 myself, name,
                                 type(super(AutoLogger,
                                            self).__getattribute__(name)),
                                 super(AutoLogger, self).__getattribute__(name),
                                 type(value), value)
                if type(super(AutoLogger, self).__getattribute__(name)) !=\
                  type(value):
                    if super(AutoLogger, self).__getattribute__(name) is not ''\
                      and type(super(AutoLogger, self).__getattribute__(name)) !=\
                      type(None) and not self.ignore_type_change:
                        # Warns the logger if we are changing the type of an
                        #    existing variable. However; if the variable was just
                        #    an empty string we assume it's fine.
                        AUTOLOGGER.warning('Warning - The type of %s.%s '\
                                           'was changed from type %s to type %s. '\
                                           'Was this intentional?',
                                           myself,
                                           name,
                                           type( super(AutoLogger,
                                                       self).__getattribute__(name)),
                                           type(value))
            else:
                # Logs the creating of the new attribute that is about to occur.
                AUTOLOGGER.debug('Creating - %s.%s = %s', myself, name, value)

        # ACTUALLY sets the attribute (here is where the magic happens).
        super(AutoLogger, self).__setattr__(name, value)

        if not super(AutoLogger, self).__getattribute__('_is_disabled'):
            # Verifies that the setting has acctually occured.
            AUTOLOGGER.debug('Verifying - %s.%s = %s(%s)',
                             self, name,
                             type(super(AutoLogger, self).__getattribute__(name)),
                             super(AutoLogger, self).__getattribute__(name))

            # Logs a message to let the log file know we are done logging.
            AUTOLOGGER.debug('###Autologger### Finishing: \'__setattr__\' '\
                             'for %s.%s', self, name)
            AUTOLOGGER.debug('')
            super(AutoLogger, self).__setattr__('_is_setting', False)
