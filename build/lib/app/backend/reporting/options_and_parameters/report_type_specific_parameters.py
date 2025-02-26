from dataclasses import dataclass
from typing import List


@dataclass
class SpecificParametersForTypeOfReport:
    group_by_column: str
    group_order: List[str]
    report_type: str
    unallocated_group: str