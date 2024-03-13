from app.backend.cadets import cadet_name_from_id
from app.backend.data.volunteer_allocation import get_volunteer_at_event, \
    remove_volunteer_and_cadet_association_at_event, delete_volunteer_with_id_at_event
from app.backend.forms.form_utils import get_availability_checkbox, get_availablity_from_form
from app.backend.volunteers.volunteer_allocation import \
    get_dict_of_relevant_volunteer_names_and_association_cadets_with_id_values, \
    any_other_cadets_for_volunteer_at_event_apart_from_this_one, update_volunteer_availability_at_event, \
    is_current_cadet_active_at_event
from app.backend.volunteers.volunteers import get_volunteer_from_id
from app.backend.wa_import.update_cadets_at_event import get_cadet_at_event_for_cadet_id
from app.logic.events.constants import SAVE_CHANGES
from app.logic.events.events_in_state import get_event_from_state
from app.objects.abstract_objects.abstract_buttons import Button
from app.objects.abstract_objects.abstract_form import Form, checkboxInput
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_lines import ListOfLines
from app.objects.events import Event


def display_form_volunteer_rota_check_changed_cadet_when_availability_changed(cadet_id: str, event: Event, interface: abstractInterface) -> Form:
    cadet_at_event = get_cadet_at_event_for_cadet_id(cadet_id=cadet_id, event=event)
    cadet_name = cadet_name_from_id(cadet_id)
    cadet_availability_as_str = str(cadet_at_event.availability)
    save_type_of_form_displayed_for_volunteer_update(interface=interface,
                                                     new_type=UPDATE_AVAILABLE)
    list_of_volunteer_form_lines = get_list_of_volunteer_form_lines_changing_availability(cadet_id=cadet_id, event=event)

    return Form(ListOfLines([
        "Registration for cadet %s has been modified recently, availability is now %s" % (
        cadet_name, cadet_availability_as_str),
        "Modify availability for volunteers if appropriate",
        list_of_volunteer_form_lines,
        Button(SAVE_CHANGES)
    ]))


def display_form_volunteer_rota_check_changed_cadet_when_status_changed_to_deleted_or_cancelled( cadet_id: str,
                                                                                                event: Event,
                                                                                                 interface: abstractInterface) -> Form:
    cadet_at_event = get_cadet_at_event_for_cadet_id(cadet_id=cadet_id, event=event)
    cadet_name = cadet_name_from_id(cadet_id)
    cadet_status_as_str = cadet_at_event.status.name

    list_of_volunteer_form_lines = get_list_of_volunteer_form_lines_changing_status_to_deleted_or_cancelled(
                                                                                                            cadet_id=cadet_id,
                                                                                                            event=event)

    save_type_of_form_displayed_for_volunteer_update(interface=interface,
                                                     new_type=UPDATE_WHEN_DELETED_OR_CANCELLED)

    return Form(ListOfLines([
        "Registration for cadet %s has been modified recently, status is now %s" % (cadet_name, cadet_status_as_str),
        "Select voluteers that are still available",
        list_of_volunteer_form_lines,
        Button(SAVE_CHANGES)
    ]))




def get_list_of_volunteer_form_lines_changing_availability(cadet_id: str, event: Event) -> ListOfLines:
    dict_of_relevant_volunteers = get_dict_of_relevant_volunteer_names_and_association_cadets_with_id_values(
        cadet_id=cadet_id, event=event)
    list_of_volunteer_lines = [get_volunteer_form_line_changing_availability(event=event,
                                                       volunteer_id=volunteer_id)
                               for volunteer_and_others, volunteer_id in dict_of_relevant_volunteers.items()
                               ]

    return ListOfLines(list_of_volunteer_lines)


