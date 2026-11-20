K-means and dynamic time warping
===================================

K-means selects representative periods. DTW aligns two sequences that can
progress at different rates. They are independent operations in Vaelchi.

Representative periods with k-means
--------------------------------------

These four days alternate between low and high demand. Each day has two
timesteps. K-means groups similar days even when they are not adjacent:

.. code-block:: python

   from vaelchi import ClusterResult, kmeans

   result = kmeans(
       [0, 1, 10, 11, 0, 1, 10, 11],
       periods=2,
       period_length=2,
       random_state=0,
   )
   print(result.labels.tolist())                 # [0, 1, 0, 1]
   print(result.representative_indices.tolist()) # [0, 1]
   print(result.weights.tolist())                # [2, 2]
   print(isinstance(result, ClusterResult))      # True
   reconstructed = result.reconstruct()         # shape (8, 1)
   payload = result.to_dict()

Pass additional aligned series as positional arguments to add features.
Use ``parent_length=365`` with ``period_length=24`` to fit each complete
365-day year independently. Scaling is per feature/timestep column within
each parent. Representatives are actual observed periods in the original
units, with nearest-centroid ties resolved chronologically.

The default uses ten k-means++ starts and a fixed seed. Increase ``n_init``
to try more starts, or set ``random_state=None`` for random starts between
calls. A parent must contain enough distinct profiles for the requested
cluster count. Cluster labels reconstruct the original ordering, but k-means
does not impose AHC's temporal-adjacency constraint.

Existing AHC callers retain ``AHCResult``. It is also a ``ClusterResult``,
so either algorithm supports the same reconstruction and dictionary methods.
``inertia`` measures squared distance to the final cluster means;
``reconstruction_error`` measures squared distance to the selected observed
profiles. Both are measured in standardized space. Weighted representative
totals equal reconstructed totals, not necessarily the original input totals.

Aligning sequences with DTW
------------------------------

.. code-block:: python

   from vaelchi import dtw, dtw_matrix, dtw_path

   alignment = dtw([0, 10], [10])
   print(alignment.distance)       # 10.0
   print(alignment.path.tolist())  # [[0, 0], [1, 0]]
   payload = alignment.to_dict()

   matrix = dtw_matrix([0, 10], [10])
   path = dtw_path(matrix)         # same path as alignment.path

Both sequence endpoints participate. Path rows contain zero-based source and
target positions in chronological order; an index can repeat while the other
sequence advances. Distance is the sum of absolute differences along the path.
The original Energia convention is retained: no squared-distance cost, square
root, scaling, or length normalization is applied.

DTW supports unequal lengths and leaves inputs unchanged. Empty, nonfinite,
and multidimensional sequences are rejected. The exact implementation uses
O(n*m) time and memory, so it is intended initially for short profiles. The
padded cost matrix contains infinity at unreachable borders; use the result's
``to_dict()`` for portable JSON containing only the finite distance and path.

Runnable example
--------------------

.. literalinclude:: ../../examples/kmeans_and_dtw.py
   :language: python
