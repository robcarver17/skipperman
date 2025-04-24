from typing import Dict

from app.backend.reporting.options_and_parameters.print_options import PrintOptions
from app.objects.day_selectors import Day
from app.objects.events import Event
from app.objects.utilities.utils import we_are_not_the_same


def pseudo_reporting_options_for_event_data_dump(event: Event) -> PrintOptions:
    print_options = PrintOptions(
        publish_to_public=False,
        output_pdf=False,
    )
    print_options.filename = "event_data_%s" % event.event_name

    return print_options


ROW_ID = "row_id"


def day_item_dict_as_string_or_single_if_identical(
    day_item_dict: Dict[Day, str]
) -> str:
    if len(day_item_dict) == 0:
        return ""
    all_values = list(day_item_dict.values())
    if we_are_not_the_same(all_values):
        items_as_list_of_str = [
            "%s:%s" % (day.name, item) for day, item in day_item_dict.items()
        ]
        return ", ".join(items_as_list_of_str)
    else:
        return all_values[0]  ## all the same
