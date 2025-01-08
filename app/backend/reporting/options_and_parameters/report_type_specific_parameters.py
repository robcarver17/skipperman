from dataclasses import dataclass
from typing import List


@dataclass
class SpecificParametersForTypeOfReport:
    group_by_column: str
    passed_group_order: list
    report_type: str
