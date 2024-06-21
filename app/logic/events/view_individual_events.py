from typing import Union

from app.backend.wa_import.map_wa_fields import     is_wa_field_mapping_setup_for_event
from app.backend.group_allocations.event_summarys import summarise_registrations_for_event, \
    identify_birthdays, summarise_allocations_for_event
from app.backend.volunteers.patrol_boats import get_summary_list_of_boat_allocations_for_events
from app.backend.volunteers.volunteer_rota_summary import    get_summary_list_of_teams_and_groups_for_events
from app.backend.wa_import.map_wa_files import   is_wa_file_mapping_setup_for_event
from app.logic.events.group_allocation.ENTRY_allocate_cadets_to_groups import display_form_allocate_cadets
from app.logic.events.import_wa.import_wa_file import display_form_import_event_file
from app.logic.events.import_wa.update_existing_event import display_form_update_existing_event
from app.logic.events.import_wa.upload_event_file import display_form_upload_event_file
from app.logic.events.mapping.ENTRY_event_field_mapping import display_form_event_field_mapping
from app.logic.events.registration_details.ENTRY_edit_registration_details import display_form_edit_registration_details
from app.logic.events.volunteer_rota.ENTRY1_display_main_rota_page import display_form_view_for_volunteer_rota
from app.logic.events.patrol_boats.ENTRY_allocate_patrol_boats import display_form_view_for_patrol_boat_allocation
from app.logic.events.food.ENTRY_food import display_form_view_for_food_requirements
from app.logic.events.clothing.ENTRY_clothing import display_form_view_for_clothing_requirements

from app.objects.abstract_objects.abstract_form import (
    Form,
    NewForm
)
from app.objects.abstract_objects.abstract_lines import Line, ListOfLines, _______________
from app.objects.abstract_objects.abstract_buttons import BACK_BUTTON_LABEL, Button, ButtonBar, main_menu_button
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.logic.abstract_logic_api import button_error_and_back_to_initial_state_form

from app.logic.events.constants import *
from app.backend.wa_import.load_wa_file import does_raw_event_file_exist
from app.logic.events.events_in_state import get_event_from_state
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

    birthdays = identify_birthdays(interface=interface, event=event)

    event_description = event.details_as_list_of_str()
    event_description = event_description + birthdays
    event_description = ListOfLines([Line([Heading(item,centred=True, size=5)]) for item in event_description])

    summarise_registrations = summarise_registrations_for_event(interface=interface, event=event)

    allocations_lines = ""
    if event.contains_cadets:
        if event.contains_groups:
            description = "Boat details and group allocations"
        else:
            description = "Boat details and allocations"
        allocations = summarise_allocations_for_event(interface=interface, event=event)
        if len(allocations)>0:
            allocations_lines = ListOfLines([ _______________,
                        description,
                        _______________,
                        allocations])


    rota_lines = ""
    if event.contains_volunteers:
        rota = get_summary_list_of_teams_and_groups_for_events(interface=interface, event=event)
        boat_allocation_table = get_summary_list_of_boat_allocations_for_events(interface=interface, event=event)
        if len(boat_allocation_table)>0:
            rota_lines =   ListOfLines([
                         _______________,
                        "Volunteer rota:",
                          _______________,
                          rota,
                        _______________,
                        _______________,
                        "Patrol boats, number of crew:",
                        boat_allocation_table])



    if event.contains_food:
        ## FIXME SUMMARISE FOOD NUMBERS
        pass

    if event.contains_clothing:
        ## FIXME SUMMARISE CLOTHING NUMBERS
        pass

    buttons = get_event_buttons(event, interface=interface)

    lines_in_form = (ListOfLines(
                    [
                        buttons,
                        _______________,
                        ListOfLines(event_description),
                        _______________,
                        summarise_registrations,
                        allocations_lines,
                        rota_lines,
]))

    return Form(lines_in_form)



