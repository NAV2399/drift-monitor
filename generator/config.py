"""Generator configuration — all knobs in one place."""
from dataclasses import dataclass, field


@dataclass
class DriftSpec:
    kind: str            # "sudden" | "gradual" | "feature"
    at_event: int        # event index where drift starts
    length: int = 0      # events over which gradual drift unfolds (0 = sudden)
    feature: str = ""    # feature drifted (for kind="feature")
    magnitude: float = 1.0


@dataclass
class GeneratorConfig:
    paysim_path: str = "data/paysim.csv"
    events_per_second: int = 1000
    seed: int = 42
    drifts: list = field(default_factory=list)  # list[DriftSpec]
    manifest_path: str = "data/drift_manifest.json"
