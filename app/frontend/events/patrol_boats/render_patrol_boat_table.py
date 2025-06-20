from typing import List, Union

from app.frontend.events.patrol_boats.swapping import (
    get_swap_button_to_move_to_boat_without_swapping,
)
from app.frontend.forms.swaps import is_ready_to_swap

from app.backend.patrol_boats.patrol_boat_summary import (
    get_summary_list_of_patrol_boat_allocations_for_events,
)
from app.frontend.events.patrol_boats.elements_in_patrol_boat_table import (
    get_existing_allocation_elements_for_day_and_boat,
    get_volunteer_row_to_select_skill,
    get_list_of_volunteers_for_skills_checkboxes,
    update_and_get_warnings_on_all_volunteers_in_patrol_boats,
    instructions_qual_table,
    instructions_text, get_boat_label_entry,
)
from app.frontend.events.patrol_boats.patrol_boat_dropdowns import (
    get_add_boat_dropdown,
    get_add_volunteer_to_patrol_boat_dropdown,
)
from app.frontend.events.patrol_boats.patrol_boat_buttons import (
    delete_button_for_boat_value,
    DELETE_BOAT_BUTTON_LABEL,
)
from app.frontend.shared.club_dinghies import get_club_dinghies_detail
from app.frontend.shared.club_boats_instructors import get_club_dinghies_detail_instructors
from app.objects.abstract_objects.abstract_buttons import (
    Button,
)
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_lines import (
    ListOfLines,
    DetailListOfLines,
    _______________,
)
from app.objects.day_selectors import Day
from app.objects.events import Event
from app.objects.abstract_objects.abstract_tables import Table, RowInTable
from app.objects.abstract_objects.abstract_text import bold
from app.objects.patrol_boats import PatrolBoat

SAVE_CHANGES_BUTTON_LABEL = "Save changes"


def get_top_material_for_patrol_boat_form(
    interface: abstractInterface, event: Event
) -> ListOfLines:
    if is_ready_to_swap(interface):
        return ListOfLines([""])
    summary_of_boat_allocations = get_patrol_boat_summary(
        interface=interface, event=event
    )
    patrol_boat_driver_and_crew_qualifications = (
        get_patrol_boat_driver_and_crew_qualifications(interface=interface, event=event)
    )
    club_dinghies_instructors = get_club_dinghies_detail_instructors(interface=interface, event=event)

    warnings = update_and_get_warnings_on_all_volunteers_in_patrol_boats(
        interface=interface, event=event
    )
    return ListOfLines(
        [
            _______________,
            summary_of_boat_allocations,
            _______________,
            patrol_boat_driver_and_crew_qualifications,
            _______________,
            club_dinghies_instructors,
            _______________,
        ]
        + warnings
        + [
            _______________,
            _______________,
            instructions_text,
        ]
    )


def get_patrol_boat_summary(
    interface: abstractInterface, event: Event
) -> Union[str, DetailListOfLines]:
    summary_of_boat_allocations_as_df = (
        get_summary_list_of_patrol_boat_allocations_for_events(
            object_store=interface.object_store, event=event
        )
    )
    if len(summary_of_boat_allocations_as_df) == 0:
        summary_of_boat_allocations = ""
    else:
        summary_of_boat_allocations = DetailListOfLines(
            ListOfLines([summary_of_boat_allocations_as_df]), name="Summary"
        )

    return summary_of_boat_allocations


def get_patrol_boat_driver_and_crew_qualifications(
    interface: abstractInterface, event: Event
) -> Union[DetailListOfLines, str]:

    patrol_boat_driver_and_crew_qualifications_table = (
        get_patrol_boat_driver_and_crew_qualifications_table(
            interface=interface, event=event
        )
    )

    if len(patrol_boat_driver_and_crew_qualifications_table) == 0:
        return ""
    else:
        patrol_boat_driver_and_crew_qualifications = DetailListOfLines(
            ListOfLines(
                [
                    instructions_qual_table,
                    patrol_boat_driver_and_crew_qualifications_table,
                ]
            ),
            name="Qualifications",
        )

    return patrol_boat_driver_and_crew_qualifications


def get_patrol_boat_driver_and_crew_qualifications_table(
    interface: abstractInterface, event: Event
) -> Table:
    list_of_volunteers = get_list_of_volunteers_for_skills_checkboxes(
        object_store=interface.object_store,
        event=event,
    )
    list_of_volunteers = list_of_volunteers.sort_by_firstname()

    return Table(
        [
            get_volunteer_row_to_select_skill(interface=interface, volunteer=volunteer)
            for volunteer in list_of_volunteers
        ]
    )


def get_patrol_boat_table(interface: abstractInterface, event: Event) -> Table:
    top_row = get_top_row_for_patrol_boat_table(event)
    other_rows = get_body_of_patrol_boat_table_at_event(
        event=event, interface=interface
    )
    bottom_row = get_bottom_row_for_patrol_boat_table(
        interface=interface, event=event, top_row=top_row
    )

    return Table([top_row] + other_rows + [bottom_row], has_column_headings=True)


def get_top_row_for_patrol_boat_table(event: Event) -> RowInTable:
    list_of_days_at_event_as_str = event.days_in_event_as_list_of_string()
    list_of_days_at_event_as_bold_text = [
        bold(text) for text in list_of_days_at_event_as_str
    ]

    return RowInTable(
        [
            bold("Boat")
        ]
        + list_of_days_at_event_as_bold_text
    )


