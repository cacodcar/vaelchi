API reference
=============

.. currentmodule:: vaelchi

Preprocessing
-------------

.. autofunction:: fill_missing_values

Clustering
----------

.. autofunction:: ahc

Result
------

.. autoclass:: AHCResult
   :members:

Compatibility helpers
---------------------

These helpers retain their historical behavior. In particular,
``find_euclidean_distance`` returns a **squared** distance.

.. automodule:: vaelchi.functions.legacy
   :members:
