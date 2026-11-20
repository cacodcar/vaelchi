"""General time-series clustering with explicit representative mappings."""

from .algorithms.ahc import ahc
from .preprocessing import fill_missing_values
from .result import AHCResult

__all__ = ["AHCResult", "ahc", "fill_missing_values"]

#  public package version.
__version__ = "0.1.1"
