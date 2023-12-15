import functools
from time import perf_counter

def measure_time(func):
    """Вимірює час виконання функції."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = perf_counter()

        func(*args, **kwargs)

        end = perf_counter()
        measured_time = round(end - start, 5)

        print(f"Функцію {func.__name__} було виконано за {measured_time * 1000} мс")
    return wrapper

def sep_print_block(symbol):
    """Відокремлює блок друку з потрібними символами."""
    def inner_decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            separator = symbol * 42

            print(separator)

            func(*args, *kwargs)

            print(separator)
        return wrapper
    return inner_decorator