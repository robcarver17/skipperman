from typing import Union

from app.backend.patrol_boats.patrol_boat_summary import (
    get_summary_list_of_patrol_boat_allocations_for_events,
)
from app.backend.rota.volunteer_rota_summary import (
    get_summary_list_of_teams_and_groups_for_events,
)
from app.backend.events.summarys import summarise_allocations_for_event
from app.backend.events.view_event import (
    identify_birthdays,
    summarise_registrations_for_event,
)
from app.frontend.events.group_allocation.ENTRY_allocate_cadets_to_groups import (
    display_form_allocate_cadets,
)
from app.frontend.events.import_data.ENTRY_import_choose import (
    display_form_choose_import_source,
)

from app.frontend.events.registration_details.ENTRY_edit_registration_details import (
    display_form_edit_registration_details,
)
from app.frontend.events.volunteer_rota.ENTRY1_display_main_rota_page import (
    display_form_view_for_volunteer_rota,
)
from app.frontend.events.patrol_boats.ENTRY_allocate_patrol_boats import (
    display_form_view_for_patrol_boat_allocation,
)
from app.frontend.events.food.ENTRY_food import display_form_view_for_food_requirements
from app.frontend.events.clothing.ENTRY_clothing import (
    display_form_view_for_clothing_requirements,
)

from app.objects.abstract_objects.abstract_form import Form, NewForm
from app.objects.abstract_objects.abstract_lines import (
    Line,
    ListOfLines,
    _______________,
)
from app.objects.abstract_objects.abstract_buttons import (
    Button,
    ButtonBar,
    main_menu_button,
    back_menu_button,
    HelpButton,
)
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.frontend.form_handler import button_error_and_back_to_initial_state_form

from app.frontend.shared.events_state import get_event_from_state
from app.objects.abstract_objects.abstract_text import Heading
from app.objects.events import Event


def display_form_view_individual_event(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    event = get_event_from_state(interface)
    form = get_event_form_for_event(event, interface=interface)

    return form


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
    summarise_registrations = summarise_registrations_for_event(
        object_store=interface.object_store, event=event
    )

    allocations = summarise_allocations_for_event(
        object_store=interface.object_store, event=event
    )
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

    """
    food_summary = summarise_food_data_by_day(interface=interface, event=event)
    if len(food_summary)>0:
        food_summary_lines = ListOfLines(
            [
                _______________,
                "Food requirements",
                _______________,
                food_summary,
                _______________,
            ]
        )
    else:
        food_summary_lines = ""


    clothing_summary = summarise_clothing(interface=interface, event=event)
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

    """

    summary_lines = ListOfLines(
        [
            summarise_registrations,
            allocations_lines,
            rota_lines,
            boat_lines,
            # food_summary,
            # clothing_summary,
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


def post_form_view_individual_event(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    ## Called by post on view events form, so both stage and event name are set

    last_button_pressed = interface.last_button_pressed()
    if import_registration_data_button.pressed(last_button_pressed):
        return form_to_upload_event_file(interface)

    elif group_allocation_button.pressed(last_button_pressed):
        return form_to_do_cadet_allocation(interface)

    elif edit_registration_button.pressed(last_button_pressed):
        return form_to_edit_registration_details(interface)

    elif volunteer_rota_button.pressed(last_button_pressed):
        return form_to_do_volunteer_rota(interface)

    elif patrol_boat_allocation_button.pressed(last_button_pressed):
        return form_to_allocate_patrol_boats(interface)

    elif food_button.pressed(last_button_pressed):
        return form_to_allocate_food(interface)

    elif clothing_button.pressed(last_button_pressed):
        return form_to_do_clothing(interface)

    elif back_menu_button.pressed(last_button_pressed):
        return previous_form(interface)
    else:
        button_error_and_back_to_initial_state_form(interface)


def row_of_form_for_event_with_buttons(event) -> Line:
    return Line(Button(str(event)))


def form_to_upload_event_file(interface: abstractInterface):
    return interface.get_new_form_given_function(display_form_choose_import_source)


def form_to_do_cadet_allocation(interface: abstractInterface):
    return interface.get_new_form_given_function(display_form_allocate_cadets)


def form_to_edit_registration_details(interface: abstractInterface):
    return interface.get_new_form_given_function(display_form_edit_registration_details)


def form_to_do_volunteer_rota(interface: abstractInterface):
    return interface.get_new_form_given_function(
        display_form_view_for_volunteer_rota
    )  ## check rota before going to form


def form_to_allocate_patrol_boats(interface: abstractInterface):
    return interface.get_new_form_given_function(
        display_form_view_for_patrol_boat_allocation
    )


def form_to_allocate_food(interface: abstractInterface):
    return interface.get_new_form_given_function(
        display_form_view_for_food_requirements
    )


def form_to_do_clothing(interface: abstractInterface):
    return interface.get_new_form_given_function(
        display_form_view_for_clothing_requirements
    )


def previous_form(interface: abstractInterface):
    return interface.get_new_display_form_for_parent_of_function(
        post_form_view_individual_event
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
