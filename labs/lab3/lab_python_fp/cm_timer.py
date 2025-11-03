
import time
from contextlib import contextmanager



class cm_timer_1:
    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, *args):
        elapsed = time.time() - self.start
        print(f'time: {elapsed:.1f}')



@contextmanager
def cm_timer_2():
    start = time.time()
    try:
        yield
    finally:
        elapsed = time.time() - start
        print(f'time: {elapsed:.1f}')


if __name__ == '__main__':
    from time import sleep

    print("=== cm_timer_1 (КЛАСС) ===")
    with cm_timer_1():
        sleep(1.5)

    print("\n=== cm_timer_2 (contextlib) ===")
    with cm_timer_2():
        sleep(1.5)