from app.backend.forms.swaps import is_ready_to_swap
from app.logic.events.volunteer_rota.volunteer_targets import save_volunteer_targets

from app.objects.volunteers_at_event import ListOfVolunteersAtEvent

from app.backend.volunteers.volunteer_allocation import     make_volunteer_unavailable_on_day, make_volunteer_available_on_day
from app.backend.volunteers.volunteer_rota import delete_role_at_event_for_volunteer_on_day, \
    copy_across_duties_for_volunteer_at_event_from_one_day_to_all_other_days, \
    update_role_and_group_at_event_for_volunteer_on_all_days_when_available, \
    copy_earliest_valid_role_and_overwrite_for_volunteer, copy_earliest_valid_role_to_all_empty_for_volunteer
from app.backend.volunteers.volunteer_rota_data import get_data_to_be_stored_for_volunteer_rota_page, \
    get_last_role_for_volunteer_id
from app.data_access.configuration.configuration import VOLUNTEER_SKILLS
from app.logic.events.volunteer_rota.edit_cadet_connections_for_event_from_rota import \
    display_form_edit_cadet_connections_from_rota
from app.logic.events.volunteer_rota.edit_volunteer_details_from_rota import \
    display_form_confirm_volunteer_details_from_rota
from app.logic.events.volunteer_rota.edit_volunteer_skills_from_rota import \
    display_form_edit_individual_volunteer_skills_from_rota
from app.logic.events.volunteer_rota.elements_in_volunteer_rota_page import SKILLS_FILTER, \
    get_available_filter_name_for_day, from_filter_entry_to_option, COPY_ALL_ROLES_BUTTON_LABEL, \
    COPY_ALL_FIRST_ROLE_BUTTON_LABEL
from app.logic.events.volunteer_rota.rota_state import save_skills_filter_to_state, save_availablity_filter_to_state
from app.logic.events.volunteer_rota.swapping import get_list_of_swap_buttons
from app.logic.events.events_in_state import get_event_from_state
from app.logic.events.volunteer_rota.parse_data_fields_in_rota import update_details_from_form_for_volunteer_at_event
from app.logic.events.volunteer_rota.volunteer_table_buttons import *
from app.logic.volunteers.volunteer_state import update_state_with_volunteer_id
from app.objects.abstract_objects.abstract_form import NewForm


def update_volunteer_skills_filter(interface: abstractInterface):

    ticked_skills = interface.value_of_multiple_options_from_form(SKILLS_FILTER)
    dict_of_skills = dict([
        (skill, skill in ticked_skills)
        for skill in VOLUNTEER_SKILLS
    ])
    save_skills_filter_to_state(interface=interface, dict_of_skills=dict_of_skills)

def update_volunteer_availability_filter(interface: abstractInterface):
    event = get_event_from_state(interface)
    availabilty_filter_dict = dict(
        [
            (day.name, update_volunteer_availability_for_day(interface=interface, day=day))
            for day in event.weekdays_in_event()
        ]
    )

    save_availablity_filter_to_state(interface=interface, availability_filter_dict=availabilty_filter_dict)

def update_volunteer_availability_for_day(interface: abstractInterface, day: Day) -> str:
    form_entry_name =get_available_filter_name_for_day(day)
    form_value = interface.value_from_form(form_entry_name)
    option_chosen = from_filter_entry_to_option(form_value)
    return option_chosen


def get_list_of_volunteer_name_buttons(interface: abstractInterface)-> list:
    event = get_event_from_state(interface)
    volunteer_name_buttons_dict =get_dict_of_volunteer_name_buttons_and_volunteer_ids(interface=interface, event=event)
    list_of_volunteer_name_buttons = list(volunteer_name_buttons_dict.keys())

    return list_of_volunteer_name_buttons


def action_if_volunteer_button_pressed(interface: abstractInterface, volunteer_button: str) -> NewForm:
    event = get_event_from_state(interface)
    volunteer_name_buttons_dict =get_dict_of_volunteer_name_buttons_and_volunteer_ids(interface=interface,
                                                                                      event=event)

    volunteer_id = volunteer_name_buttons_dict[volunteer_button]
    update_state_with_volunteer_id(interface=interface, volunteer_id=volunteer_id)

    return interface.get_new_form_given_function(display_form_confirm_volunteer_details_from_rota)

