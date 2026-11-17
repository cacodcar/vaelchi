Runnable example
================

From an installed Vaelchi environment, run this command at the repository root:

.. code-block:: console

   python examples/representative_days.py

The six synthetic days contain four samples per day and two features: demand
and temperature. Two groups of identical profiles reduce exactly to two
representatives, with weights ``[3, 3]`` and labels ``[0, 0, 0, 1, 1, 1]``.
The script prints the entire JSON-compatible result.

.. literalinclude:: ../../examples/representative_days.py
   :language: python
   :linenos:

The :doc:`representative_days` notebook also reconstructs the chronology from
plain exported data, illustrating the interface other applications can use.
