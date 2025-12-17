from typing import List, Tuple

from core.config import Config
from models import LineItem


def calculate_sums_and_vat(items: List[LineItem], config: Config) -> Tuple[float, float, float]:
    """Calculate sum_net, vat, and sum_gross from LineItems."""
    sum_net = sum(item.total_price for item in items)
    vat = sum_net * config.vat_rate
    sum_gross = sum_net + vat
    return sum_net, vat, sum_gross
