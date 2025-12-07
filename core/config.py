import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict


@dataclass
class Config:
    data_root: str
    hourly_rate_mapping: Dict[float, str]
    hourly_rate_default: str


def load_config(path: Path) -> Config:
    raw = json.loads(path.read_text(encoding="utf-8"))

    mapping_raw = raw["HOURLY_RATE_MAPPING"]
    mapping_converted = {
        float(k): v
        for k, v in mapping_raw.items()
    }

    return Config(
        data_root=raw["DATA_ROOT"],
        hourly_rate_mapping=mapping_converted,
        hourly_rate_default=raw["HOURLY_RATE_DEFAULT"]
    )