def get_event_buttons(event: Event, interface: abstractInterface) -> ButtonBar:
    wa_initial_upload = Button(
        WA_UPLOAD_BUTTON_LABEL,
        nav_button=True
    )  ## uploads and creates staging file
    wa_create_field_mapping = Button(
        WA_FIELD_MAPPING_BUTTON_LABEL,
        nav_button=True
    )  ## does field mapping from staged file
    wa_check_field_mapping = Button(WA_CHECK_FIELD_MAPPING_BUTTON_LABEL,
        nav_button=True)
    wa_modify_field_mapping = Button(WA_MODIFY_FIELD_MAPPING_BUTTON_LABEL,
        nav_button=True)

    wa_import = Button(WA_IMPORT_BUTTON_LABEL,
        nav_button=True)  ## does import_wa given a staged file
    wa_update = Button(
        WA_UPDATE_BUTTON_LABEL,
        nav_button=True
    )  ## does upload and import_wa, assuming no staged file

    back_button = Button(BACK_BUTTON_LABEL,
        nav_button=True)


    wa_import_done = is_wa_file_mapping_setup_for_event(interface=interface, event=event) ## have we done an import already (sets up event mapping)
    field_mapping_done = is_wa_field_mapping_setup_for_event(interface=interface, event=event) ## have set up field mapping
    raw_event_file_exists = does_raw_event_file_exist(event.id) ## is there a staging file waiting to be uploaded


    print(
        "[wa_import_done=%s, field_mapping_done=%s, raw_event_file_exists=%s]"
        % (str(wa_import_done), str(field_mapping_done), str(raw_event_file_exists))
    )

    if not wa_import_done and not field_mapping_done and not raw_event_file_exists:
        return ButtonBar([main_menu_button, back_button, wa_initial_upload])

    if not wa_import_done and field_mapping_done and not raw_event_file_exists:
        ## probably done mapping manually, need to do initial upload
        return ButtonBar([main_menu_button, back_button, wa_initial_upload])

    if not wa_import_done and not field_mapping_done and raw_event_file_exists:
        return ButtonBar([main_menu_button, back_button, wa_create_field_mapping])

    if not wa_import_done and field_mapping_done and raw_event_file_exists:
        return ButtonBar([main_menu_button, back_button, wa_import, wa_check_field_mapping])

    ## both done, we can update the WA file and do cadet backend / other editing
    if wa_import_done and field_mapping_done and not raw_event_file_exists:
        event_specific_buttons = get_event_specific_buttons(event)
        return ButtonBar([main_menu_button, back_button, wa_update, wa_modify_field_mapping]+event_specific_buttons )

    if wa_import_done and field_mapping_done and raw_event_file_exists:
        ## shouldn't really happen
        event_specific_buttons = get_event_specific_buttons(event)
        return ButtonBar([main_menu_button, back_button, wa_update, wa_modify_field_mapping]+event_specific_buttons )

    interface.log_error(
        "Something went wrong; contact support [wa_import_done=%s, field_mapping_done=%s, raw_event_file_exists=%s]"
        % (str(wa_import_done), str(field_mapping_done), str(raw_event_file_exists))
    )
    return ButtonBar([main_menu_button, back_button])

def get_event_specific_buttons(event: Event) -> list:
    group_allocation = Button(ALLOCATE_CADETS_BUTTON_LABEL, nav_button=True)
    modify_cadet_boats = Button(MODIFY_CADET_BOATS_BUTTON_LABEL, nav_button=True)
    edit_registration = Button(EDIT_CADET_REGISTRATION_DATA_IN_EVENT_BUTTON, nav_button=True)
    volunteer_rota = Button(EDIT_VOLUNTEER_ROLES_BUTTON_LABEL, nav_button=True)
    patrol_boat_allocation = Button(PATROL_BOAT_ALLOCATION_BUTTON_LABEL, nav_button=True)
    food = Button(FOOD_BUTTON_LABEL, nav_button=True)
    clothing = Button(CLOTHING_BUTTON_LABEL, nav_button=True)
    event_specific_buttons = []
    if event.contains_cadets:
        event_specific_buttons.append(edit_registration)
        if event.contains_groups:
            event_specific_buttons.append(group_allocation)
        else:
            event_specific_buttons.append(modify_cadet_boats) ## Still do sails etc even if not groups
    if event.contains_volunteers:
        event_specific_buttons+=[volunteer_rota, patrol_boat_allocation]
    if event.contains_food:
        event_specific_buttons.append(food)
    if event.contains_clothing:
        event_specific_buttons.append(clothing)

    return event_specific_buttons



