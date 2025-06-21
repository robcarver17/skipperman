from dataclasses import dataclass
from typing import List


@dataclass
class SpecificParametersForTypeOfReport:
    group_by_column: str
    group_order: List[str]
    report_type: str
    unallocated_group: str


def apply_override_additional_options(additional_parameters, **kwargs):
    for key, value in kwargs.items():
        setattr(additional_parameters, key, value)

    return additional_parameters
