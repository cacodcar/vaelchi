"""Generate (matrices and such)"""

from numpy import eye, ndarray


def connectivity_matrix(size: int, cyclic: bool = False) -> ndarray:
    """
    Generates a connectivity matrix to maintain chronology [..1,0,1..]

    :param size: length of the scale
    :type size: int
    :param cyclic: whether to create a cyclic matrix, defaults to False
    :type cyclic: bool, optional

    :returns: connectivity matrix
    :rtype: numpy.ndarray
    """

    _matrix = eye(size, k=1, dtype=int) + eye(size, k=-1, dtype=int)

    if cyclic:
        # if cyclic last period, cycles to first
        _matrix[0, size - 1] = 1
        _matrix[size - 1, 0] = 1

    return _matrix
