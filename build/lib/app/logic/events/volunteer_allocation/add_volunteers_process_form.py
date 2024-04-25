from typing import List

from app.objects.constants import NoDaysSelected
from app.objects.volunteers_at_event import VolunteerAtEvent

from app.backend.forms.form_utils import get_availablity_from_form
from app.backend.volunteers.volunteer_allocation import \
    DEPRECATE_get_list_of_active_associated_cadet_id_in_mapped_event_data_given_identified_volunteer_and_cadet, \
    add_volunteer_at_event, mark_all_cadets_associated_with_volunteer_at_event_as_no_longer_changed, \
    DEPRECATED_get_list_of_relevant_information, \
    get_list_of_active_associated_cadet_id_in_mapped_event_data_given_identified_volunteer_and_cadet
from app.backend.volunteers.volunteers import add_list_of_cadet_connections_to_volunteer, \
    DEPRECATED_get_volunteer_from_id, get_volunteer_from_id
from app.logic.events.events_in_state import get_event_from_state
from app.logic.events.volunteer_allocation.add_volunteer_to_event_form_contents import AVAILABILITY, \
    MAKE_CADET_CONNECTION, PREFERRED_DUTIES, SAME_OR_DIFFERENT, ANY_OTHER_INFORMATION, NOTES
from app.logic.events.volunteer_allocation.track_state_in_volunteer_allocation import get_current_volunteer_id_at_event
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.day_selectors import no_days_selected
from app.objects.events import Event
from app.objects.relevant_information_for_volunteers import ListOfRelevantInformationForVolunteer


def add_volunteer_at_event_with_form_contents(interface: abstractInterface):

    try:
        volunteer_at_event = get_volunteer_at_event_from_form_contents(interface)
    except NoDaysSelected as e:
        interface.log_error(str(e))
        return

    add_volunteer_at_event(interface=interface,
                           event=get_event_from_state(interface),
                           volunteer_at_event=volunteer_at_event)

    list_of_cadet_ids_to_permanently_connect = get_list_of_cadet_ids_to_permanently_connect_from_form(interface=interface)
    add_list_of_cadet_connections_to_volunteer(interface=interface,
                                               volunteer_id=volunteer_at_event.volunteer_id,
                                               list_of_connected_cadet_ids=list_of_cadet_ids_to_permanently_connect)

    interface.save_stored_items()


def get_volunteer_at_event_from_form_contents(interface: abstractInterface):

    volunteer_id = get_current_volunteer_id_at_event(interface)
    event =get_event_from_state(interface)
    availability = get_availablity_from_form(interface=interface, event=event, input_name=AVAILABILITY)

    if no_days_selected(availability, possible_days=event.weekdays_in_event()):
        volunteer = get_volunteer_from_id(interface=interface, volunteer_id=volunteer_id)
        raise NoDaysSelected("No days selected for volunteer %s at event - not adding this volunteer - you might want to add manually later" % volunteer.name)

    list_of_associated_cadet_id = get_list_of_active_associated_cadet_id_in_mapped_event_data_given_identified_volunteer_and_cadet(interface=interface, event=event, volunteer_id=volunteer_id)
    any_other_information = get_any_other_information(volunteer_id=volunteer_id, event=event)
    preferred_duties = get_preferred_duties_from_form(interface)
    same_or_different = get_same_or_different_from_form(interface)
    notes = interface.value_from_form(NOTES)

    volunteer_at_event = VolunteerAtEvent(
        volunteer_id=volunteer_id,
        availablity=availability,
        list_of_associated_cadet_id=list_of_associated_cadet_id,
        preferred_duties=preferred_duties,
        same_or_different=same_or_different,
        any_other_information=any_other_information,
        notes=notes
    )

    return volunteer_at_event

def get_list_of_cadet_ids_to_permanently_connect_from_form(interface: abstractInterface) -> List[str]:
    ## return list of str
    try:
        return interface.value_of_multiple_options_from_form(MAKE_CADET_CONNECTION)
    except:
        ## already connected
        return []



def get_any_other_information(event: Event, volunteer_id: str) -> str:
    list_of_relevant_information = DEPRECATED_get_list_of_relevant_information(volunteer_id=volunteer_id, event=event)

    return first_valid_other_information(list_of_relevant_information)

def first_valid_other_information(list_of_relevant_information: ListOfRelevantInformationForVolunteer) -> str:
    for relevant_information in list_of_relevant_information:
        try:
            return relevant_information.details.any_other_information
        except:
            continue

    return ""


def get_preferred_duties_from_form(interface: abstractInterface) -> str:
    return interface.value_from_form(PREFERRED_DUTIES)


def get_same_or_different_from_form(interface: abstractInterface) -> str:
    return interface.value_from_form(SAME_OR_DIFFERENT)
