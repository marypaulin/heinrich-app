from typing import List

from .config import Config
from .models import LineItem, Totals


def calculate_sums_and_vat(items: List[LineItem], config: Config) -> Totals:
    """Calculate sum_net, vat, and sum_gross from LineItems."""
    sum_net = sum(i.total_price for i in items)
    vat = sum_net * config.vat_rate
    sum_gross = sum_net + vat
    return Totals(sum_net=sum_net, vat=vat, sum_gross=sum_gross)