def get_list_of_volunteer_form_lines_changing_status_to_deleted_or_cancelled( cadet_id: str, event: Event) -> ListOfLines:
    dict_of_relevant_volunteers = get_dict_of_relevant_volunteer_names_and_association_cadets_with_id_values(
        cadet_id=cadet_id, event=event)
    list_of_volunteer_lines = [get_volunteer_form_line_changing_status_to_deleted_or_cancelled(event=event,
                                                       volunteer_and_others=volunteer_and_others,
                                                       volunteer_id=volunteer_id,
                                                       cadet_id=cadet_id)
                               for volunteer_and_others, volunteer_id in dict_of_relevant_volunteers.items()
                               ]

    return ListOfLines(list_of_volunteer_lines)


def get_volunteer_form_line_changing_availability( volunteer_id: str, event: Event) -> checkboxInput:
    volunteer_at_event = get_volunteer_at_event(event=event, volunteer_id=volunteer_id)
    current_availability = volunteer_at_event.availablity
    volunteer_name = get_volunteer_from_id(volunteer_id)

    return get_availability_checkbox(
        availability=current_availability,
        event=event,
        input_label="Update availability for volunteer %s :" % volunteer_name,
        input_name=form_name_given_volunteer_and_type(type=AVAILABILITY_NAME, volunteer_id=volunteer_id)
    )


def get_volunteer_form_line_changing_status_to_deleted_or_cancelled(event: Event, volunteer_and_others: str, volunteer_id: str, cadet_id: str) -> checkboxInput:

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


AVAILABILITY_NAME = "availability"
INCLUSION_NAME = "inclusion_name"
INCLUDE_VOLUNTEER = "include"


def modify_specific_volunteer_availability_when_cadet_changed(interface: abstractInterface, volunteer_id: str):
    event = get_event_from_state(interface)
    availability = get_availablity_from_form(interface=interface, event=event, input_name=
                                             form_name_given_volunteer_and_type(volunteer_id=volunteer_id, type=AVAILABILITY_NAME))

    update_volunteer_availability_at_event(volunteer_id=volunteer_id, availability=availability, event=event)

def modify_specific_volunteer_linkage_at_event_when_cadet_changed(interface: abstractInterface, volunteer_id: str, cadet_id: str):
    event = get_event_from_state(interface)
    current_cadet_is_active = is_current_cadet_active_at_event(cadet_id=cadet_id, event=event)
    assert not current_cadet_is_active

    volunteer_is_included = INCLUDE_VOLUNTEER in interface.value_of_multiple_options_from_form(
        form_name_given_volunteer_and_type(
        volunteer_id=volunteer_id, type=INCLUSION_NAME
    ))

    if volunteer_is_included:
        remove_volunteer_and_cadet_association_at_event(volunteer_id=volunteer_id, cadet_id=cadet_id, event=event)
    else:
        delete_volunteer_with_id_at_event(volunteer_id=volunteer_id, event=event)

VOLUNTEER_UPDATE_FORM_TYPE ="volunteer_update_form_type"

UPDATE_AVAILABLE = "update_available"
UPDATE_WHEN_DELETED_OR_CANCELLED = "update_when_deleted_or_cancelled"
UPDATE_TYPE_UNKNONW = "update_uknown"

all_update_types = [UPDATE_AVAILABLE, UPDATE_WHEN_DELETED_OR_CANCELLED,UPDATE_TYPE_UNKNONW]

def get_type_of_form_displayed_for_volunteer_update(interface: abstractInterface) -> str:
    return interface.get_persistent_value(VOLUNTEER_UPDATE_FORM_TYPE, default=UPDATE_TYPE_UNKNONW)

def  save_type_of_form_displayed_for_volunteer_update(interface: abstractInterface, new_type: str):
    assert new_type in all_update_types
    interface.set_persistent_value(VOLUNTEER_UPDATE_FORM_TYPE, new_type)

def clear_type_of_form_displayed_for_volunteer_update(interface: abstractInterface):
    interface.set_persistent_value(VOLUNTEER_UPDATE_FORM_TYPE, UPDATE_TYPE_UNKNONW)
