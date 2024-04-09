import math


def get_prime_numbers(start, end) -> list[int]:
    """
    Найти натуральные числа в диапазоне
    :param start: начало диапазона поиска
    :param end: конец диапазона поиска
    :return: найденные натуральные числа
    """

    result = []

    for number in range(start, end + 1):
        if number < 0 or number == 0 or number == 1:
            continue

        if all(number % i != 0 for i in range(2, int(number ** 0.5) + 1)):
            result.append(number)

    return result


def get_ranges_by_number_of_workers(number_of_workers: int, prime_range_start: int, prime_range_end: int) -> list[tuple[int]]:
    """
    Получить диапазоны в зависимости от количества рабочих
    :param number_of_workers: количество рабочих
    :param prime_range_start: начало диапазона поиска
    :param prime_range_утв: конец диапазона поиска
    :return: список с диапазонами поиска
    """
    
    digit_quantity = prime_range_end - prime_range_start

    digit_part = math.ceil(digit_quantity / number_of_workers)

    tasks = []
    
    for worker_index in range(number_of_workers):
        worker_prime_range_start = prime_range_start + worker_index * digit_part
        if number_of_workers == worker_index + 1:
            worker_prime_range_end = prime_range_end
        else:
            worker_prime_range_end = (prime_range_start + (worker_index + 1) * digit_part) - 1
        
        tasks.append((worker_prime_range_start, worker_prime_range_end,))
        