""" This module holds the main menu screen.
"""

#TODO: finish logging

from kivy.core.window import Window
from kivy.uix.screenmanager import Screen
from kivy.uix.relativelayout import RelativeLayout

from scripts.buttons.commands_button import CommandsButton
from scripts.buttons.exit_button import ExitButton
from scripts.logger import LOGGER

class MainMenu(Screen, RelativeLayout):
    """ This is the main menu Widget which holds the main menu.

        #TODO: doctest here.
    """
    def __init__(self, *args, **kwargs):
        """ Method gets called when class in instantiated.
        """
        LOGGER.info('Running - %s.__init__(%s, %s)',
                    self, args, kwargs)

        #Calls inherited classes __init__() functions for consistency.
        LOGGER.debug('Calling - '\
                     'super(MainMenu, %s).__init(%s, %s)',
                     self, args, kwargs)
        super(MainMenu, self).__init__(*args, **kwargs)

        #Makes self._on_resize get called when Window.on_resize gets called.
        LOGGER.debug('Calling - %s.bind(on_resize=%s._onresize)', Window, self)
        Window.bind(on_resize=self._on_resize)

        #Creates the Command Button and sets it as a child of self.
        self._commands_button = CommandsButton()
        LOGGER.debug('Declared - %s._commands_button = %s',
                     self, self._commands_button)
        self._commands_button.text = "Commands"
        LOGGER.debug('Declared - '\
                     '%s._commands_button.test = %s(%s)',
                     self,
                     type(self._commands_button.text),
                     self._commands_button.text)
        LOGGER.debug('Calling - %s.add_widget( %s(%s) )',
                     self, type(self._commands_button), self._commands_button)
        self.add_widget(self._commands_button)

        #Creates the Exit Button and sets it as a child of self.
        self._exit_button = ExitButton()
        LOGGER.debug('Declared - %s._exit_button = %s(%s)',
                     self, type(self._exit_button), self._exit_button)
        self._exit_button.text = "Exit"
        LOGGER.debug('Declared - %s._exit_button.test = %s(%s)', self,
                     type(self._exit_button.text), self._exit_button.text)
        LOGGER.debug('Calling - %s.add_widget(%s(%s))', self,
                     type(self._exit_button), self._exit_button)
        self.add_widget(self._exit_button)

        #Initializes screen's size and position by calling self._on_resize().
        LOGGER.debug('Calling - %s._on_resize(%s(%s), %s(%s), %s(%s))',
                     self,
                     type(Window), Window,
                     type(Window.width), Window.width,
                     type(Window.height), Window.height)
        self._on_resize(Window, Window.width, Window.height)

        #NOTE: Not used anymore, left in incase it's needed in the future.
        #Calls all children's on_start method.
        LOGGER.debug('Iterating - for child in %s.%s(%s)',
                     self, type(self.children), self.children)
        for child in self.children:
            childs_start = getattr(child, 'on_start', None)
            LOGGER.debug('Declared - childs_start = %s(%s)',
                         type(childs_start), childs_start)
            if callable(childs_start):
                LOGGER.debug('Calling - %s(%s)',
                             type(childs_start), childs_start)
                childs_start()

    def _on_resize(self, sdl2_handle, width, height):
        """ Method gets called when the window gets resized

            #TODO: doctest here
        """

        LOGGER.info('Running - %s._on_resize(%s(%s), %s(%s), %s(%s))',
                    self,
                    type(sdl2_handle), sdl2_handle,
                    type(width), width,
                    type(height), height)

        #Sets the size of the Screen to be that of the Window.
        self.size = (width, height)
        LOGGER.debug('Declared - %s.size = %s(%s)',
                     self, type(self.size), self.size)

        #Centers the Screen inside the Window
        self.center = (width/2, height/2)
        LOGGER.debug('Declared - %s.center = %s(%s)',
                     self, type(self.center), self.center)

        #Calls all children's on_resize method.
        LOGGER.debug('Iterating - for child in %s.%s(%s)',
                     self, type(self.children), self.children)
        for child in self.children:
            childs_on_resize = getattr(child, 'on_resize', None)
            LOGGER.debug('Declared - childs_on_resize = %s(%s)',
                         type(childs_on_resize), childs_on_resize)
            if callable(childs_on_resize):
                LOGGER.debug('Calling - '\
                             'childs_on_resize(%s(%s), %s(%s), %s(%s)',
                             type(sdl2_handle), sdl2_handle,
                             type(width), width,
                             type(height), height)
                childs_on_resize(sdl2_handle, width, height)

        LOGGER.info('Returning - %s, %s(%s), %s(%s), %s(%s)',
                    self,
                    type(sdl2_handle), sdl2_handle,
                    type(width), width,
                    type(height), height)
        #Returns the function's inputs.
        return self, sdl2_handle, width, height
