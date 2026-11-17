"""Measures (of distances usually)"""


def euclidean_distance(a: list, b: list) -> float:
    """
    finds euclidean distances between two cluster nodes

    :param a: coordinates of cluster node a
    :type a: list
    :param b: coordinates of cluster node b
    :type b: list

    :returns: euclidean distance
    :rtype: float
    """
    return sum([(a - b) ** 2 for a, b in zip(a, b)])
