"""T-Cell Target Explorer — disease -> trusted candidate targets from CD4+ T-cell Perturb-seq."""
from .core import list_diseases, disease_targets, summary

__all__ = ["list_diseases", "disease_targets", "summary"]
__version__ = "0.1.0"
