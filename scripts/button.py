""" This module holds the generic 'Button' class that all buttons should
    inherit from.
"""

from kivy.uix.button import Button as KivyButton

from scripts.logger import AutoLogger

class Button(KivyButton, AutoLogger):
    """ This is the generic 'Button' class that all buttons should
        inherit from.
    """

    def scale_and_center(self, width, height):
        neighbors = self.parent.children
        my_index = neighbors.index(self)

        self.center = (width/2, (height/2)+(self.height*my_index+1))

    def on_resize(self, sdl2_handle, width, height):
        self.scale_and_center(width, height)