def post_form_view_individual_event(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    ## Called by post on view events form, so both stage and event name are set

    last_button_pressed = interface.last_button_pressed()
    if last_button_pressed == WA_UPLOAD_BUTTON_LABEL:
        return form_to_upload_event_file(interface)

    elif last_button_pressed in [WA_FIELD_MAPPING_BUTTON_LABEL, WA_MODIFY_FIELD_MAPPING_BUTTON_LABEL, WA_CHECK_FIELD_MAPPING_BUTTON_LABEL]:
        ## same form, but contents will be different
        return form_to_do_field_mapping(interface)

    elif last_button_pressed == WA_IMPORT_BUTTON_LABEL:
        return form_to_do_import_event(interface)

    elif last_button_pressed == WA_UPDATE_BUTTON_LABEL:
        return form_to_do_update_event(interface)

    elif last_button_pressed in [ALLOCATE_CADETS_BUTTON_LABEL, MODIFY_CADET_BOATS_BUTTON_LABEL]:
        return form_to_do_cadet_allocation(interface)

    elif last_button_pressed==EDIT_CADET_REGISTRATION_DATA_IN_EVENT_BUTTON:
        return form_to_edit_registration_details(interface)

    elif last_button_pressed==EDIT_VOLUNTEER_ROLES_BUTTON_LABEL:
        return form_to_do_volunteer_rota(interface)

    elif last_button_pressed==PATROL_BOAT_ALLOCATION_BUTTON_LABEL:
        return form_to_allocate_patrol_boats(interface)

    elif last_button_pressed==FOOD_BUTTON_LABEL:
        return form_to_allocate_food(interface)

    elif last_button_pressed==CLOTHING_BUTTON_LABEL:
        return form_to_do_clothing(interface)

    elif last_button_pressed == BACK_BUTTON_LABEL:
        return previous_form(interface)
    else:
        button_error_and_back_to_initial_state_form(interface)


def row_of_form_for_event_with_buttons(event) -> Line:
    return Line(Button(str(event)))


def form_to_upload_event_file(interface: abstractInterface):
    return interface.get_new_form_given_function(display_form_upload_event_file)


def form_to_do_field_mapping(interface: abstractInterface):
    return interface.get_new_form_given_function(display_form_event_field_mapping)


def form_to_do_import_event(interface: abstractInterface):
    return interface.get_new_form_given_function(display_form_import_event_file)


def form_to_do_update_event(interface: abstractInterface):
    return interface.get_new_form_given_function(display_form_update_existing_event)


def form_to_do_cadet_allocation(interface: abstractInterface):
    return interface.get_new_form_given_function(display_form_allocate_cadets)


def form_to_edit_registration_details(interface: abstractInterface):
    return interface.get_new_form_given_function(display_form_edit_registration_details)


def form_to_do_volunteer_rota(interface: abstractInterface):
    return interface.get_new_form_given_function(display_form_view_for_volunteer_rota) ## check rota before going to form


def form_to_allocate_patrol_boats(interface: abstractInterface):
    return interface.get_new_form_given_function(display_form_view_for_patrol_boat_allocation)

def form_to_allocate_food(interface: abstractInterface):
    return interface.get_new_form_given_function(display_form_view_for_food_requirements)

def form_to_do_clothing(interface: abstractInterface):
    return interface.get_new_form_given_function(display_form_view_for_clothing_requirements)



def previous_form(interface: abstractInterface):
    return interface.get_new_display_form_for_parent_of_function(post_form_view_individual_event)

