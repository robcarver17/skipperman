from dataclasses import dataclass
from typing import List, Dict

from app.objects.day_selectors import Day
from app.objects.utilities.exceptions import arg_not_passed


class GroupAnnotations(Dict[str, Dict[str,str]]):
    pass

@dataclass
class SpecificParametersForTypeOfReport:
    group_by_column: str
    group_order: List[str]
    report_type: str
    unallocated_group: str
    group_annotations: GroupAnnotations = arg_not_passed


def apply_override_additional_options(additional_parameters, **kwargs):
    for key, value in kwargs.items():
        setattr(additional_parameters, key, value)

    return additional_parameters
