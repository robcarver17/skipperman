from typing import List

from app.backend.data.dinghies import load_list_of_patrol_boats_at_event
from app.backend.forms.swaps import is_ready_to_swap
from app.backend.volunteers.patrol_boats import get_summary_list_of_boat_allocations_for_events
from app.data_access.configuration.configuration import WEBLINK_FOR_QUALIFICATIONS
from app.data_access.configuration.fixed import COPY_SYMBOL1, COPY_SYMBOL2, SWAP_SHORTHAND1, SWAP_SHORTHAND2, \
    BOAT_SHORTHAND, ROLE_SHORTHAND, BOAT_AND_ROLE_SHORTHAND, REMOVE_SHORTHAND
from app.logic.events.patrol_boats.elements_in_patrol_boat_table import \
    get_existing_allocation_elements_for_day_and_boat, get_unique_list_of_volunteer_ids_for_skills_checkboxes, \
    get_volunteer_row_to_select_skill
from app.logic.events.patrol_boats.patrol_boat_dropdowns import get_add_boat_dropdown, \
    get_allocation_dropdown_to_add_volunteer_for_day_and_boat
from app.logic.events.patrol_boats.patrol_boat_buttons import delete_button_for_boat, DELETE_BOAT_BUTTON_LABEL
from app.objects.abstract_objects.abstract_buttons import Button, ButtonBar, CANCEL_BUTTON_LABEL
from app.objects.abstract_objects.abstract_form import Link
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_lines import Line, ListOfLines, DetailListOfLines, _______________
from app.objects.day_selectors import Day
from app.objects.events import Event
from app.objects.abstract_objects.abstract_tables import Table, RowInTable
from app.objects.abstract_objects.abstract_text import bold
from app.objects.patrol_boats import PatrolBoat


SAVE_CHANGES_BUTTON_LABEL = "Save changes"

def get_top_material_for_patrol_boat_form(interface: abstractInterface, event: Event) -> ListOfLines:
    summary_of_boat_allocations =  get_summary_list_of_boat_allocations_for_events(interface=interface, event=event)
    if len(summary_of_boat_allocations)==0:
        summary_of_boat_allocations=""
    else:
        summary_of_boat_allocations = DetailListOfLines(
            ListOfLines([summary_of_boat_allocations]), name='Summary'
        )
    patrol_boat_driver_and_crew_qualifications_table = (
        get_patrol_boat_driver_and_crew_qualifications_table(interface=interface, event=event))
    if len(patrol_boat_driver_and_crew_qualifications_table)==0:
        patrol_boat_driver_and_crew_qualifications_table = ''
    else:
        patrol_boat_driver_and_crew_qualifications_table = DetailListOfLines(ListOfLines([
            instructions_qual_table,
            patrol_boat_driver_and_crew_qualifications_table
        ]), name = "Qualifications")

    return  ListOfLines(
            [
                _______________,
                _______________,
                summary_of_boat_allocations,
                _______________,
                _______________,
                patrol_boat_driver_and_crew_qualifications_table,
                _______________,
                _______________,
                instructions_text,
             ]
        )


