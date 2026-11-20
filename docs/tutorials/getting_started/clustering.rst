Clustering and consuming results
================================

Pass aligned one-dimensional numeric series as positional arguments to
:func:`vaelchi.ahc`. Their order defines the feature axis of the result.
``period_length`` is the number of samples in each period; ``periods`` is the
number of representative periods to retain per parent group. If provided,
``parent_length`` counts original periods within each independently clustered
parent group. Inputs must contain complete periods and complete parent groups.

Vaelchi constrains clustering to adjacent periods, without wraparound. The
default ``selection="nearest_centroid"`` chooses an observed member of each
cluster, with chronological tie breaking. Pass ``selection="legacy"`` to
reproduce the Vaelchi 0.1.0 default.

Output contract
---------------

:class:`vaelchi.AHCResult` exposes representative profiles in original input units,
a representative-row label for every original period, selected original-period
indices, weights, and two standardized squared-error measures. Weights count
periods; they are not probabilities or time durations.

``result.reconstruct()`` returns an array of shape ``(timesteps, features)``.
``result.to_dict()`` exports detached JSON-compatible lists and scalars. See
:doc:`../../CLUSTERING` for shapes, numerical details, and historical validation.

Using exported results
----------------------

A consumer reads ``representatives`` as ``(rows, samples_per_period, features)``
and uses ``labels`` to map every original period to a representative row.
It retains feature names, timestamps, and units separately, and maps these
numeric values into its own model.

.. code-block:: python

   
   import json
   import numpy as np

   payload = json.loads(json.dumps(result.to_dict()))
   profiles = np.asarray(payload["representatives"])
   reconstructed = profiles[payload["labels"]].reshape(-1, profiles.shape[-1])

Try :doc:`../../examples/representative_days` for a complete two-feature example.
