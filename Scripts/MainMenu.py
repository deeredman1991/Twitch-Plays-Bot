from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.uix.button import Button



class MainMenu(Widget):
    def __init__(self):
        super(MainMenu, self).__init__()
        
        Window.bind(on_resize=self._on_resize)
        self.size = Window.size
        
        self.test_button = Button()
        self.add_widget(self.test_button)
        
        self._on_resize()
        
    def _on_resize(self, *ignore):
        self.test_button.text = "Test Button"
        self.test_button.height = Window.height/10
        self.test_button.width = Window.width/10
        self.test_button.font_size = self.test_button.width/7
        self.test_button.center = self.center