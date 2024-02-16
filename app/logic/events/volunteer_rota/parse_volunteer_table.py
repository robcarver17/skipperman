from app.backend.data.volunteer_rota import copy_across_duties_for_volunteer_at_event_from_one_day_to_all_other_days
from app.backend.volunteers.volunteer_allocation import make_volunteer_available_on_day
from app.backend.volunteers.volunteer_rota_data import get_data_to_be_stored
from app.logic.events.volunteer_rota.edit_cadet_connections_for_event_from_rota import \
    display_form_edit_cadet_connections_from_rota
from app.logic.events.volunteer_rota.edit_volunteer_details_from_rota import \
    display_form_confirm_volunteer_details_from_rota
from app.logic.events.volunteer_rota.edit_volunteer_skills_from_rota import \
    display_form_edit_individual_volunteer_skills_from_rota
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.logic.events.events_in_state import get_event_from_state
from app.logic.events.volunteer_rota.parse_data_fields_in_rota import update_details_from_form_for_volunteer_at_event, \
    update_details_from_form_for_volunteer_given_specific_day_at_event
from app.logic.events.volunteer_rota.volunteer_table_buttons import *
from app.logic.volunteers.volunteer_state import update_state_with_volunteer_id
from app.objects.abstract_objects.abstract_form import NewForm


def get_list_of_volunteer_name_buttons(interface: abstractInterface)-> list:
    event = get_event_from_state(interface)
    volunteer_name_buttons_dict =get_dict_of_volunteer_name_buttons_and_volunteer_ids(event=event)
    list_of_volunteer_name_buttons = list(volunteer_name_buttons_dict.keys())

    return list_of_volunteer_name_buttons


def action_if_volunteer_button_pressed(interface: abstractInterface, volunteer_button: str) -> NewForm:
    event = get_event_from_state(interface)
    volunteer_name_buttons_dict =get_dict_of_volunteer_name_buttons_and_volunteer_ids(event=event)

    volunteer_id = volunteer_name_buttons_dict[volunteer_button]
    update_state_with_volunteer_id(interface=interface, volunteer_id=volunteer_id)

    return interface.get_new_display_form_given_function(display_form_confirm_volunteer_details_from_rota)

def get_all_day_sort_buttons(interface:abstractInterface):
    event = get_event_from_state(interface)

    return get_list_of_day_button_values(event)

def get_all_location_buttons(interface: abstractInterface):
    event =get_event_from_state(interface)
    all_location_buttons =list_of_all_location_button_names(event)

    return all_location_buttons


def get_all_skill_buttons(interface: abstractInterface):
    event =get_event_from_state(interface)
    all_skill_buttons = list_of_all_skills_buttons(event=event)

    return all_skill_buttons



def get_all_unavailable_buttons(interface: abstractInterface):
    event =get_event_from_state(interface)
    all_buttons = get_list_of_unavailable_button_values(event)

    return all_buttons

def get_all_copy_buttons(interface: abstractInterface):
    event = get_event_from_state(interface)
    return get_list_of_copy_buttons(event)

def action_if_location_button_pressed(interface: abstractInterface, location_button: str) -> NewForm:
    volunteer_id = from_location_button_to_volunteer_id(location_button)
    update_state_with_volunteer_id(interface=interface, volunteer_id=volunteer_id)

    return interface.get_new_display_form_given_function(display_form_edit_cadet_connections_from_rota)


def action_if_volunteer_skills_button_pressed(interface: abstractInterface, volunteer_skills_button: str) -> NewForm:
    volunteer_id = from_skills_button_to_volunteer_id(volunteer_skills_button)
    update_state_with_volunteer_id(interface=interface, volunteer_id=volunteer_id)

    return interface.get_new_display_form_given_function(display_form_edit_individual_volunteer_skills_from_rota)

def update_if_copy_button_pressed(interface: abstractInterface, copy_button: str):

    volunteer_id, day =    from_copy_button_to_volunteer_id_and_day(copy_button)
    event = get_event_from_state(interface)
    list_of_volunteers_at_event = load_list_of_volunteers_at_event(event)
    volunteer_at_event = list_of_volunteers_at_event.volunteer_at_event_with_id(volunteer_id)
    data_to_be_stored = get_data_to_be_stored(event)

    update_details_from_form_for_volunteer_given_specific_day_at_event(
        interface=interface,
        volunteer_at_event=volunteer_at_event,
        day=day,
        data_to_be_stored=data_to_be_stored
    )
    print("copying volunteer id %s day %s" % (volunteer_id, day.name))
    copy_across_duties_for_volunteer_at_event_from_one_day_to_all_other_days(event=event,
                    volunteer_id=volunteer_id, day=day)

def update_if_make_available_button_pressed(interface: abstractInterface, unavailable_button: str):
    volunteer_id, day =  from_unavailable_button_value_to_volunteer_and_day(unavailable_button)
    event = get_event_from_state(interface)
    make_volunteer_available_on_day(volunteer_id=volunteer_id, event=event, day=day)

def update_if_save_button_pressed_in_rota_page(interface: abstractInterface):
    event = get_event_from_state(interface)
    list_of_volunteers_at_event = load_list_of_volunteers_at_event(event)
    data_to_be_stored = get_data_to_be_stored(event)

    for volunteer_at_event in list_of_volunteers_at_event:
        update_details_from_form_for_volunteer_at_event(
            interface=interface,
            volunteer_at_event=volunteer_at_event,
            data_to_be_stored=data_to_be_stored
        )


