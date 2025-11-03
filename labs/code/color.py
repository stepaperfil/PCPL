class Color:

    def __init__(self, color_name):
        self._color_name = color_name

    @property
    def color_name(self):
        return self._color_name