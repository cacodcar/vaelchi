"""Other Functions"""


def normalize(data: list, how: str = "max") -> list:
    """
    min max normalization of data

    :param data: time-series data
    :type data: list
    :param how: min-max or max, defaults to "max"
    :type how: str, optional

    :return: normalized data
    :rtype: list
    """
    if all(isinstance(i, tuple) for i in data):
        # lower bound
        lb = [i[0] for i in data]
        # upper bound
        ub = [i[1] for i in data]
        # normalize lower and upper bounds individually
        lb_norm = normalize(lb, how=how)
        ub_norm = normalize(ub, how=how)
        return list(zip(lb_norm, ub_norm))

    if how == "min_max":
        min_ = min(data)
        max_ = max(data)
        return [(i - min_) / (max_ - min_) for i in data]

    if how == "max":
        return [
            normalize(i) if isinstance(i, list) else i / max(data)
            for i in data
        ]

    message = "Invalid normalization method. Use 'min_max' or 'max'."
    raise ValueError(message)
