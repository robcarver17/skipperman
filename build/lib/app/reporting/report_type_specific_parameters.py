from dataclasses import dataclass
from typing import List


@dataclass
class SpecificParametersForTypeOfReport:
    entry_columns: List[str]
    group_by_column: str
    passed_group_order: list
