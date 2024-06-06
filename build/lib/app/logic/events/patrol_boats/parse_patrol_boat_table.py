from typing import List, Union

from app.backend.forms.swaps import is_ready_to_swap

from app.backend.volunteers.patrol_boats import add_named_boat_to_event_with_no_allocation, \
    remove_patrol_boat_and_all_associated_volunteer_connections_from_event, \
    remove_volunteer_from_patrol_boat_on_day_at_event, \
    copy_across_allocation_of_boats_at_event, \
    get_volunteer_ids_allocated_to_any_patrol_boat_at_event_on_day, \
    BoatDayVolunteer, NO_ADDITION_TO_MAKE, ListOfBoatDayVolunteer, \
    add_list_of_new_boat_day_volunteer_allocations_to_data_reporting_conflicts
from app.backend.volunteers.volunteer_rota import update_role_at_event_for_volunteer_on_day_at_event, \
    get_volunteer_role_at_event_on_day, copy_across_duties_for_volunteer_at_event_from_one_day_to_all_other_days
from app.backend.volunteers.volunteers import add_boat_related_skill_for_volunteer, \
    remove_boat_related_skill_for_volunteer, boat_related_skill_for_volunteer, get_volunteer_name_from_id
from app.logic.events.events_in_state import get_event_from_state
from app.logic.events.patrol_boats.elements_in_patrol_boat_table import  \
     get_unique_list_of_volunteer_ids_for_skills_checkboxes, \
    is_volunteer_skill_checkbox_ticked
from app.logic.events.patrol_boats.patrol_boat_dropdowns import TOP_ROW_OF_VOLUNTEER_DROPDOWN, \
    from_allocation_dropdown_input_name_to_boat_and_day, from_selected_dropdown_to_volunteer, \
    get_list_of_dropdown_names_for_adding_volunteers, ADD_BOAT_DROPDOWN, \
    which_volunteer_role_selected_in_boat_allocation
from app.logic.events.patrol_boats.patrol_boat_buttons import from_delete_button_name_to_boat_name, \
    list_of_delete_buttons_in_patrol_boat_table, from_volunter_remove_button_name_to_volunteer_id_and_day, \
    get_all_remove_volunteer_button_names, get_button_type_day_volunteer_id_given_button_str
from app.logic.events.patrol_boats.copying import COPY_BOAT, COPY_ROLE, COPY_BOTH, get_list_of_all_types_of_copy_buttons
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.day_selectors import Day
from app.objects.events import Event


def get_all_copy_boat_buttons_for_boat_allocation(interface: abstractInterface) -> list:
    event = get_event_from_state(interface)
    return get_list_of_all_types_of_copy_buttons(interface=interface, event=event)


def update_if_copy_button_pressed(interface: abstractInterface, copy_button: str):
    event = get_event_from_state(interface)
    copy_type, day, volunteer_id = get_button_type_day_volunteer_id_given_button_str(copy_button)

    if copy_type==COPY_BOAT:
        copy_boat=True
        copy_role=False

    elif copy_type==COPY_ROLE:
        copy_boat=False
        copy_role=True

    elif copy_type==COPY_BOTH:
        copy_boat=True
        copy_role=True

    else:
        raise Exception("button type %s not recognised" % copy_type)

    if copy_boat:
        copy_across_allocation_of_boats_at_event(interface=interface, day=day, volunteer_id=volunteer_id, event=event)

    if copy_role:
        copy_across_duties_for_volunteer_at_event_from_one_day_to_all_other_days(
            interface=interface,
            event=event,
                    volunteer_id=volunteer_id, day=day)


def get_all_delete_buttons_for_patrol_boat_table(interface: abstractInterface) -> List[str]:
    event = get_event_from_state(interface)
    return list_of_delete_buttons_in_patrol_boat_table(interface=interface, event=event)

def get_all_delete_volunteer_buttons_for_patrol_boat_table(interface:abstractInterface) -> List[str]:
    event = get_event_from_state(interface)
    return get_all_remove_volunteer_button_names(interface=interface, event=event)

def update_if_delete_boat_button_pressed(interface: abstractInterface, delete_button: str):
    patrol_boat_name = from_delete_button_name_to_boat_name(delete_button)
    event = get_event_from_state(interface)
    print("Deleting %s" % patrol_boat_name)
    try:
        remove_patrol_boat_and_all_associated_volunteer_connections_from_event(interface=interface, event=event, patrol_boat_name=patrol_boat_name)
    except Exception as e:
        interface.log_error("Error deleting patrol boat %s: %s" % (patrol_boat_name, str(e)))


def update_data_from_form_entries_in_patrol_boat_allocation_page(interface: abstractInterface):

    ## Any added volunteers
    update_skills_checkbox(interface)
    if is_ready_to_swap(interface):
        return
    else:
        update_role_dropdowns(interface)
        update_adding_volunteers_to_specific_boats_and_days(interface) ## must come last or will confuse role and skills

