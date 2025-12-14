from dataclasses import dataclass
from datetime import date
from typing import Literal


@dataclass
class CsvRow:
    row_number: int         # For debugging
    date: date              # "Datum" - aus "%d.%m.%Y" geparst
    order_number: str       # "Auftrags-Nr."
    description: str        # "Beschreibung"
    duration_hours: float   # "Dauer (Std)"
    hourly_rate: float      # "Stundensatz (€)"
    material_cost: float    # "Material (€)"
    total_cost: float       # "Gesamtkosten (€)" - just for debugging


@dataclass
class LineItem:
    # CSV rows split into two kinds
    kind: Literal["arbeitsstunden", "material"]
    order_number: str       # "Auftrag Nr."
    quantity: float         # "Menge"
    description: str        # "Beschreibung"
    unit_price: float       # "€/Stk"
    total_price: float      # "Preis gesamt" = €/Stk * Menge
