from dataclasses import dataclass
from typing import List


@dataclass
class SpecificParametersForTypeOfReport:
    group_by_column: str
    report_type: str
