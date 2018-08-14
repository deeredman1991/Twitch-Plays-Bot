""" This module holds the main menu screen.
"""

#pylint: disable=locally-disabled, too-many-ancestors

import os

from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.dropdown import DropDown
from kivy.core.window import Window

from scripts.screen import Screen


class MainMenu(Screen):
    """ This is the main menu Screen which holds the main menu.

        #TODO: doctest here.
    """
    def __init__(self, *args, **kwargs):
        """ Method gets called when class in instantiated.
        """
        super(MainMenu, self).__init__(*args, **kwargs)
        self.created = False
    def on_enter(self):
        if not self.created:
            bx = self.make_box(self)

            top = self.make_box(bx, o='horizontal', sy=0.3)

            self.make_box(top, sx=0.8)

            drop_down_holder = self.make_box(top, sx=0.1, sy=0.2)

            drop_down_holder.add_widget( self.make_dropdown() )

            self.make_box(drop_down_holder, sy=0.8)

            self.make_box(top, sx=0.1)

            mid = self.make_box(bx, o='horizontal', sy=0.4)

            left_mid_spacer = self.make_box(mid, sx=0.4)

            button_holder = self.make_box(mid, sx=0.6)

            #Creates the Start Session button and sets it as a child of self.
            session_button = self.make_button( button_holder, 'Start Session', self.session_button_on_press, sy=0.1 )

            #Creates the Command Button and sets it as a child of self.
            settings_button = self.make_button( button_holder, 'Settings', self.settings_button_on_press, sy=0.1 )

            #Creates the Exit Button and sets it as a child of self.
            exit_button = self.make_button( button_holder, 'Exit', self.exit_button_on_press, sy=0.1 )

            right_mid_spacer = self.make_box(mid, sx=0.4)

            bottom_spacer = self.make_box(bx, sy=0.3)

    def make_dropdown(self):
        self.dropdown = DropDown()
        for folder in os.listdir( self.parent.cfg_path ):
            if '.' not in folder:
                # When adding widgets, we need to specify the height manually
                # (disabling the size_hint_y) so the dropdown can calculate
                # the area it needs.

                btn = Button(text=folder, size_hint_y=None, height=44)

                # for each button, attach a callback that will call the select() method
                # on the dropdown. We'll pass the text of the button as the data of the
                # selection.
                btn.bind(on_release=lambda btn: self.dropdown.select(btn.text))

                # then add the button inside the dropdown
                self.dropdown.add_widget(btn)
        
        # create a big main button
        mainbutton = Button(text=self.parent.profile, size_hint=(None, None), height=44)

        # show the dropdown menu when the main button is released
        # note: all the bind() calls pass the instance of the caller (here, the
        # mainbutton instance) as the first argument of the callback (here,
        # dropdown.open.).
        mainbutton.bind(on_release=self.dropdown.open)

        def profile_select(instance, x):
           setattr(mainbutton, 'text', x)
           self.parent.profile = x
        # one last thing, listen for the selection in the dropdown list and
        # assign the data to the button text.
        self.dropdown.bind( on_select=profile_select )

        return mainbutton

    def session_button_on_press(self):
        screen_manager = self.parent
        #main_menu = screen_manager.get_screen('Main Menu')
        screen_manager.current = 'Session'

    def settings_button_on_press(self):
        #Creates a string equal to %cd%/configs/commands.json
        _user_commands_file = str(os.getcwd()) + '/configs/' +\
                self.parent.profile + '/user_commands.json'

        #executes the string created earlier as a console command.
        os.startfile(_user_commands_file)
        
    def exit_button_on_press(self):
        Window.close()
        