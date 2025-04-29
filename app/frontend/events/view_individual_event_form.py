from typing import Union

from app.backend.clothing.summarise_clothing import summarise_clothing
from app.backend.events.summarys import summarise_allocations_for_event
from app.backend.events.view_event import identify_birthdays, summarise_registrations_for_event, \
    summarise_volunteers_for_event
from app.backend.food.summarise_food import summarise_food_data_by_day
from app.backend.patrol_boats.patrol_boat_summary import get_summary_list_of_patrol_boat_allocations_for_events
from app.backend.rota.volunteer_rota_summary import get_summary_list_of_teams_and_groups_for_events
from app.objects.abstract_objects.abstract_buttons import ButtonBar, main_menu_button, back_menu_button, Button, \
    HelpButton
from app.objects.abstract_objects.abstract_form import Form, NewForm
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_lines import ListOfLines, Line, _______________
from app.objects.abstract_objects.abstract_tables import PandasDFTable
from app.objects.abstract_objects.abstract_text import Heading
from app.objects.events import Event


def get_event_form_for_event(
    event: Event, interface: abstractInterface
) -> Union[Form, NewForm]:
    event_heading = get_event_heading(interface=interface, event=event)
    summary_lines = summary_tables_for_event(interface=interface, event=event)
    buttons = ListOfLines([get_event_buttons()])

    lines_in_form = buttons + event_heading + summary_lines

    return Form(lines_in_form.add_Lines())


def get_event_heading(interface: abstractInterface, event: Event) -> ListOfLines:
    birthdays = identify_birthdays(object_store=interface.object_store, event=event)

    event_description = event.details_as_list_of_str()
    event_description = event_description + birthdays
    event_description = ListOfLines(
        [Line([Heading(item, centred=True, size=5)]) for item in event_description]
    )

    return event_description

def summary_tables_for_event(interface: abstractInterface, event: Event) -> ListOfLines:
    summarise_registrations = PandasDFTable(summarise_registrations_for_event(
        object_store=interface.object_store, event=event
    ))
    if len(summarise_registrations)==0:
        summarise_registrations=""

    summarise_volunteers = PandasDFTable(summarise_volunteers_for_event(
        object_store=interface.object_store, event=event
    ))
    if len(summarise_volunteers)==0:
        summarise_volunteers=""


    allocations = PandasDFTable(summarise_allocations_for_event(
        object_store=interface.object_store, event=event
    ))
    if len(allocations) > 0:
        allocations_lines = ListOfLines(
            [
                _______________,
                "Boat details and group allocations",
                _______________,
                allocations,
            ]
        )
    else:
        allocations_lines = ""

    rota = get_summary_list_of_teams_and_groups_for_events(
        object_store=interface.object_store, event=event
    )
    if len(rota) > 0:
        rota_lines = ListOfLines(
            [
                _______________,
                "Volunteer rota:",
                _______________,
                rota,
                _______________,
            ]
        )
    else:
        rota_lines = ""

    boat_allocation_table = get_summary_list_of_patrol_boat_allocations_for_events(
        object_store=interface.object_store, event=event
    )
    if len(boat_allocation_table) > 0:
        boat_lines = ListOfLines(
            [
                _______________,
                "Patrol boats, number of crew:",
                boat_allocation_table,
                _______________,
            ]
        )
    else:
        boat_lines = ""

    food_summary = summarise_food_data_by_day(object_store=interface.object_store, event=event)
    if len(food_summary)>0:
        food_summary_lines = ListOfLines(
            [
                _______________,
                "Food requirements (if catered event)",
                _______________,
                food_summary,
                _______________,
            ]
        )
    else:
        food_summary_lines = ""


    clothing_summary = summarise_clothing(object_store=interface.object_store, event=event)
    if len(clothing_summary)>0:        
        clothing_summary_lines = ListOfLines(
            [
                _______________,
                "Clothing sizes and colours:",
                _______________,
                clothing_summary,
                _______________,
            ]
        )
    else:
        clothing_summary_lines = ""


    summary_lines = ListOfLines(
        [
            summarise_registrations,
            _______________,
            allocations_lines,
            _______________,
            summarise_volunteers,
            _______________,
            rota_lines,
            _______________,
            boat_lines,
            _______________,
             food_summary_lines,
            _______________,
            clothing_summary_lines,
        ]
    )

    return summary_lines


def get_event_buttons() -> ButtonBar:
    return ButtonBar(
        [
            main_menu_button,
            back_menu_button,
            " ",
            import_registration_data_button,
            edit_registration_button,
            group_allocation_button,
            volunteer_rota_button,
            patrol_boat_allocation_button,
            food_button,
            clothing_button,
            help_button,
        ]
    )


IMPORT_REGISTRATION_DATA_BUTTON_LABEL = "Import registration data"
ALLOCATE_CADETS_BUTTON_LABEL = "Sailors, groups and boats"
EDIT_CADET_REGISTRATION_DATA_IN_EVENT_BUTTON = "Edit sailors registration data"
EDIT_VOLUNTEER_ROLES_BUTTON_LABEL = "Volunteers"
PATROL_BOAT_ALLOCATION_BUTTON_LABEL = "Patrol boats"
CLOTHING_BUTTON_LABEL = "Clothing"
FOOD_BUTTON_LABEL = "Food"
group_allocation_button = Button(ALLOCATE_CADETS_BUTTON_LABEL, nav_button=True)
edit_registration_button = Button(
    EDIT_CADET_REGISTRATION_DATA_IN_EVENT_BUTTON, nav_button=True
)
volunteer_rota_button = Button(EDIT_VOLUNTEER_ROLES_BUTTON_LABEL, nav_button=True)
patrol_boat_allocation_button = Button(
    PATROL_BOAT_ALLOCATION_BUTTON_LABEL, nav_button=True
)
food_button = Button(FOOD_BUTTON_LABEL, nav_button=True)
clothing_button = Button(CLOTHING_BUTTON_LABEL, nav_button=True)
import_registration_data_button = Button(
    IMPORT_REGISTRATION_DATA_BUTTON_LABEL, nav_button=True
)  ## uploads and creates staging file
help_button = HelpButton("view_event_help")
