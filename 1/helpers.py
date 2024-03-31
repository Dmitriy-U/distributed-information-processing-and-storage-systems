def get_prime_numbers(start, end) -> [int]:
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
