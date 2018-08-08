""" This module holds the generic 'Button' class that all buttons should
    inherit from.
"""

from kivy.uix.button import Button as KivyButton

class Button(KivyButton):
    """ This is the generic 'Button' class that all buttons should
        inherit from.
    """

    def scale_and_center(self, width, height):
        neighbors = self.parent.children
        num_neighbors = len(neighbors)
        my_index = neighbors.index(self)

        self.center = (width*0.5, (height*0.5)+((self.height*my_index+1)-\
                                                (self.height*num_neighbors/2)))

    def on_resize(self, sdl2_handle, width, height):
        self.scale_and_center(width, height)



