from typing import Dict, Union

from app.backend.data.volunteer_allocation import remove_volunteer_and_cadet_association_at_event, \
    delete_volunteer_with_id_at_event, get_volunteer_at_event
from app.backend.cadets import cadet_name_from_id
from app.backend.wa_import.update_cadets_at_event import mark_cadet_at_event_as_unchanged, has_cadet_at_event_changed, \
    get_cadet_at_event_for_cadet_id
from app.backend.volunteers.volunteer_allocation import volunteer_ids_associated_with_cadet_at_specific_event, \
    get_volunteer_name_and_associated_cadets_for_event, any_other_cadets_for_volunteer_at_event_apart_from_this_one, \
    update_volunteer_availability_at_event
from app.backend.form_utils import get_availability_checkbox, get_availablity_from_form

from app.logic.events.volunteer_rota.rota_state import clear_cadet_id_for_rota_at_event, \
    get_and_save_next_cadet_id_in_event_data, get_current_cadet_id_for_rota_at_event
from app.logic.events.constants import *
from app.logic.events.events_in_state import get_event_from_state
from app.objects.constants import NoMoreData

from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_form import Form, NewForm, checkboxInput
from app.objects.abstract_objects.abstract_buttons import Button
from app.objects.abstract_objects.abstract_lines import ListOfLines, Line
from app.objects.events import Event

AVAILABILITY_NAME = "availability"
INCLUSION_NAME = "inclusion_name"
INCLUDE_VOLUNTEER = "include"


# VOLUNTEER_ROTA_INITIALISE_LOOP_IN_VIEW_EVENT_STAGE
def volunteer_rota_initialise_changed_cadet_loop(interface: abstractInterface)-> NewForm:

    clear_cadet_id_for_rota_at_event(interface)

    return interface.get_new_display_form_given_function(volunteer_rota_check_changed_cadet_loop)


# VOLUNTEER_ROTA_CHECK_LOOP_IN_VIEW_EVENT_STAGE
def volunteer_rota_check_changed_cadet_loop(interface: abstractInterface) -> Union[Form, NewForm]:
    try:
        cadet_id = get_and_save_next_cadet_id_in_event_data(interface)
    except NoMoreData:
        ## main volunteer rota form
        return goto_main_rota_form(interface)

    return check_cadet_in_loop(interface=interface, cadet_id=cadet_id)

def goto_main_rota_form(interface:abstractInterface)-> NewForm:
    return interface.get_new_display_form_given_function(volunteer_rota_initialise_changed_cadet_loop)


def check_cadet_in_loop(interface: abstractInterface, cadet_id: str) -> Union[Form, NewForm]:
    event = get_event_from_state(interface)
    cadet_has_changed = has_cadet_at_event_changed(cadet_id=cadet_id, event=event)

    if cadet_has_changed:
        return display_form_volunteer_rota_check_changed_cadet_loop(interface=interface, cadet_id=cadet_id)
    else:
        return goto_next_cadet_in_loop(interface)

def goto_next_cadet_in_loop(interface: abstractInterface) -> NewForm:
    return interface.get_new_display_form_given_function(volunteer_rota_check_changed_cadet_loop)

def display_form_volunteer_rota_check_changed_cadet_loop(interface: abstractInterface, cadet_id: str) -> Form:
    event = get_event_from_state(interface)
    cadet_at_event = get_cadet_at_event_for_cadet_id(cadet_id=cadet_id, event=event)
    cadet_name = cadet_name_from_id(cadet_id)
    cadet_status_as_str = cadet_at_event.status.name
    cadet_availability_as_str = str(cadet_at_event.availability)

    list_of_volunteer_form_lines = get_list_of_volunteer_form_lines(interface=interface, cadet_id=cadet_id)

    return Form(ListOfLines([
        "Registration for cadet %s has been modified recently, status is now %s, availability is now %s" % (cadet_name, cadet_status_as_str, cadet_availability_as_str),
        "Select voluteers that are still available, and modify availability if appropriate",
        list_of_volunteer_form_lines,
        Button(SAVE_CHANGES)
    ]))


def get_list_of_volunteer_form_lines(interface: abstractInterface, cadet_id: str) -> ListOfLines:
    dict_of_relevant_volunteers = get_dict_of_relevant_volunteer_names_and_association_cadets_with_id_values(interface=interface, cadet_id=cadet_id)
    list_of_volunteer_lines = [get_volunteer_form_line(interface=interface,
                                                       volunteer_and_others=volunteer_and_others,
                                                       volunteer_id=volunteer_id,
                                                       cadet_id=cadet_id)
                               for volunteer_and_others, volunteer_id in dict_of_relevant_volunteers.items()
                               ]

    return ListOfLines(list_of_volunteer_lines)