def get_all_day_sort_buttons(interface:abstractInterface):
    event = get_event_from_state(interface)

    return get_list_of_day_button_values(event)

def get_all_location_buttons(interface: abstractInterface):
    event =get_event_from_state(interface)
    all_location_buttons =list_of_all_location_button_names(interface=interface, event=event)

    return all_location_buttons


def get_all_skill_buttons(interface: abstractInterface):
    event =get_event_from_state(interface)
    all_skill_buttons = list_of_all_skills_buttons(interface=interface, event=event)

    return all_skill_buttons

def get_all_copy_previous_role_buttons(interface: abstractInterface):
    event =get_event_from_state(interface)
    all_copy_previous_role_buttons = list_of_all_copy_previous_roles_buttons(interface=interface, event=event)

    return all_copy_previous_role_buttons

def get_all_copy_overwrite_individual_role_buttons(interface: abstractInterface):
    event =get_event_from_state(interface)

    return get_list_of_copy_overwrite_buttons_for_individual_volunteers(interface=interface, event=event)

def get_all_copy_fill_individual_role_buttons(interface: abstractInterface):
    event =get_event_from_state(interface)

    return get_list_of_copy_fill_buttons_for_individual_volunteers(interface=interface, event=event)


def get_all_make_available_buttons(interface: abstractInterface):
    event =get_event_from_state(interface)
    all_buttons = get_list_of_make_available_button_values(interface=interface, event=event)

    return all_buttons

def get_all_copy_buttons(interface: abstractInterface):
    return get_all_copy_overwrite_individual_role_buttons(interface)+get_all_copy_fill_individual_role_buttons(interface)+\
            [COPY_ALL_ROLES_BUTTON_LABEL, COPY_ALL_FIRST_ROLE_BUTTON_LABEL]+get_all_copy_previous_role_buttons(interface)

def get_all_swap_buttons(interface: abstractInterface):
    event = get_event_from_state(interface)
    return get_list_of_swap_buttons(interface=interface, event=event)

def get_all_remove_role_buttons(interface: abstractInterface):
    event = get_event_from_state(interface)
    return get_list_of_remove_role_buttons(interface=interface, event=event)

def get_all_make_unavailable_buttons(interface: abstractInterface):
    event = get_event_from_state(interface)
    return get_list_of_make_unavailable_buttons(interface=interface, event=event)


def action_if_location_button_pressed(interface: abstractInterface, location_button: str) -> NewForm:
    volunteer_id = from_location_button_to_volunteer_id(location_button)
    update_state_with_volunteer_id(interface=interface, volunteer_id=volunteer_id)

    return interface.get_new_form_given_function(display_form_edit_cadet_connections_from_rota)


def action_if_volunteer_skills_button_pressed(interface: abstractInterface, volunteer_skills_button: str) -> NewForm:
    volunteer_id = from_skills_button_to_volunteer_id(volunteer_skills_button)
    update_state_with_volunteer_id(interface=interface, volunteer_id=volunteer_id)

    return interface.get_new_form_given_function(display_form_edit_individual_volunteer_skills_from_rota)

def update_if_copy_button_pressed(interface: abstractInterface, copy_button: str):

    if copy_button==COPY_ALL_ROLES_BUTTON_LABEL:
        update_if_copy_first_role_to_empty_roles_button_pressed(interface=interface)
    elif copy_button == COPY_ALL_FIRST_ROLE_BUTTON_LABEL:
        update_if_copy_first_role_and_overwrite_button_pressed(interface=interface)
    elif copy_button in get_all_copy_previous_role_buttons(interface=interface):
        update_if_copy_previous_role_button_pressed(interface=interface, copy_button=copy_button)
    elif copy_button in get_all_copy_overwrite_individual_role_buttons(interface):
        update_if_individual_copy_overwrite_button_pressed(interface=interface, copy_button=copy_button)
    elif copy_button in get_all_copy_fill_individual_role_buttons(interface):
        update_if_individual_copy_fill_button_pressed(interface=interface, copy_button=copy_button)
    else:
        raise Exception("can't handle button %s" % copy_button)

def update_if_individual_copy_overwrite_button_pressed(interface: abstractInterface, copy_button: str):
    volunteer_id, day = from_known_button_to_volunteer_id_and_day(copy_button)
    event = get_event_from_state(interface)

    copy_across_duties_for_volunteer_at_event_from_one_day_to_all_other_days(interface=interface, event=event,
                                                                             volunteer_id=volunteer_id, day=day,
                                                                             allow_replacement=True)

