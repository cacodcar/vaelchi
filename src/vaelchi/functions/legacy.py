"""Historical numeric helpers for distance and connectivity calculations."""

import numpy
import pandas as pd


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


def remove_outliers(
    data: pd.DataFrame,
    sd_cuttoff: int = 2,
    mean_range: int = 1,
) -> pd.DataFrame:
    """
    Apply Energia's historical sequential outlier replacement in place.

    Ported from TAMUparametric/energiapy revision
    308f965f45cd8c1f80b2b950cebe024d64d69e39, utils/data.py (MIT).
    The first column determines which rows are replaced; replacement applies
    to every column. Thresholds use the original sample mean and standard
    deviation, while neighbours include earlier replacements.

    This compatibility function retains the historical limitations. Use a
    single column, mean_range=1, and interior outliers for neighbour means.
    Negative positions wrap at the start; positions beyond the end raise
    IndexError. Larger windows retain the original sum / 2 * mean_range
    expression, which is not the neighbour mean. The input is modified and
    returned; an error can leave earlier replacements applied.

    Parameters
    ----------
    data : :class:`pandas.DataFrame`
        Input data.
    sd_cuttoff : :class:`int`, optional
        Replace rows beyond this many standard deviations in the first
        column. Defaults to ``2``.
    mean_range : :class:`int`, optional
        Number of neighbouring positions on each side. Defaults to ``1``.
        Larger values preserve the historical expression described above.

    Returns
    -------
    :class:`pandas.DataFrame`
        The input DataFrame after sequential replacements.

    """
    data_mean, data_std = data.mean(), data.std()
    # identify outliers
    cut_off = data_std * sd_cuttoff
    lower, upper = data_mean - cut_off, data_mean + cut_off
    for i in range(len(data)):
        x = data.iloc[i].values[0]
        if x < float(lower.iloc[0]) or x > float(upper.iloc[0]):
            data.iloc[i] = (
                (
                    sum(data.iloc[i - (j + 1)] for j in range(mean_range))
                    + sum(data.iloc[i + (j + 1)] for j in range(mean_range))
                )
                / 2
                * mean_range
            )
    return data