def get_bottom_row_for_patrol_boat_table(
    interface: abstractInterface, event: Event, top_row: RowInTable
) -> RowInTable:
    in_swap_state = is_ready_to_swap(interface)
    if in_swap_state:
        return RowInTable([""] * len(top_row))

    add_boat_dropdown = get_add_boat_dropdown(interface=interface, event=event)
    padding_columns = get_bottom_row_padding_columns_for_patrol_boat_table(event)

    return RowInTable(
        [
            add_boat_dropdown,
        ]
        + padding_columns
    )


def get_bottom_row_padding_columns_for_patrol_boat_table(event: Event) -> List[str]:
    list_of_days_at_event_as_str = event.days_in_event_as_list_of_string()
    number_of_padding_columns = len(list_of_days_at_event_as_str)
    padding_columns = [""] * number_of_padding_columns

    return padding_columns


from app.backend.patrol_boats.volunteers_at_event_on_patrol_boats import (
    load_list_of_patrol_boats_at_event,
    is_boat_empty, )


def get_body_of_patrol_boat_table_at_event(
    interface: abstractInterface, event: Event
) -> List[RowInTable]:
    list_of_boats_at_event = load_list_of_patrol_boats_at_event(
        object_store=interface.object_store, event=event
    )

    other_rows = [
        get_row_for_boat_at_event(
            patrol_boat=patrol_boat, event=event, interface=interface
        )
        for patrol_boat in list_of_boats_at_event
    ]

    return other_rows


def get_row_for_boat_at_event(
    interface: abstractInterface, event: Event, patrol_boat: PatrolBoat
) -> RowInTable:
    boat_name_and_button_for_first_column = get_boat_name_and_button_for_first_column(
        interface=interface, patrol_boat=patrol_boat
    )
    day_inputs = get_allocation_inputs_for_boat_across_days(
        interface=interface, event=event, patrol_boat=patrol_boat
    )

    return RowInTable([boat_name_and_button_for_first_column] + day_inputs)


def get_boat_name_and_button_for_first_column(
    interface: abstractInterface, patrol_boat: PatrolBoat
) -> ListOfLines:
    boat_name = patrol_boat.name
    in_swap_state = is_ready_to_swap(interface)

    if in_swap_state:
        delete_button = ""
    else:
        delete_button = Button(
            label=DELETE_BOAT_BUTTON_LABEL,
            value=delete_button_for_boat_value(patrol_boat),
        )

    return ListOfLines([boat_name, delete_button]).add_Lines()


def get_allocation_inputs_for_boat_across_days(
    interface: abstractInterface, event: Event, patrol_boat: PatrolBoat
) -> list:
    day_inputs = [
        get_allocation_inputs_for_day_and_boat(
            patrol_boat=patrol_boat, day=day, event=event, interface=interface
        )
        for day in event.days_in_event()
    ]
    return day_inputs


def get_allocation_inputs_for_day_and_boat(
    interface: abstractInterface, patrol_boat: PatrolBoat, day: Day, event: Event
) -> ListOfLines:
    if is_boat_empty(
        object_store=interface.object_store,
        patrol_boat=patrol_boat,
        day=day,
        event=event,
    ):
        return get_allocation_inputs_for_day_and_boat_if_boat_is_empty(
            interface=interface, patrol_boat=patrol_boat, day=day, event=event
        )
    else:
        return get_allocation_inputs_for_day_and_boat_if_boat_contains_volunteers(
            interface=interface, patrol_boat=patrol_boat, day=day, event=event
        )


def get_allocation_inputs_for_day_and_boat_if_boat_is_empty(
    interface: abstractInterface, patrol_boat: PatrolBoat, day: Day, event: Event
) -> ListOfLines:
    if is_ready_to_swap(interface):
        return ListOfLines(
            [
                get_swap_button_to_move_to_boat_without_swapping(
                    interface=interface, patrol_boat=patrol_boat, day=day
                )
            ]
        )
    dropdown = get_add_volunteer_to_patrol_boat_dropdown(
            interface=interface, patrol_boat=patrol_boat, day=day, event=event
        )
    label = get_boat_label_entry(interface=interface, patrol_boat=patrol_boat, day=day, event=event)

    return ListOfLines([
        label,
        dropdown
    ])


def get_allocation_inputs_for_day_and_boat_if_boat_contains_volunteers(
    interface: abstractInterface, patrol_boat: PatrolBoat, day: Day, event: Event
) -> ListOfLines:
    label = get_boat_label_entry(interface=interface, patrol_boat=patrol_boat, day=day, event=event)

    existing_elements = get_existing_allocation_elements_for_day_and_boat(
        day=day, patrol_boat=patrol_boat, event=event, interface=interface
    )

    in_swap_state = is_ready_to_swap(interface)
    if in_swap_state:
        last_bit = get_swap_button_to_move_to_boat_without_swapping(
            patrol_boat=patrol_boat, day=day, interface=interface
        )
    else:
        last_bit = get_add_volunteer_to_patrol_boat_dropdown(
            interface=interface, patrol_boat=patrol_boat, day=day, event=event
        )

    return ListOfLines([label]+ existing_elements + [last_bit])
