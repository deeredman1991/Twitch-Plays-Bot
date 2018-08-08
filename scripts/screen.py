""" This module contains the Screen class that all screens will inherit from.
"""

#pylint: disable=locally-disabled, too-many-ancestors

from functools import partial

from kivy.graphics import BorderImage
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.screenmanager import Screen as KivyScreen


class Screen(KivyScreen):
    """ This is the main Screen class which all screens will inherit from.

        #TODO: doctest here.
    """
    def __init__(self, *args, **kwargs):
        """ Gets called when a screen is created.
            inheriting objects should call super AFTER
            child gui elements are assigned.
        """

        self.background = BorderImage(source='images/generic_background.png')

        #Sets self._on_resize to get called when Window.on_resize gets called.
        Window.bind(on_resize=self._on_resize)

        #Calls inherited classes __init__() function.
        super(Screen, self).__init__(*args, **kwargs)

    def on_pre_enter(self, *args, **kwargs):
        self.canvas.before.add(self.background)
        self._scale_and_center(Window.width, Window.height)
        print(self)

    def _scale_and_center(self, width, height):
        """ Method gets called whenever the screen needs to
            reset it's size and center.
        """
        self.size = (width, height)
        self.center = (width*0.5, height*0.5)

        self.background.size = self.size
        self.background.pos = self.pos

        #NOTE: For some reason this doesn't work unless it's on a clock.
        Clock.schedule_once(partial(self._scale_and_size_children, width, height) )

    def _scale_and_size_children(self, width, height, dt):
        for child in self.children:
            childs_scale_and_center = getattr(child, 'scale_and_center', None)
            if callable(childs_scale_and_center):
                childs_scale_and_center(width, height)

    def _on_resize(self, sdl2_handle, width, height):
        """ Method gets called when the window gets resized.

            #TODO: doctest here
        """

        self._scale_and_center(width, height)
