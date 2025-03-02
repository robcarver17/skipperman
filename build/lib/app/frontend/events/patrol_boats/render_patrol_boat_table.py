from typing import List, Union


from app.frontend.forms.swaps import is_ready_to_swap

from app.backend.patrol_boats.patrol_boat_summary import (
    get_summary_list_of_patrol_boat_allocations_for_events,
)
from app.frontend.events.patrol_boats.elements_in_patrol_boat_table import (
    get_existing_allocation_elements_for_day_and_boat,
    get_volunteer_row_to_select_skill,
    get_list_of_volunteers_for_skills_checkboxes,
    warn_on_all_volunteers_in_patrol_boats,
    instructions_qual_table,
    instructions_text,
)
from app.frontend.events.patrol_boats.patrol_boat_dropdowns import (
    get_add_boat_dropdown,
    get_add_volunteer_to_patrol_boat_dropdown,
)
from app.frontend.events.patrol_boats.patrol_boat_buttons import (
    delete_button_for_boat_value,
    DELETE_BOAT_BUTTON_LABEL,
)
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
    summary_of_boat_allocations = get_patrol_boat_summary(
        interface=interface, event=event
    )
    patrol_boat_driver_and_crew_qualifications = (
        get_patrol_boat_driver_and_crew_qualifications(interface=interface, event=event)
    )
    warnings = warn_on_all_volunteers_in_patrol_boats(interface=interface, event=event)
    return ListOfLines(
        [
            _______________,
            _______________,
            summary_of_boat_allocations,
            _______________,
            _______________,
            patrol_boat_driver_and_crew_qualifications,
            _______________,
            _______________,
            warnings,
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
    in_swap_state = is_ready_to_swap(interface)
    if in_swap_state:
        return ""

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
    in_swap_state = is_ready_to_swap(interface)
    if in_swap_state:
        bottom_row = RowInTable([""] * len(top_row))
    else:
        bottom_row = get_bottom_row_for_patrol_boat_table(
            interface=interface, event=event
        )

    return Table([top_row] + other_rows + [bottom_row], has_column_headings=True)


def get_top_row_for_patrol_boat_table(event: Event) -> RowInTable:
    list_of_days_at_event_as_str = event.days_in_event_as_list_of_string()
    list_of_days_at_event_as_bold_text = [
        bold(text) for text in list_of_days_at_event_as_str
    ]

    return RowInTable([
                          bold("Boat"),
                      ]
                      + list_of_days_at_event_as_bold_text)


def get_bottom_row_for_patrol_boat_table(
    interface: abstractInterface, event: Event
) -> RowInTable:
    add_boat_dropdown = get_add_boat_dropdown(interface=interface, event=event)
    padding_columns = get_bottom_row_padding_columns_for_patrol_boat_table(event)

    return RowInTable([
                          add_boat_dropdown,
                      ]
                      + padding_columns)


def get_bottom_row_padding_columns_for_patrol_boat_table(event: Event) -> List[str]:
    list_of_days_at_event_as_str = event.days_in_event_as_list_of_string()
    number_of_padding_columns = len(list_of_days_at_event_as_str)
    padding_columns = [""] * number_of_padding_columns

    return padding_columns


from app.backend.patrol_boats.volunteers_at_event_on_patrol_boats import (
    load_list_of_patrol_boats_at_event,
)


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
    day_inputs = [
        get_allocation_inputs_for_day_and_boat(
            patrol_boat=patrol_boat, day=day, event=event, interface=interface
        )
        for day in event.days_in_event()
    ]

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


def get_allocation_inputs_for_day_and_boat(
    interface: abstractInterface, patrol_boat: PatrolBoat, day: Day, event: Event
) -> ListOfLines:
    existing_elements = get_existing_allocation_elements_for_day_and_boat(
        day=day, patrol_boat=patrol_boat, event=event, interface=interface
    )
    add_volunteer_to_patrol_boat_dropdown = get_add_volunteer_to_patrol_boat_dropdown(
        interface=interface, patrol_boat=patrol_boat, day=day, event=event
    )
    return ListOfLines(existing_elements + [add_volunteer_to_patrol_boat_dropdown])
