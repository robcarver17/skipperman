from dataclasses import dataclass
from typing import List

from app.backend.data.resources import load_list_of_patrol_boats_at_event
from app.backend.forms.swaps import is_ready_to_swap
from app.logic.events.patrol_boats.elements_in_patrol_boat_table import \
    get_existing_allocation_elements_for_day_and_boat, get_unique_list_of_volunteer_ids_for_skills_checkboxes, \
    get_volunteer_row_to_select_skill
from app.logic.events.patrol_boats.patrol_boat_dropdowns import get_add_boat_dropdown, \
    get_allocation_dropdown_to_add_volunteer_for_day_and_boat
from app.logic.events.patrol_boats.patrol_boat_buttons import delete_button_for_boat, DELETE_BOAT_BUTTON_LABEL
from app.objects.abstract_objects.abstract_buttons import Button
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_lines import Line, ListOfLines
from app.objects.day_selectors import Day
from app.objects.events import Event
from app.objects.abstract_objects.abstract_tables import Table, RowInTable
from app.objects.abstract_objects.abstract_text import bold
from app.objects.patrol_boats import PatrolBoat


def get_patrol_boat_driver_and_crew_qualifications_table(event: Event) -> Table:
    volunteer_ids = get_unique_list_of_volunteer_ids_for_skills_checkboxes(event)

    return Table([
        get_volunteer_row_to_select_skill(
            volunteer_id=volunteer_id
        ) for volunteer_id in volunteer_ids
    ])

def get_patrol_boat_table( interface:abstractInterface, event: Event) -> Table:

    top_row = get_top_row_for_patrol_boat_table(event)
    other_rows = get_body_of_patrol_boat_table_at_event(event=event, interface=interface)
    in_swap_state = is_ready_to_swap(interface)
    if in_swap_state:
        bottom_row = RowInTable([""]*len(top_row))
    else:
        bottom_row = get_bottom_row_for_patrol_boat_table(event)

    return Table(
        [top_row]+other_rows+[bottom_row],
        has_column_headings=True
    )


def get_top_row_for_patrol_boat_table(event: Event) -> RowInTable:
    list_of_days_at_event_as_str = event.weekdays_in_event_as_list_of_string()
    list_of_days_at_event_as_bold_text = [bold(text) for text in list_of_days_at_event_as_str]

    return RowInTable([
        bold("Boat"),
    ]+list_of_days_at_event_as_bold_text
                      )

def get_bottom_row_for_patrol_boat_table(event: Event) -> RowInTable:

    add_boat_dropdown = get_add_boat_dropdown(event)

    list_of_days_at_event_as_str = event.weekdays_in_event_as_list_of_string()
    number_of_padding_columns=len(list_of_days_at_event_as_str)
    padding_columns = [""]*number_of_padding_columns

    return RowInTable([
        add_boat_dropdown,
    ]+padding_columns
                      )


def get_body_of_patrol_boat_table_at_event( interface:abstractInterface, event: Event) -> List[RowInTable]:

    #data_to_be_stored = get_patrol_boat_data_to_be_stored(event)
    data_to_be_stored = ""

    #list_of_boats_at_event = get_list_of_boats_at_event(data_to_be_stored)
    list_of_boats_at_event= load_list_of_patrol_boats_at_event(event)

    other_rows = [get_row_for_boat_at_event(
                                                 boat_at_event = boat_at_event,
                                                 event=event,
                                            interface=interface)

                  for boat_at_event in list_of_boats_at_event]

    return other_rows


def get_row_for_boat_at_event( interface:abstractInterface,
                               event: Event,
                              boat_at_event: PatrolBoat) -> RowInTable:

    boat_name = boat_at_event.name
    in_swap_state = is_ready_to_swap(interface)

    if in_swap_state:
        delete_button = ""
    else:
        delete_button = Button(label=DELETE_BOAT_BUTTON_LABEL, value=delete_button_for_boat(boat_at_event))

    day_inputs = [get_allocation_inputs_for_day_and_boat(
        boat_at_event=boat_at_event,
        day=day,
        event=event,
        interface=interface
    ) for day in event.weekdays_in_event()]

    return RowInTable([
        ListOfLines([boat_name, delete_button]).add_Lines()
    ]+day_inputs)


def get_allocation_inputs_for_day_and_boat( interface:abstractInterface,
                                            boat_at_event: PatrolBoat,
                                                 day: Day,
                                                event: Event
                                                 ) -> ListOfLines:

    existing_elements = get_existing_allocation_elements_for_day_and_boat(
        day=day,
        boat_at_event=boat_at_event,
        event=event,
        interface=interface
    )
    in_swap_state = is_ready_to_swap(interface)
    if in_swap_state:
        add_volunteer_dropdown = ""
    else:
        add_volunteer_dropdown = get_allocation_dropdown_to_add_volunteer_for_day_and_boat(
            boat_at_event=boat_at_event,
            day=day,
            event=event
        )
    return ListOfLines(existing_elements+[add_volunteer_dropdown])



