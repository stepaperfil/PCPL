
import random

def gen_random(num_count, begin, end):
    for i in range(num_count):
        yield random.randint(begin, end)


if __name__ == '__main__':
    print("gen_random(5, 1, 3):")
    for num in gen_random(5, 1, 3):
        print(num, end=' ')
    print()