from gen_random import gen_random


class Unique(object):
    def __init__(self, items, **kwargs):
        self.items = items
        self.ignore_case = kwargs.get('ignore_case', False)
        self.seen = set()
        self.iterator = iter(items)

    def __next__(self):
        while True:
            current = next(self.iterator)

            if self.ignore_case and isinstance(current, str):
                key = current.lower()
            else:
                key = current

            if key not in self.seen:
                self.seen.add(key)
                return current

    def __iter__(self):
        return self


if __name__ == '__main__':

    data1 = [1, 1, 1, 1, 1, 2, 2, 2, 2, 2]
    print("Unique(data1):")
    for value in Unique(data1):
        print(value)

    print("\nUnique(gen_random(10, 1, 3)):")
    for value in Unique(gen_random(10, 1, 3)):
        print(value)

    data3 = ['a', 'A', 'b', 'B', 'a', 'A', 'b', 'B']
    print("\nUnique(data3):")
    for value in Unique(data3):
        print(value)

    print("\nUnique(data3, ignore_case=True):")
    for value in Unique(data3, ignore_case=True):
        print(value)