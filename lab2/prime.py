def find_prime(start: int, end: int):
    prime_list = []
    for num in range(start, end + 1):
        if is_prime(num):
            prime_list.append(num)

    return prime_list


def is_prime(num: int):
    if num > 1:
        for i in range(2, num):
            if (num % i) == 0:
                return False
        else:
            return True
    else:
        return False
