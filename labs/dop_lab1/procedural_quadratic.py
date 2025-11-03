
import sys
import math

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

def compute_discriminant(a, b, c):
    return b*b - 4*a*c

def print_solution(a, b, c):

    if a == 0:
        print("Коэффициент A не может быть равен нулю. Это не квадратное уравнение.")
        sys.exit(1)

    d = compute_discriminant(a, b, c)
    print(f"Дискриминант D = {d}")

    if d > 0:
        sqrt_d = math.sqrt(d)
        x1 = (-b + sqrt_d) / (2 * a)
        x2 = (-b - sqrt_d) / (2 * a)
        print("Два действительных корня:")
        print(f"x1 = {x1}")
        print(f"x2 = {x2}")
    elif d == 0:
        x = -b / (2 * a)
        print("Один действительный корень:")
        print(f"x = {x}")
    else:
        print("Нет действительных корней.")

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

    print_solution(a, b, c)

if __name__ == "__main__":
    main()