def get_volunteer_form_line(interface: abstractInterface, volunteer_and_others: str, volunteer_id: str, cadet_id: str) -> checkboxInput:
    event = get_event_from_state(interface)
    current_cadet_is_active = is_current_cadet_active_at_event(cadet_id=cadet_id, event=event)
    if current_cadet_is_active:
        ## must be availability change
        volunteer_at_event = get_volunteer_at_event(event=event, volunteer_id=volunteer_id)
        current_availability = volunteer_at_event.availablity

        return get_availability_checkbox(
            availability=current_availability,
            event=event,
            input_label="Update availability for volunteer",
            input_name=form_name_given_volunteer_and_type(type=AVAILABILITY_NAME, volunteer_id=volunteer_id)
        )
    else:
        ## must be status change eg
        ## checkbox is True only if other cadets
        has_other_cadets = any_other_cadets_for_volunteer_at_event_apart_from_this_one(volunteer_id=volunteer_id,
                                                                                       event=event,
                                                                                       cadet_id=cadet_id)
        relevant_volunteers_as_dict_checked = {INCLUDE_VOLUNTEER: has_other_cadets}
        relevant_volunteers_as_dict_labels = {INCLUDE_VOLUNTEER: volunteer_and_others}

        return checkboxInput(dict_of_labels=relevant_volunteers_as_dict_labels,
                          dict_of_checked=relevant_volunteers_as_dict_checked,
                          input_name=form_name_given_volunteer_and_type(type=INCLUSION_NAME, volunteer_id=volunteer_id),
                          input_label="Select volunteer if still available")


def form_name_given_volunteer_and_type(type: str, volunteer_id:str):
    return type+"_"+volunteer_id

def is_current_cadet_active_at_event(cadet_id: str, event: Event)-> bool:
    cadet_at_event = get_cadet_at_event_for_cadet_id(event=event, cadet_id=cadet_id)

    return cadet_at_event.is_active()

def get_dict_of_relevant_volunteer_names_and_association_cadets_with_id_values(interface: abstractInterface, cadet_id: str) \
        -> Dict[str, str]:
    event = get_event_from_state(interface)

    ## list of volunteers at event
    list_of_volunteers_ids = volunteer_ids_associated_with_cadet_at_specific_event(event=event, cadet_id=cadet_id)
    list_of_relevant_volunteer_names_and_other_cadets = [get_volunteer_name_and_associated_cadets_for_event(
        event=event, volunteer_id=volunteer_id, cadet_id=cadet_id) for volunteer_id in list_of_volunteers_ids
    ]

    return dict([volunteer_and_any_other_cadets, id] for volunteer_and_any_other_cadets, id in
                zip(list_of_relevant_volunteer_names_and_other_cadets, list_of_volunteers_ids))


def post_form_volunteer_rota_check_changed_cadet_loop(interface: abstractInterface)-> NewForm:
    cadet_id=get_current_cadet_id_for_rota_at_event(interface)

    dict_of_relevant_volunteers_with_ids = get_dict_of_relevant_volunteer_names_and_association_cadets_with_id_values(interface=interface, cadet_id=cadet_id)
    for volunteer_id in list(dict_of_relevant_volunteers_with_ids.values()):
        modify_specific_volunteer_when_cadet_changed(interface=interface, volunteer_id=volunteer_id, cadet_id=cadet_id)

    event = get_event_from_state(interface)
    mark_cadet_at_event_as_unchanged(cadet_id=cadet_id, event=event)
    ## next cadet
    return goto_next_cadet_in_loop(interface)

def modify_specific_volunteer_when_cadet_changed(interface: abstractInterface, volunteer_id: str, cadet_id: str):

    ##  Some thoughts... if a cadet goes from active to cancelled/deleted then they will show up here
    ##  if however they are going in the other direction (cancelled/deleted to active) then they won't
    ##  because the volunteer just won't exist. However they will be added in the volunteer allocation stage
    event = get_event_from_state(interface)
    current_cadet_is_active = is_current_cadet_active_at_event(cadet_id=cadet_id, event=event)
    if current_cadet_is_active:
        modify_specific_volunteer_availability_when_cadet_changed(interface=interface, volunteer_id=volunteer_id)
    else:
        modify_specific_volunteer_linkage_at_event_when_cadet_changed(interface=interface, volunteer_id=volunteer_id, cadet_id=cadet_id)

def modify_specific_volunteer_availability_when_cadet_changed(interface: abstractInterface, volunteer_id: str):
    event = get_event_from_state(interface)
    availability = get_availablity_from_form(interface=interface, event=event, input_name=
                                             form_name_given_volunteer_and_type(volunteer_id=volunteer_id, type=AVAILABILITY_NAME))

    update_volunteer_availability_at_event(volunteer_id=volunteer_id, availability=availability, event=event)

def modify_specific_volunteer_linkage_at_event_when_cadet_changed(interface: abstractInterface, volunteer_id: str, cadet_id: str):
    event = get_event_from_state(interface)
    include_volunteer = form_name_given_volunteer_and_type(volunteer_id=volunteer_id, type=INCLUSION_NAME)
    current_cadet_is_active = is_current_cadet_active_at_event(cadet_id=cadet_id, event=event)
    assert not current_cadet_is_active

    if include_volunteer:
        remove_volunteer_and_cadet_association_at_event(volunteer_id=volunteer_id, cadet_id=cadet_id, event=event)
    else:
        delete_volunteer_with_id_at_event(volunteer_id=volunteer_id, event=event)