def update_adding_volunteers_to_specific_boats_and_days(interface: abstractInterface):
    event = get_event_from_state(interface)
    list_of_volunteer_additions_to_boats = get_list_of_volunteer_additions_to_boats(interface)
    list_of_volunteer_additions_to_boats = list_of_volunteer_additions_to_boats.remove_no_additions()

    add_list_of_new_boat_day_volunteer_allocations_to_data_reporting_conflicts(interface=interface, list_of_volunteer_additions_to_boats=list_of_volunteer_additions_to_boats, event=event)


def get_list_of_volunteer_additions_to_boats(interface: abstractInterface) -> ListOfBoatDayVolunteer:
    event = get_event_from_state(interface)
    list_of_names = get_list_of_dropdown_names_for_adding_volunteers(interface=interface, event=event)
    list_of_updates = [get_boat_day_volunteer_for_dropdown_name_or_none(interface=interface, dropdown_name=dropdown_name) for dropdown_name in list_of_names]
    list_of_volunteer_additions_to_boats = ListOfBoatDayVolunteer(list_of_updates)

    return list_of_volunteer_additions_to_boats



def get_boat_day_volunteer_for_dropdown_name_or_none(interface: abstractInterface, dropdown_name: str) -> Union[
    BoatDayVolunteer, str]:

    selected_dropdown = interface.value_from_form(dropdown_name)

    if selected_dropdown == TOP_ROW_OF_VOLUNTEER_DROPDOWN:
        return NO_ADDITION_TO_MAKE
    boat, day = from_allocation_dropdown_input_name_to_boat_and_day(interface=interface, dropdown_input_name=dropdown_name)

    volunteer = from_selected_dropdown_to_volunteer(interface=interface, selected_dropdown=selected_dropdown)
    boat_day_volunteer = BoatDayVolunteer(boat=boat, day=day, volunteer=volunteer)

    return boat_day_volunteer

def update_skills_checkbox(interface: abstractInterface):
    event = get_event_from_state(interface)
    unique_volunteer_ids = get_unique_list_of_volunteer_ids_for_skills_checkboxes(interface=interface, event=event)
    for volunteer_id in unique_volunteer_ids:
        update_skills_checkbox_for_specific_volunteer_id(
                                                         volunteer_id=volunteer_id,
                                                         interface=interface)


def update_skills_checkbox_for_specific_volunteer_id(interface: abstractInterface,  volunteer_id: str):

    currently_has_boat_skill = boat_related_skill_for_volunteer(volunteer_id=volunteer_id, interface=interface)
    is_ticked = is_volunteer_skill_checkbox_ticked(interface=interface, volunteer_id=volunteer_id)

    if currently_has_boat_skill == is_ticked:
        return

    if is_ticked:
        add_boat_related_skill_for_volunteer(interface=interface, volunteer_id=volunteer_id)
    else:
        remove_boat_related_skill_for_volunteer(interface=interface, volunteer_id=volunteer_id)


def update_role_dropdowns(interface: abstractInterface):
    event = get_event_from_state(interface)
    for day in event.weekdays_in_event():
        list_of_volunteer_ids = get_volunteer_ids_allocated_to_any_patrol_boat_at_event_on_day(interface=interface, day=day, event=event)
        for volunteer_id in list_of_volunteer_ids:
            try:
                update_role_dropdown_for_volunteer_on_day(
                    interface=interface,
                    event=event,
                    day=day,
                    volunteer_id=volunteer_id
                )
            except Exception as e:
                name = get_volunteer_name_from_id(interface=interface, volunteer_id=volunteer_id)
                interface.log_error(
                    "Couldn't update volunteer role for %s on day %s - perhaps a conflicting change was made? Error code %s" % (
                    name, day.name, str(e)))


def update_role_dropdown_for_volunteer_on_day(interface: abstractInterface, volunteer_id: str, event: Event, day: Day):
    role_selected =which_volunteer_role_selected_in_boat_allocation(interface=interface, volunteer_id=volunteer_id, day=day)
    current_role = get_volunteer_role_at_event_on_day(interface=interface, event=event, volunteer_id=volunteer_id, day=day)

    if role_selected==current_role:
        return

    update_role_at_event_for_volunteer_on_day_at_event(interface=interface, volunteer_id=volunteer_id, day=day,
                                                       new_role=role_selected, event=event)


def update_adding_boat(interface: abstractInterface):
    event =get_event_from_state(interface)
    name_of_boat_added = interface.value_from_form(ADD_BOAT_DROPDOWN)

    try:
        add_named_boat_to_event_with_no_allocation(interface=interface,
                                                   name_of_boat_added=name_of_boat_added,
                                                   event=event)
    except Exception as e:
        interface.log_error("Can't add boat %s, error %s" % (name_of_boat_added, str(e)))

def update_if_delete_volunteer_button_pressed(interface: abstractInterface, delete_button: str):
    event =get_event_from_state(interface)
    volunteer_id, day = from_volunter_remove_button_name_to_volunteer_id_and_day(delete_button)

    try:
        remove_volunteer_from_patrol_boat_on_day_at_event(interface=interface,  event=event, day=day,  volunteer_id=volunteer_id)
    except Exception as e:
        name =get_volunteer_name_from_id(interface=interface,volunteer_id=volunteer_id)
        interface.log_error("Couldn't remove volunteer %s from rescue boat on day %s - perhaps a conflicting change was made? Error: %s" % (name, day.name, str(e)))

