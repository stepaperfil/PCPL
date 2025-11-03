import sys
import math


def get_float_input(prompt):
    while True:
        try:
            value = float(input(prompt))
            return value
        except ValueError:
            print("Некорректное значение. Пожалуйста, введите действительное число.")



a = None
b = None
c = None

if len(sys.argv) == 4:
    try:
        a = float(sys.argv[1])
    except ValueError:
        print("Некорректный коэффициент A в командной строке. Будет запрошен ввод с клавиатуры.")

    try:
        b = float(sys.argv[2])
    except ValueError:
        print("Некорректный коэффициент B в командной строке. Будет запрошен ввод с клавиатуры.")

    try:
        c = float(sys.argv[3])
    except ValueError:
        print("Некорректный коэффициент C в командной строке. Будет запрошен ввод с клавиатуры.")


if a is None:
    a = get_float_input("Введите коэффициент A: ")


if b is None:
    b = get_float_input("Введите коэффициент B: ")


if c is None:
    c = get_float_input("Введите коэффициент C: ")


if a == 0:
    print("Коэффициент A не может быть равен нулю. Это не квадратное уравнение.")
    sys.exit(1)


d = b ** 2 - 4 * a * c

print(f"Дискриминант D = {d}")

if d > 0:
    sqrt_d = math.sqrt(d)
    x1 = (-b + sqrt_d) / (2 * a)
    x2 = (-b - sqrt_d) / (2 * a)
    print(f"Два действительных корня:")
    print(f"x1 = {x1}")
    print(f"x2 = {x2}")
elif d == 0:
    x = -b / (2 * a)
    print(f"Один действительный корень:")
    print(f"x = {x}")
else:
    print("Нет действительных корней.")
