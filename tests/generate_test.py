"""Verify exact neighbor connections for cyclic and non-cyclic periods."""

from numpy.testing import assert_array_equal

#  use the renamed public package.
from vael.functions.generate import connectivity_matrix


def test_connectivity_matrix():
    """Match both boundary policies against explicit adjacency matrices."""
    # Test non-cyclic connectivity matrix
    expected_non_cyclic = [
        [0, 1, 0, 0, 0],
        [1, 0, 1, 0, 0],
        [0, 1, 0, 1, 0],
        [0, 0, 1, 0, 1],
        [0, 0, 0, 1, 0],
    ]
    assert_array_equal(connectivity_matrix(5), expected_non_cyclic)

    # Test cyclic connectivity matrix
    expected_cyclic = [
        [0, 1, 0, 0, 1],
        [1, 0, 1, 0, 0],
        [0, 1, 0, 1, 0],
        [0, 0, 1, 0, 1],
        [1, 0, 0, 1, 0],
    ]
    assert_array_equal(connectivity_matrix(5, cyclic=True), expected_cyclic)