def update_if_individual_copy_fill_button_pressed(interface: abstractInterface, copy_button: str):
    volunteer_id, day = from_known_button_to_volunteer_id_and_day(copy_button)
    event = get_event_from_state(interface)

    copy_across_duties_for_volunteer_at_event_from_one_day_to_all_other_days(interface=interface, event=event,
                                                                             volunteer_id=volunteer_id, day=day,
                                                                             allow_replacement=False)



def update_if_copy_previous_role_button_pressed(interface: abstractInterface, copy_button: str):
    volunteer_id = from_previous_role_copy_button_to_volunteer_id(copy_button)
    event = get_event_from_state(interface)
    previous_role_and_group = get_last_role_for_volunteer_id(interface=interface, volunteer_id=volunteer_id, avoid_event=event)

    if previous_role_and_group.missing:
        return

    update_role_and_group_at_event_for_volunteer_on_all_days_when_available(interface=interface,
                                                                            event=event,
                                                                            volunteer_id=volunteer_id,
                                                                            new_role_and_group=previous_role_and_group,
                                                                        )


def update_if_copy_first_role_to_empty_roles_button_pressed(interface: abstractInterface):
    list_of_volunteers_at_event = get_list_of_volunteers_at_event(interface)
    event = get_event_from_state(interface)
    for volunteer in list_of_volunteers_at_event:
        volunteer_id = volunteer.volunteer_id
        copy_earliest_valid_role_to_all_empty_for_volunteer(interface=interface,
                                                            event=event,
                                                            volunteer_id=volunteer_id)




def update_if_copy_first_role_and_overwrite_button_pressed(interface: abstractInterface):
    list_of_volunteers_at_event = get_list_of_volunteers_at_event(interface)
    event = get_event_from_state(interface)

    for volunteer in list_of_volunteers_at_event:
        volunteer_id = volunteer.volunteer_id
        copy_earliest_valid_role_and_overwrite_for_volunteer(interface=interface,
                                                             event=event,
                                                             volunteer_id=volunteer_id)


def update_if_make_available_button_pressed(interface: abstractInterface, available_button: str):
    volunteer_id, day =  from_known_button_to_volunteer_id_and_day(available_button)
    event = get_event_from_state(interface)
    make_volunteer_available_on_day(interface=interface, volunteer_id=volunteer_id, event=event, day=day)


def update_if_make_unavailable_button_pressed(interface: abstractInterface, unavailable_button: str):
    volunteer_id, day =  from_known_button_to_volunteer_id_and_day(unavailable_button)
    event = get_event_from_state(interface)
    make_volunteer_unavailable_on_day(interface=interface,
                                      volunteer_id=volunteer_id,
                                      event=event,
                                      day=day)

def update_if_remove_role_button_pressed(interface: abstractInterface, remove_button: str):
    volunteer_id, day =  from_known_button_to_volunteer_id_and_day(remove_button)
    event = get_event_from_state(interface)
    delete_role_at_event_for_volunteer_on_day(interface=interface, event=event, day=day, volunteer_id=volunteer_id)



def save_all_information_and_filter_state_in_rota_page(interface: abstractInterface):
    ready_to_swap = is_ready_to_swap(interface)
    if ready_to_swap:
        return

    save_all_information_in_rota_page(interface)
    save_volunteer_targets(interface)
    ### FILTERS
    update_volunteer_skills_filter(interface)
    update_volunteer_availability_filter(interface)



def save_all_information_in_rota_page(interface: abstractInterface):
    list_of_volunteers_at_event = get_list_of_volunteers_at_event(interface)

    for volunteer_at_event in list_of_volunteers_at_event:
        try:
            update_details_from_form_for_volunteer_at_event(
                interface=interface,
                volunteer_at_event=volunteer_at_event,
            )
        except Exception as e:
            ## perfectly fine if
            print("Can't volunteer %s: error code %s probably because was filtered out" % (str(volunteer_at_event), str(e)))


def get_list_of_volunteers_at_event(interface: abstractInterface) -> ListOfVolunteersAtEvent:
    event = get_event_from_state(interface)
    data_to_be_stored = get_data_to_be_stored_for_volunteer_rota_page(interface=interface, event=event)

    return data_to_be_stored.list_of_volunteers_at_event

