from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.uix.button import Button



class MainMenu(Widget):
    def __init__(self):
        super(MainMenu, self).__init__()
        
        Window.bind(on_resize=self._on_resize)
        
        self.configButton = ConfigButton()
        self.configButton.text = "Config"
        
        self.add_widget(self.configButton)
        
        self._on_resize()
        
    def _on_resize(self, *ignore):
        self.size = Window.size
        self.configButton.height = Window.height/10
        self.configButton.width = Window.width/10
        self.configButton.font_size = self.configButton.width/7
        self.configButton.center = self.center
        
        
class ConfigButton(Button):
    def __init__(self):
        super(ConfigButton, self).__init__()
        
    def on_press(self, *ignore):
        #Need to use screen manager
        self.parent.right = 0
        self.parent._on_resize()
        print (self.parent.pos)