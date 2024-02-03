from app.logic.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_form import Form, NewForm, checkboxInput
from app.objects.abstract_objects.abstract_buttons import Button
from app.objects.abstract_objects.abstract_lines import ListOfLines
from app.logic.events.constants import *
from app.logic.events.volunteer_allocation.track_state_in_volunteer_allocation import get_current_cadet_id
from app.backend.cadets import cadet_name_from_id
from app.logic.events.events_in_state import get_event_from_state
from app.backend.volunteers.volunteer_allocation import volunteer_ids_associated_with_cadet_at_specific_event, \
    remove_volunteer_and_cadet_association, delete_volunteer_with_id_at_event, \
    get_volunteer_name_and_associated_cadets_for_event

VOLUNTEERS= "volunteers"

def display_form_volunteer_extraction_from_master_records_if_cadet_is_deleted_or_cancelled(interface: abstractInterface)-> Form:
    cadet_id = get_current_cadet_id(interface)
    cadet_name = cadet_name_from_id(cadet_id)

    checkbox = checkbox_for_volunteers(interface=interface, cadet_id=cadet_id)
    return Form(ListOfLines([
        "Cadet %s has been deleted or registration cancelled, if any of the following volunteers are still available to volunteer then tick their names" % cadet_name,
        checkbox,
        Button(SAVE_CHANGES)
    ]))

def checkbox_for_volunteers(interface: abstractInterface, cadet_id: str) -> checkboxInput:
    dict_of_relevant_volunteers = get_dict_of_relevant_volunteers_with_ids(interface=interface, cadet_id=cadet_id)
    list_of_relevant_volunteers = list(dict_of_relevant_volunteers.keys())
    list_of_relevant_volunteers_as_dict_checked = dict([(volunteer, False) for volunteer in list_of_relevant_volunteers])
    list_of_relevant_volunteers_as_dict = dict([(volunteer, volunteer) for volunteer in list_of_relevant_volunteers])

    return checkboxInput(dict_of_labels=list_of_relevant_volunteers_as_dict,
                      dict_of_checked=list_of_relevant_volunteers_as_dict_checked,
                      input_name=VOLUNTEERS,
                      input_label="Select available volunteers")


def get_dict_of_relevant_volunteers_with_ids(interface: abstractInterface, cadet_id: str) -> dict:
    event = get_event_from_state(interface)

    ## list of volunteers at event
    list_of_volunteers_ids = volunteer_ids_associated_with_cadet_at_specific_event(event=event, cadet_id=cadet_id)
    list_of_relevant_volunteer_names = [get_volunteer_name_and_associated_cadets_for_event(
        event=event, volunteer_id=volunteer_id, cadet_id=cadet_id) for volunteer_id in list_of_volunteers_ids
    ]

    return dict([volunteer, id] for volunteer, id in zip(list_of_relevant_volunteer_names, list_of_volunteers_ids))


def post_form_volunteer_extraction_from_master_records_if_cadet_is_deleted_or_cancelled(interface: abstractInterface)-> NewForm:
    ## only one button could have been pressed
    cadet_id = get_current_cadet_id(interface)
    dict_of_relevant_volunteers_with_ids = get_dict_of_relevant_volunteers_with_ids(interface=interface, cadet_id=cadet_id)
    volunteers_checked_in_form= interface.value_of_multiple_options_from_form(VOLUNTEERS)
    list_of_relevant_volunteers = list(dict_of_relevant_volunteers_with_ids.keys())
    event = get_event_from_state(interface)

    for volunteer_name in list_of_relevant_volunteers:
        volunteer_id = dict_of_relevant_volunteers_with_ids.get(volunteer_name)
        if volunteer_name in volunteers_checked_in_form:
            ## just remove cadet association
            remove_volunteer_and_cadet_association(volunteer_id=volunteer_id, cadet_id=cadet_id, event=event)
        else:
            ## delete volunteer entirely
            delete_volunteer_with_id_at_event(volunteer_id=volunteer_id, event=event)

    ## next cadet
    return NewForm(WA_VOLUNTEER_EXTRACTION_LOOP_IN_VIEW_EVENT_STAGE)

