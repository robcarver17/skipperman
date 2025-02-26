
from app.objects.volunteers import Volunteer

from app.backend.volunteers.list_of_volunteers import get_volunteer_from_id

from app.objects.exceptions import NoDaysSelected
from app.objects.volunteer_at_event_with_id import VolunteerAtEventWithId

from app.frontend.forms.form_utils import get_availablity_from_form
from app.backend.volunteers.volunteers_at_event import add_volunteer_at_event
from app.backend.registration_data.identified_volunteers_at_event import (
    get_list_of_relevant_information_for_volunteer_in_registration_data,
)
from app.backend.registration_data.cadet_and_volunteer_connections_at_event import (
    update_cadet_connections_when_volunteer_already_at_event,
)
from app.frontend.shared.events_state import get_event_from_state
from app.frontend.events.volunteer_identification.add_volunteer_to_event_form_contents import (
    AVAILABILITY,
    PREFERRED_DUTIES,
    SAME_OR_DIFFERENT,
    NOTES,
)
from app.frontend.events.volunteer_identification.track_state_in_volunteer_allocation import (
    get_current_volunteer_id_at_event,
)
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.day_selectors import no_days_selected_from_available_days
from app.objects.events import Event
from app.objects.relevant_information_for_volunteers import (
    ListOfRelevantInformationForVolunteer,
)


def add_volunteer_at_event_with_form_contents(interface: abstractInterface):
    volunteer = get_volunteer_from_state(interface)
    try:
        volunteer_at_event = get_volunteer_at_event_from_form_contents(
            interface=interface, volunteer=volunteer
        )
    except NoDaysSelected as e:
        interface.log_error(str(e))
        return

    add_volunteer_at_event(
        object_store=interface.object_store,
        event=get_event_from_state(interface),
        volunteer_at_event=volunteer_at_event,
    )
    event =get_event_from_state(interface)
    update_cadet_connections_when_volunteer_already_at_event(
        object_store=interface.object_store, event=event, volunteer=volunteer
    )


def get_volunteer_from_state(interface: abstractInterface) -> Volunteer:
    volunteer_id = get_current_volunteer_id_at_event(interface)
    volunteer = get_volunteer_from_id(
        object_store=interface.object_store, volunteer_id=volunteer_id
    )
    return volunteer


def get_volunteer_at_event_from_form_contents(
    interface: abstractInterface, volunteer: Volunteer
) -> VolunteerAtEventWithId:
    event = get_event_from_state(interface)
    availability_in_form = get_availablity_from_form(
        interface=interface, event=event, input_name=AVAILABILITY
    )

    if no_days_selected_from_available_days(availability_in_form, possible_days=event.days_in_event()):
        raise NoDaysSelected(
            "No days selected for volunteer %s at event - not adding this volunteer - you might want to add manually later"
            % volunteer.name
        )

    any_other_information = get_any_other_information(
        interface=interface, volunteer=volunteer, event=event
    )
    preferred_duties_in_form = get_preferred_duties_from_form(interface)
    same_or_different_in_form = get_same_or_different_from_form(interface)
    notes_in_form = interface.value_from_form(NOTES)

    volunteer_at_event = VolunteerAtEventWithId(
        volunteer_id=volunteer.id,
        availablity=availability_in_form,
        list_of_associated_cadet_id=[],  ## no longer used
        preferred_duties=preferred_duties_in_form,
        same_or_different=same_or_different_in_form,
        any_other_information=any_other_information,
        notes=notes_in_form,
    )

    return volunteer_at_event




def get_any_other_information(
    interface: abstractInterface, event: Event, volunteer: Volunteer
) -> str:
    list_of_relevant_information = (
        get_list_of_relevant_information_for_volunteer_in_registration_data(
            object_store=interface.object_store, event=event, volunteer=volunteer
        )
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
    try:
        return interface.value_from_form(SAME_OR_DIFFERENT)
    except:
        ## not in original form
        return ''
