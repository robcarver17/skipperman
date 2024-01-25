from app.objects.abstract_objects.abstract_form import dropDownInput
from app.logic.events.constants import (
    ROW_STATUS,
)
from app.objects.constants import arg_not_passed
from app.objects.mapped_wa_event_with_ids import all_possible_status, RowStatus

all_status_names = [row_status.name for row_status in all_possible_status]


def dropdown_input_for_status_change(input_label: str = "Status", input_name: str = ROW_STATUS, current_status: RowStatus = arg_not_passed,
                                     dict_of_options: dict = arg_not_passed) -> dropDownInput:
    if current_status is arg_not_passed:
        default_label = arg_not_passed
    else:
        default_label = current_status.name

    if dict_of_options is arg_not_passed:
        dict_of_options = dict(
            [(status_name, status_name) for status_name in all_status_names])

    return dropDownInput(
        input_label=input_label,
        input_name=input_name,
        default_label=default_label,
        dict_of_options=dict_of_options
        )
