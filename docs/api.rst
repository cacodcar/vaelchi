API reference
=============

.. currentmodule:: vaelchi

Preprocessing
-------------

.. autofunction:: fill_missing_values

Clustering
----------

.. autofunction:: ahc

.. autofunction:: kmeans

Clustering results
------------------

.. autoclass:: ClusterResult
   :members:

.. autoclass:: AHCResult

Dynamic time warping
--------------------

.. autofunction:: dtw

.. autofunction:: dtw_matrix

.. autofunction:: dtw_path

.. autoclass:: DTWResult
   :members:

Compatibility helpers
---------------------

These helpers retain their historical behavior. In particular,
``find_euclidean_distance`` returns a **squared** distance.
``remove_outliers`` was moved from Energia and retains sequential in-place
replacement. Its documented boundary and window limitations also remain.

.. automodule:: vaelchi.functions.legacy
   :members:
