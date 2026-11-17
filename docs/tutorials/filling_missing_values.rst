Filling missing calendar values
===============================

``vaelchi.fill_missing_values`` completes a timestamp-indexed pandas Series or
DataFrame. It inserts missing calendar rows and fills missing cells using the
chosen policy. The result preserves column names and physical units for
further analysis.

Weekends and holidays
---------------------

Use a daily calendar to insert weekends and holidays. The default carries the
last available observation forward:

.. code-block:: python

   
   import pandas as pd
   from vaelchi import fill_missing_values

   prices = pd.Series(
       [10.0, 12.0],
       index=pd.to_datetime(["2024-05-24", "2024-05-28"]),
       name="price",
   )
   daily = fill_missing_values(prices, freq="D")
   # May 24 through May 28: [10.0, 10.0, 10.0, 10.0, 12.0]

This fills every missing daily value. No holiday database is needed, and the
function does not distinguish a scheduled closure from a measurement outage.
Choose a policy appropriate to the physical meaning of your observations.

Policies and boundaries
-----------------------

* ``method="ffill"`` carries the previous value forward, leaving leading gaps.
* ``method="bfill"`` uses the next value, leaving trailing gaps.
* ``method="time"`` interpolates numeric values by elapsed time, only between
  observations. It leaves leading and trailing gaps.
* ``limit=2`` fills at most two consecutive missing rows per column. For time
  interpolation the limit is applied in the forward direction.

Backward fill and interpolation use future observations. Columns are processed
independently; a column without observations remains missing.

``start`` and ``end`` set inclusive bounds; otherwise the earliest and latest
input timestamps are used. Only observations inside the requested window supply
values. Timezones and leap days are preserved, and ``freq="h"`` creates an hourly
calendar. Observations must fall on the requested grid: this function does not
aggregate or resample off-grid observations. Duplicate timestamps are rejected.
