from typing import List

from app.backend.form_utils import get_availablity_from_form
from app.backend.volunteers.volunteer_allocation import \
    get_list_of_active_associated_cadet_id_in_mapped_event_data_given_identified_volunteer_and_cadet, \
    add_volunteer_at_event
from app.backend.volunteers.volunteers import add_list_of_cadet_connections_to_volunteer
from app.logic.events.events_in_state import get_event_from_state
from app.logic.events.volunteer_allocation.add_volunteer_to_event_form_contents import AVAILABILITY, \
    MAKE_CADET_CONNECTION, PREFERRED_DUTIES, SAME_OR_DIFFERENT, ANY_OTHER_INFORMATION
from app.logic.events.volunteer_allocation.track_state_in_volunteer_allocation import get_current_volunteer_id_at_event
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.day_selectors import no_days_selected


def add_volunteer_at_event_with_form_contents_and_return_true_if_ok(interface: abstractInterface) -> bool:

    volunteer_id = get_current_volunteer_id_at_event(interface)
    event =get_event_from_state(interface)
    availability = get_availablity_from_form(interface=interface, event=event, input_name=AVAILABILITY)
    list_of_cadet_ids_to_permanently_connect = get_list_of_cadet_ids_to_permanently_connect_from_form(interface=interface)

    list_of_associated_cadet_id = get_list_of_active_associated_cadet_id_in_mapped_event_data_given_identified_volunteer_and_cadet(event=event, volunteer_id=volunteer_id)
    any_other_information = get_any_other_information_from_form(interface=interface)
    preferred_duties = get_preferred_duties_from_form(interface)
    same_or_different = get_same_or_different_from_form(interface)

    if no_days_selected(availability, possible_days=event.weekdays_in_event()):
        interface.log_error("No days selected for volunteer at event")
        return False

    add_volunteer_at_event(event=event,volunteer_id=volunteer_id,
                                                             availability=availability,
                                                list_of_associated_cadet_id=list_of_associated_cadet_id,
                                                any_other_information=any_other_information,
                                                preferred_duties=preferred_duties,
                                                same_or_different=same_or_different
                                       )

    add_list_of_cadet_connections_to_volunteer(volunteer_id=volunteer_id,
                                               list_of_connected_cadet_ids=list_of_cadet_ids_to_permanently_connect)

    return True


def get_list_of_cadet_ids_to_permanently_connect_from_form(interface: abstractInterface) -> List[str]:
    ## return list of str
    try:
        return interface.value_of_multiple_options_from_form(MAKE_CADET_CONNECTION)
    except:
        ## already connected
        return []



def get_any_other_information_from_form(interface: abstractInterface) -> str:
    return interface.value_from_form(ANY_OTHER_INFORMATION)


def get_preferred_duties_from_form(interface: abstractInterface) -> str:
    return interface.value_from_form(PREFERRED_DUTIES)


def get_same_or_different_from_form(interface: abstractInterface) -> str:
    return interface.value_from_form(SAME_OR_DIFFERENT)
