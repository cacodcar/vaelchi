"""General time-series clustering with explicit representative mappings."""

from .algorithms.ahc import ahc
from .algorithms.dtw import dtw, dtw_matrix, dtw_path
from .algorithms.kmeans import kmeans
from .nsrdb import fetch_nsrdb_data
from .preprocessing import fill_missing_values
from .result import AHCResult, ClusterResult, DTWResult
from .scaling import normalize, scaling

# OpenAI Codex: expose independent clustering and alignment APIs.
__all__ = [
    "AHCResult",
    "ClusterResult",
    "DTWResult",
    "ahc",
    "dtw",
    "dtw_matrix",
    "dtw_path",
    "fetch_nsrdb_data",
    "fill_missing_values",
    "kmeans",
    "normalize",
    "scaling",
]

#  public package version.
__version__ = "0.3.0"
