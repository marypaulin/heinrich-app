import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict


@dataclass
class Config:
    data_root: Path
    hourly_rate_mapping: Dict[float, str]
    hourly_rate_default: str


def load_config(path: Path) -> Config:
    raw = json.loads(path.read_text(encoding="utf-8"))

    data_root_raw = Path(raw["DATA_ROOT"])

    if data_root_raw.is_absolute():
        data_root = data_root_raw
    else:
        data_root = path.parent / data_root_raw

    mapping_raw = raw["HOURLY_RATE_MAPPING"]
    mapping_converted = {
        float(k): v
        for k, v in mapping_raw.items()
    }

    default_description = raw["HOURLY_RATE_DEFAULT"]

    return Config(
        data_root=data_root,
        hourly_rate_mapping=mapping_converted,
        hourly_rate_default=default_description
    )
