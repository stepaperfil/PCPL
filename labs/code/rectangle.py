from .figure import Figure
from .color import Color


class Rectangle(Figure):

    FIGURE_NAME = "Прямоугольник"

    def __init__(self, width, height, color):
        self.width = width
        self.height = height
        self.color = Color(color)

    def get_area(self):
        return self.width * self.height

    def __repr__(self):
        return (
            "{name} шириной {width:0.2f}, высотой {height:0.2f}, "
            "цветом {color}, площадью {area:0.2f}"
        ).format(
            name=self.FIGURE_NAME,
            width=self.width,
            height=self.height,
            color=self.color.color_name,
            area=self.get_area()
        )