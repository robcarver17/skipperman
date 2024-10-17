from typing import List

from app.OLD_backend.cadets import get_cadet_from_id

from app.objects.cadets import ListOfCadets

from app.objects.exceptions import NoDaysSelected
from app.objects.volunteer_at_event_with_id import VolunteerAtEventWithId

from app.frontend.forms.form_utils import get_availablity_from_form
from app.OLD_backend.volunteers.volunteer_allocation import (
    add_volunteer_at_event,
    get_list_of_active_associated_cadet_id_in_mapped_event_data_given_identified_volunteer_and_cadet,
    get_list_of_relevant_information,
)
from app.OLD_backend.volunteers.volunteers import (
    add_list_of_cadet_connections_to_volunteer,
    DEPRECATE_get_volunteer_from_id,
)
from app.frontend.shared.events_state import get_event_from_state
from app.frontend.events.volunteer_allocation.add_volunteer_to_event_form_contents import (
    AVAILABILITY,
    MAKE_CADET_CONNECTION,
    PREFERRED_DUTIES,
    SAME_OR_DIFFERENT,
    NOTES,
)
from app.frontend.events.volunteer_allocation.track_state_in_volunteer_allocation import (
    get_current_volunteer_id_at_event,
)
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.day_selectors import no_days_selected
from app.objects.events import Event
from app.objects_OLD.relevant_information_for_volunteers import (
    ListOfRelevantInformationForVolunteer,
)


def add_volunteer_at_event_with_form_contents(interface: abstractInterface):
    try:
        volunteer_at_event = get_volunteer_at_event_from_form_contents(interface)
        volunteer = DEPRECATE_get_volunteer_from_id(interface=interface, volunteer_id=volunteer_at_event.volunteer_id) ## FIXME IDEALLY HAVE CLASS THAT ALREADY CONTAINS VOLUNTEER
    except NoDaysSelected as e:
        interface.log_error(str(e))
        return

    add_volunteer_at_event(
        interface=interface,
        event=get_event_from_state(interface),
        volunteer_at_event=volunteer_at_event,
    )

    list_of_cadet_ids_to_permanently_connect = (
        get_list_of_cadet_ids_to_permanently_connect_from_form(interface=interface)
    )
    list_of_cadets_to_connect= ListOfCadets([get_cadet_from_id(data_layer=interface.data, cadet_id=id) for id in list_of_cadet_ids_to_permanently_connect]) ## collapse into previous function
    add_list_of_cadet_connections_to_volunteer(
        data_layer=interface.data,
        volunteer=volunteer,
        list_of_cadets_to_connect=list_of_cadets_to_connect
    )

    interface.flush_cache_to_store()


def get_volunteer_at_event_from_form_contents(interface: abstractInterface):
    volunteer_id = get_current_volunteer_id_at_event(interface)
    event = get_event_from_state(interface)
    availability_in_form = get_availablity_from_form(
        interface=interface, event=event, input_name=AVAILABILITY
    )

    if no_days_selected(availability_in_form, possible_days=event.weekdays_in_event()):
        volunteer = DEPRECATE_get_volunteer_from_id(
            interface=interface, volunteer_id=volunteer_id
        )
        raise NoDaysSelected(
            "No days selected for volunteer %s at event - not adding this volunteer - you might want to add manually later"
            % volunteer.name
        )

    list_of_associated_cadet_id = get_list_of_active_associated_cadet_id_in_mapped_event_data_given_identified_volunteer_and_cadet(
        interface=interface, event=event, volunteer_id=volunteer_id
    )
    any_other_information = get_any_other_information(
        interface=interface, volunteer_id=volunteer_id, event=event
    )
    preferred_duties_in_form = get_preferred_duties_from_form(interface)
    same_or_different_in_form = get_same_or_different_from_form(interface)
    notes_in_form = interface.value_from_form(NOTES)

    volunteer_at_event = VolunteerAtEventWithId(
        volunteer_id=volunteer_id,
        availablity=availability_in_form,
        list_of_associated_cadet_id=list_of_associated_cadet_id,
        preferred_duties=preferred_duties_in_form,
        same_or_different=same_or_different_in_form,
        any_other_information=any_other_information,
        notes=notes_in_form,
    )

    return volunteer_at_event


def get_list_of_cadet_ids_to_permanently_connect_from_form(
    interface: abstractInterface,
) -> List[str]:
    ## return list of str
    try:
        return interface.value_of_multiple_options_from_form(MAKE_CADET_CONNECTION)
    except:
        ## already connected
        return []


def get_any_other_information(
    interface: abstractInterface, event: Event, volunteer_id: str
) -> str:
    list_of_relevant_information = get_list_of_relevant_information(
        interface=interface, volunteer_id=volunteer_id, event=event
    )

    return first_valid_other_information(list_of_relevant_information)


def first_valid_other_information(
    list_of_relevant_information: ListOfRelevantInformationForVolunteer,
) -> str:
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
