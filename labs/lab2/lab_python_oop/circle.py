import math
from .figure import Figure
from .color import Color


class Circle(Figure):


    FIGURE_NAME = "Круг"

    def __init__(self, radius, color):
        self.radius = radius
        self.color = Color(color)

    def get_area(self):
        return math.pi * self.radius ** 2

    def __repr__(self):
        return (
            "{name} радиусом {radius:0.2f}, "
            "цветом {color}, площадью {area:0.2f}"
        ).format(
            name=self.FIGURE_NAME,
            radius=self.radius,
            color=self.color.color_name,
            area=self.get_area()
        )
