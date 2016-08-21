from kivy.app import App
from kivy.core.window import Window
from kivy.uix.widget import Widget
from Scripts.MainMenu import MainMenu
import random

class GameApp(App):
    def build(self):
        #For Random Aspect Ratio Testing...
        Window.size = (random.randint(500, 1000), random.randint(500, 1000))
        #Window.size = (300, 500)
        self.title = 'Twitch Plays Bot'
        #self.icon = 'Images/Piece.png'
        return MainMenu()
        
if __name__ == "__main__":
    GameApp().run()