from app.backend.events.list_of_events import (
    get_sorted_list_of_events,
    all_sort_types_for_event_list,
)
from app.frontend.shared.buttons import (
    get_button_value_for_event_selection,
    get_button_value_for_sort_order,
)
from app.objects.abstract_objects.abstract_buttons import Button, ButtonBar
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_lines import Line
from app.objects.events import SORT_BY_START_DSC, ListOfEvents


def display_list_of_events_with_buttons(
    interface: abstractInterface, sort_by=SORT_BY_START_DSC
) -> Line:
    list_of_events = get_sorted_list_of_events(
        object_store=interface.object_store, sort_by=sort_by
    )
    return display_given_list_of_events_with_buttons(list_of_events)


def display_given_list_of_events_with_buttons(list_of_events: ListOfEvents) -> Line:
    list_with_buttons = [
        Button(
            label=str(event),
            value=get_button_value_for_event_selection(event),
            tile=True,
        )
        for event in list_of_events
    ]

    return Line(list_with_buttons)


sort_buttons_for_event_list = ButtonBar(
    [
        Button(
            label=sortby, value=get_button_value_for_sort_order(sortby), nav_button=True
        )
        for sortby in all_sort_types_for_event_list
    ]
)
