from .rectangle import Rectangle


class Square(Rectangle):

    FIGURE_NAME = "Квадрат"

    def __init__(self, side, color):
        super().__init__(side, side, color)

    def __repr__(self):
        return (
            "{name} со стороной {side:0.2f}, "
            "цветом {color}, площадью {area:0.2f}"
        ).format(
            name=self.FIGURE_NAME,
            side=self.width,
            color=self.color.color_name,
            area=self.get_area()
        )