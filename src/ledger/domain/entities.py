from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class LedgerEntry:
    voucher_id: str
    date: Optional[datetime]
    account: str
    direction: str
    amount: float
    direction_code: int
    month: int
    day_of_week: int
    source_sheet: str
    description: Optional[str] = None
