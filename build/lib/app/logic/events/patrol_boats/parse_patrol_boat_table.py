from typing import List

from app.backend.data.volunteer_rota import copy_across_duties_for_volunteer_at_event_from_one_day_to_all_other_days
from app.backend.volunteers.patrol_boats import add_named_boat_to_event_with_no_allocation, \
    remove_patrol_boat_and_all_associated_volunteer_connections_from_event, \
    remove_volunteer_from_patrol_boat_on_day_at_event, \
    get_volunteer_ids_allocated_to_any_patrol_boat_at_event_on_day, copy_across_allocation_of_boats_at_event, \
    allocate_volunteer_to_boat_at_event_on_day
from app.backend.volunteers.volunteer_rota import get_volunteer_role_at_event_on_day, \
    update_role_at_event_for_volunteer_on_day_at_event
from app.backend.volunteers.volunteers import boat_related_skill_for_volunteer, add_boat_related_skill_for_volunteer, \
    remove_boat_related_skill_for_volunteer
from app.logic.events.events_in_state import get_event_from_state
from app.logic.events.patrol_boats.elements_in_patrol_boat_table import  \
     get_unique_list_of_volunteer_ids_for_skills_checkboxes, \
    is_volunteer_skill_checkbox_ticked
from app.logic.events.patrol_boats.patrol_boat_dropdowns import DROPDOWN_IF_NOBODY_ADDED, \
    from_allocation_dropdown_input_name_to_boat_and_day, from_dropdown_name_to_volunteer, \
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
    return get_list_of_all_types_of_copy_buttons(event)


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
        copy_across_allocation_of_boats_at_event(day=day, volunteer_id=volunteer_id, event=event)

    if copy_role:
        copy_across_duties_for_volunteer_at_event_from_one_day_to_all_other_days(event=event,
                    volunteer_id=volunteer_id, day=day)


def get_all_delete_buttons_for_patrol_boat_table(interface: abstractInterface) -> List[str]:
    event = get_event_from_state(interface)
    return list_of_delete_buttons_in_patrol_boat_table(event)

def get_all_delete_volunteer_buttons_for_patrol_boat_table(interface:abstractInterface) -> List[str]:
    event = get_event_from_state(interface)
    return get_all_remove_volunteer_button_names(event)

def update_if_delete_boat_button_pressed(interface: abstractInterface, delete_button: str):
    patrol_boat_name = from_delete_button_name_to_boat_name(delete_button)
    event = get_event_from_state(interface)
    print("Deleting %s" % patrol_boat_name)
    try:
        remove_patrol_boat_and_all_associated_volunteer_connections_from_event(event=event, patrol_boat_name=patrol_boat_name)
    except Exception as e:
        interface.log_error("Error deleting patrol boat %s: %s" % (patrol_boat_name, str(e)))


def update_data_from_form_entries_in_allocation_page(interface: abstractInterface):
    ## Any added volunteers
    update_skills_checkbox(interface)
    update_role_dropdowns(interface)
    update_adding_volunteers_to_specific_boats_and_days(interface) ## must come last or will confuse role and skills

def update_adding_volunteers_to_specific_boats_and_days(interface: abstractInterface):
    event = get_event_from_state(interface)
    list_of_names = get_list_of_dropdown_names_for_adding_volunteers(event)
    for dropdown_name in list_of_names:
        try:
            update_adding_volunteers_to_specific_boats_and_days_for_a_given_dropdown_name(dropdown_name=dropdown_name,
                                                                                          event=event,
                                                                                          interface=interface)
        except Exception as e:
            print("Error %s when updating for dropdown %s" % (str(e), dropdown_name))

def update_adding_volunteers_to_specific_boats_and_days_for_a_given_dropdown_name(interface: abstractInterface, dropdown_name: str, event: Event):
    print("DROPDOWN NAME %s" % dropdown_name)
    boat, day = from_allocation_dropdown_input_name_to_boat_and_day(dropdown_name)

    selected_dropdown = interface.value_from_form(dropdown_name)
    if selected_dropdown == DROPDOWN_IF_NOBODY_ADDED:
        return

    volunteer = from_dropdown_name_to_volunteer(selected_dropdown)

    allocate_volunteer_to_boat_at_event_on_day(volunteer = volunteer,
                                                  event = event,
                                                  day=day,
                                                  patrol_boat = boat)

def update_skills_checkbox(interface: abstractInterface):
    event = get_event_from_state(interface)
    unique_volunteer_ids = get_unique_list_of_volunteer_ids_for_skills_checkboxes(event)
    for volunteer_id in unique_volunteer_ids:
        update_skills_checkbox_for_specific_volunteer_id(event=event,
                                                         volunteer_id=volunteer_id,
                                                         interface=interface)


def update_skills_checkbox_for_specific_volunteer_id(interface: abstractInterface, event: Event, volunteer_id: str):

    currently_has_boat_skill = boat_related_skill_for_volunteer(volunteer_id)

    is_ticked = is_volunteer_skill_checkbox_ticked(interface=interface, volunteer_id=volunteer_id)

    if currently_has_boat_skill == is_ticked:
        return

    if is_ticked:
        add_boat_related_skill_for_volunteer(volunteer_id)
    else:
        remove_boat_related_skill_for_volunteer(volunteer_id)


def update_role_dropdowns(interface: abstractInterface):
    event = get_event_from_state(interface)
    for day in event.weekdays_in_event():
        list_of_volunteer_ids = get_volunteer_ids_allocated_to_any_patrol_boat_at_event_on_day(day=day, event=event)
        for volunteer_id in list_of_volunteer_ids:
            try:
                update_role_dropdown_for_volunteer_on_day(
                    interface=interface,
                    event=event,
                    day=day,
                    volunteer_id=volunteer_id
                )
            except Exception as e:
                print("Error %s updating role dropdown for %s" % (str(e), volunteer_id))

def update_role_dropdown_for_volunteer_on_day(interface: abstractInterface, volunteer_id: str, event: Event, day: Day):
    role_selected =which_volunteer_role_selected_in_boat_allocation(interface=interface, volunteer_id=volunteer_id, day=day)
    current_role = get_volunteer_role_at_event_on_day(event=event, volunteer_id=volunteer_id, day=day)

    if role_selected==current_role:
        return

    update_role_at_event_for_volunteer_on_day_at_event(volunteer_id=volunteer_id, day=day,
                                                       new_role=role_selected, event=event)


def update_adding_boat(interface: abstractInterface):
    event =get_event_from_state(interface)
    name_of_boat_added = interface.value_from_form(ADD_BOAT_DROPDOWN)

    add_named_boat_to_event_with_no_allocation(name_of_boat_added=name_of_boat_added,
                                               event=event)

def update_if_delete_volunteer_button_pressed(interface: abstractInterface, delete_button: str):
    event =get_event_from_state(interface)
    volunteer_id, day = from_volunter_remove_button_name_to_volunteer_id_and_day(delete_button)

    remove_volunteer_from_patrol_boat_on_day_at_event(volunteer_id=volunteer_id, day=day,  event=event)


