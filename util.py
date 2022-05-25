def make_predefined_multiply_factors():
    result = dict()
    # 12x12 times tables (excluding 1)
    for i, j in combinations_with_replacement([k+1 for k in range(1, 12)], 2):
        prod = i * j
        if prod not in result:
            result[prod] = list()
        result[prod].append((i, j))

    # We'll allow 'easy' multiplications up to a bound of 1000
    for i in ([2] + [k * 10 for k in range(1, 100)]):
        for j in range(13, 1000 // i):
            prod = i * j
            if prod not in result:
                result[prod] = list()
            result[prod].append((i, j))

    # We'll allow 'easy-ish' multiplications up to a bound of 200
    for i in [3, 4, 5, 11, 15]:
        for j in range(13, 200 // i):
            prod = i * j
            if prod not in result:
                result[prod] = list()
            result[prod].append((i, j))


    return result