def get_patrol_boat_driver_and_crew_qualifications_table(interface: abstractInterface, event: Event) -> Table:
    volunteer_ids = get_unique_list_of_volunteer_ids_for_skills_checkboxes(event=event, interface=interface)

    return Table([
        get_volunteer_row_to_select_skill(
            interface=interface,
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
        bottom_row = get_bottom_row_for_patrol_boat_table(interface=interface, event=event)

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

def get_bottom_row_for_patrol_boat_table(interface: abstractInterface, event: Event) -> RowInTable:

    add_boat_dropdown = get_add_boat_dropdown(interface=interface, event=event)
    padding_columns = get_bottom_row_padding_columns_for_patrol_boat_table(event)

    return RowInTable([
        add_boat_dropdown,
    ]+padding_columns
                      )

def get_bottom_row_padding_columns_for_patrol_boat_table(event: Event)-> List[str]:
    list_of_days_at_event_as_str = event.weekdays_in_event_as_list_of_string()
    number_of_padding_columns=len(list_of_days_at_event_as_str)
    padding_columns = [""]*number_of_padding_columns

    return padding_columns

def get_body_of_patrol_boat_table_at_event( interface:abstractInterface, event: Event) -> List[RowInTable]:

    list_of_boats_at_event= load_list_of_patrol_boats_at_event(interface=interface, event=event)

    other_rows = [get_row_for_boat_at_event(
                                                 patrol_boat=patrol_boat,
                                                 event=event,
                                            interface=interface)

                  for patrol_boat in list_of_boats_at_event]

    return other_rows


def get_row_for_boat_at_event( interface:abstractInterface,
                               event: Event,
                              patrol_boat: PatrolBoat) -> RowInTable:
    boat_name_and_button_for_first_column = get_boat_name_and_button_for_first_column(
        interface=interface, patrol_boat=patrol_boat
    )
    day_inputs = [get_allocation_inputs_for_day_and_boat(
        patrol_boat=patrol_boat,
        day=day,
        event=event,
        interface=interface
    ) for day in event.weekdays_in_event()]

    return RowInTable([
        boat_name_and_button_for_first_column
    ]+day_inputs)

def get_boat_name_and_button_for_first_column( interface:abstractInterface,
                              patrol_boat: PatrolBoat) -> ListOfLines:

    boat_name = patrol_boat.name
    in_swap_state = is_ready_to_swap(interface)

    if in_swap_state:
        delete_button = ""
    else:
        delete_button = Button(label=DELETE_BOAT_BUTTON_LABEL, value=delete_button_for_boat(patrol_boat))


    return ListOfLines([boat_name, delete_button]).add_Lines()


def get_allocation_inputs_for_day_and_boat( interface:abstractInterface,
                                            patrol_boat: PatrolBoat,
                                                 day: Day,
                                                event: Event
                                                 ) -> ListOfLines:

    existing_elements = get_existing_allocation_elements_for_day_and_boat(
        day=day,
        patrol_boat=patrol_boat,
        event=event,
        interface=interface
    )
    in_swap_state = is_ready_to_swap(interface)
    if in_swap_state:
        add_volunteer_dropdown = ""
    else:
        add_volunteer_dropdown = get_allocation_dropdown_to_add_volunteer_for_day_and_boat(
            interface=interface,
            boat_at_event=patrol_boat,
            day=day,
            event=event
        )
    return ListOfLines(existing_elements+[add_volunteer_dropdown])



def get_button_bar_for_patrol_boats(interface: abstractInterface) -> ButtonBar:
    in_swap_state = is_ready_to_swap(interface)
    if in_swap_state:
        return ButtonBar([])
    save_button = Button(SAVE_CHANGES_BUTTON_LABEL, nav_button=True)
    back_button = get_back_button_for_boat_allocation(interface)
    return ButtonBar([back_button, save_button, copy_all_boats_button, copy_all_boats_and_roles_buttons])

COPY_ALL_BOATS_BUTTON_LABEL = "Copy all boats (where possible) across days"
COPY_BOATS_AND_ROLES_BUTTON_LABEL = "Copy all boats and roles (where possible) across days"
copy_all_boats_button = Button(COPY_ALL_BOATS_BUTTON_LABEL, nav_button=True)
copy_all_boats_and_roles_buttons = Button(COPY_BOATS_AND_ROLES_BUTTON_LABEL, nav_button=True)

def get_back_button_for_boat_allocation(interface: abstractInterface):
    in_swap_state = is_ready_to_swap(interface)
    if in_swap_state:
        return ""
    else:
        return Button(CANCEL_BUTTON_LABEL, nav_button=True)


link = Link(url=
            WEBLINK_FOR_QUALIFICATIONS, string="Qualifications table", open_new_window=True)
instructions_qual_table = ListOfLines([Line(["Tick to specify that a volunteer has PB2 (check don't assume: ", link, " )"])])
instructions_text = ListOfLines([Line(["Save changes after non button actions. Key for buttons - Copy: ",
                                       COPY_SYMBOL1, COPY_SYMBOL2,
                                        "; Swap: ", SWAP_SHORTHAND1, SWAP_SHORTHAND2, ", ",
                                       BOAT_SHORTHAND,' = boat, ',
                                       ROLE_SHORTHAND,' = role, ',
                                       BOAT_AND_ROLE_SHORTHAND,' = boat & role. '
                                        '; Remove: ', REMOVE_SHORTHAND])])
