import sys
from colorama import init, Fore, Style


def main() -> int:

    N = 18

    init()

    from lab_python_oop.rectangle import Rectangle
    from lab_python_oop.circle import Circle
    from lab_python_oop.square import Square

    rect = Rectangle(N, N, "синий")
    circ = Circle(N, "зеленый")
    sqr = Square(N, "красный")

    print(Fore.CYAN + "=" * 60 + Style.RESET_ALL)
    print(Fore.CYAN + "ТЕСТИРОВАНИЕ ГЕОМЕТРИЧЕСКИХ ФИГУР" + Style.RESET_ALL)
    print(Fore.CYAN + "=" * 60 + Style.RESET_ALL)

    print(Fore.WHITE + str(rect) + Style.RESET_ALL)
    print(Fore.BLUE + str(circ) + Style.RESET_ALL)
    print(Fore.RED + str(sqr) + Style.RESET_ALL)

    print(Fore.CYAN + "=" * 60 + Style.RESET_ALL)
    print(Fore.YELLOW + "✓ Использование внешнего пакета COLORAMA:" + Style.RESET_ALL)
    print(Fore.YELLOW + "  ЦВЕТНОЙ ВЫВОД УСПЕШНО РЕАЛИЗОВАН!" + Style.RESET_ALL)
    print(Fore.CYAN + "=" * 60 + Style.RESET_ALL)

    return 0


if __name__ == '__main__':
    sys.exit(main())