""" This module holds the generic 'Button' class that all buttons should
    inherit from.
"""

from kivy.uix.button import Button as KivyButton

from scripts.logger import AutoLogger

class Button(KivyButton, AutoLogger):
    """ This is the generic 'Button' class that all buttons should
        inherit from.
    """
    pass
