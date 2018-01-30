from kivy.uix.image import Image

class Sprite(Image):
    def __init__(self, **kwargs):
        super(Sprite, self).__init__(allow_stretch = True, **kwargs)
        self.texture.mag_filter = 'nearest'
        w, h = self.texture_size

        self.scale = 1
        self.size = (self.scale * w, self.scale * h)
