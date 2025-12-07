from pathlib import Path

from core.config import Config, load_config


def test_get_config():
    project_root = Path(__file__).resolve().parents[1]
    config = load_config(project_root / "config.json")

    assert isinstance(config, Config)
    assert isinstance(list(config.hourly_rate_mapping.keys())[0], float)
