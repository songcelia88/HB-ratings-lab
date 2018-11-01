"""Pearson correlation."""

from math import sqrt


def pearson(pairs):
    """Return Pearson correlation for pairs.
    Using a set of pairwise ratings, produces a Pearson similarity rating.
    """

    # pairs is a list of tuples: [(p1,q1), (p2,q2), (p3,q3) ... ]
    # p is user1's ratings, q is user2's ratings, 
    # 1, 2, 3, etc. corresponds to the movie they both rated

    series_1 = [float(pair[0]) for pair in pairs] # p1, p2, ... pn
    series_2 = [float(pair[1]) for pair in pairs] # q1, q2, ... qn

    sum_1 = sum(series_1) # sum of all p's
    sum_2 = sum(series_2) # sum of all q's

    squares_1 = sum([n * n for n in series_1])
    squares_2 = sum([n * n for n in series_2])

    product_sum = sum([n * m for n, m in pairs])

    size = len(pairs)

    numerator = product_sum - ((sum_1 * sum_2) / size)

    denominator = sqrt(
        (squares_1 - (sum_1 * sum_1) / size) *
        (squares_2 - (sum_2 * sum_2) / size)
    )
    # print("numerator: ", numerator)
    # print("denominator: ", denominator)
    if denominator == 0:
        return 0

    return numerator / denominator
    # returns a number between -1 and 1 that signifies how similar p is to q (and vice versa)
