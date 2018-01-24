""" This module holds the main menu screen.
"""

#TODO impliment logging

from kivy.core.window import Window
from kivy.uix.screenmanager import Screen
from kivy.uix.relativelayout import RelativeLayout

from scripts.buttons.commands_button import CommandsButton
from scripts.buttons.exit_button import ExitButton

class MainMenu(Screen, RelativeLayout):
    """ This is the main menu Widget which holds the main menu.

        #TODO: doctest here.
    """
    def __init__(self, *args, **kwargs):
        """ Method gets called when class in instantiated.
        """

        #Calls inherited classes __init__() functions for consistency.
        super(MainMenu, self).__init__(*args, **kwargs)

        #Makes self._on_resize get called when Window.on_resize gets called.
        Window.bind(on_resize=self._on_resize)

        #Creates the Command Button and sets it as a child of self.
        self._commands_button = CommandsButton()
        self._commands_button.text = "Commands"
        self.add_widget(self._commands_button)

        #Creates the Exit Button and sets it as a child of self.
        self._exit_button = ExitButton()
        self._exit_button.text = "Exit"
        self.add_widget(self._exit_button)

        #Initializes screen's size and position by calling self._on_resize().
        self._on_resize(Window, Window.width, Window.height)

        #Calls all children's on_start method.
        for child in self.children:
            childs_start = getattr(child, 'on_start', None)
            if callable(childs_start):
                childs_start()

    def _on_resize(self, sdl2_handle, width, height):
        """ Method gets called when the window gets resized

            #TODO: doctest here
        """

        #Sets the size of the Screen to be that of the Window.
        self.size = (width, height)

        #Centers the Screen inside the Window
        self.center = (width/2,
                       height/2)

        #Calls all children's on_resize method.
        for child in self.children:
            childs_on_resize = getattr(child, 'on_resize', None)
            if callable(childs_on_resize):
                childs_on_resize(sdl2_handle, width, height)

        #Returns the function's inputs.
        return self, sdl2_handle, width, height
