"""Historical numeric helpers for distance and connectivity calculations."""

import numpy


# Adapted from revision e7704752 by OpenAI Codex (GPT-6).
def find_euclidean_distance(a: list, b: list) -> float:
    """
    finds euclidean distances between two cluster nodes

    :param a: coordinates of cluster node a
    :type a: list
    :param b: coordinates of cluster node b
    :type b: list

    :returns: euclidean distance
    :rtype: float
    """
    distance_ = [(a - b) ** 2 for a, b in zip(a, b)]
    return sum(distance_)


# Adapted from revision e7704752 by OpenAI Codex (GPT-6).
def generate_connectivity_matrix(scale_len) -> numpy.ndarray:
    """
    Generates a connectivity matrix to maintain chronology [..1,0,1..]

    :param scale_len: length of the scale
    :type scale_len: int

    :returns: connectivity matrix
    :rtype: numpy.array
    """
    connect_ = numpy.zeros((scale_len, scale_len), dtype=int)
    for i_ in range(len(connect_)):
        if i_ == 0:
            # connect_[i,364] = 1 #uncomment these to generate a cyclic matrix
            connect_[i_, 1] = 1
        elif i_ == scale_len - 1:
            connect_[i_, scale_len - 2] = 1
            # connect_[i,0] = 1
        else:
            connect_[i_, i_ - 1] = 1
            connect_[i_, i_ + 1] = 1
    return connect_
