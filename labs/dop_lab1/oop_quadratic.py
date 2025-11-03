
import sys
import math
from dataclasses import dataclass

class NotQuadraticError(ValueError):
    pass

@dataclass
class QuadraticEquation:
    a: float
    b: float
    c: float

    def validate(self):
        if self.a == 0:
            raise NotQuadraticError("Коэффициент A не может быть равен нулю. Это не квадратное уравнение.")

    def discriminant(self) -> float:
        return self.b*self.b - 4*self.a*self.c

    def real_roots(self):

        self.validate()
        d = self.discriminant()
        if d > 0:
            sqrt_d = math.sqrt(d)
            x1 = (-self.b + sqrt_d) / (2 * self.a)
            x2 = (-self.b - sqrt_d) / (2 * self.a)
            return [x1, x2]
        elif d == 0:
            return [-self.b / (2 * self.a)]
        else:
            return []

    def describe(self):

        try:
            d = self.discriminant()
            lines = [f"Дискриминант D = {d}"]
            roots = self.real_roots()
            if len(roots) == 2:
                lines.append("Два действительных корня:")
                lines.append(f"x1 = {roots[0]}")
                lines.append(f"x2 = {roots[1]}")
            elif len(roots) == 1:
                lines.append("Один действительный корень:")
                lines.append(f"x = {roots[0]}")
            else:
                lines.append("Нет действительных корней.")
            return "\n".join(lines)
        except NotQuadraticError as e:
            return str(e)

def get_float_input(prompt, input_func=input):
    while True:
        try:
            return float(input_func(prompt))
        except ValueError:
            print("Некорректное значение. Пожалуйста, введите действительное число.")

def parse_args(argv):
    a = b = c = None
    if len(argv) == 4:
        for i, name in [(1, "A"), (2, "B"), (3, "C")]:
            try:
                val = float(argv[i])
            except ValueError:
                print(f"Некорректный коэффициент {name} в командной строке. Будет запрошен ввод с клавиатуры.")
                val = None
            if i == 1:
                a = val
            elif i == 2:
                b = val
            else:
                c = val
    return a, b, c

def main(argv=None, input_func=input):
    if argv is None:
        argv = sys.argv

    a, b, c = parse_args(argv)
    if a is None:
        a = get_float_input("Введите коэффициент A: ", input_func)
    if b is None:
        b = get_float_input("Введите коэффициент B: ", input_func)
    if c is None:
        c = get_float_input("Введите коэффициент C: ", input_func)

    eq = QuadraticEquation(a, b, c)
    print(eq.describe())

if __name__ == "__main__":
    main()
