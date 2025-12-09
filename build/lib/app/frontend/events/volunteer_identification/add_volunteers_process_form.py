from app.backend.events.event_warnings import add_new_event_warning_checking_for_duplicate
from app.objects.cadets import ListOfCadets
from app.objects.composed.volunteers_at_event_with_registration_data import RegistrationDataForVolunteerAtEvent
from app.objects.event_warnings import VOLUNTEER_AVAILABILITY
from app.data_access.configuration.fixed import MEDIUM_PRIORITY
from app.objects.volunteers import Volunteer

from app.backend.volunteers.list_of_volunteers import get_volunteer_from_id

from app.objects.utilities.exceptions import NoDaysSelected

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
    NOTES, VOLUNTEER_STATUS_IN_FORM, ALERT_FORM, save_alert,
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
    event = get_event_from_state(interface)

    registration_data = get_volunteer_at_event_registration_data_from_form_contents(
        interface=interface, volunteer=volunteer
    )

    add_volunteer_at_event(
        object_store=interface.object_store,
        event=event,
        volunteer=volunteer,
        registration_data=registration_data
    )

    log_any_alert_warnings(interface=interface, volunteer=volunteer)

    update_cadet_connections_when_volunteer_already_at_event(
        object_store=interface.object_store, event=event, volunteer=volunteer
    )


def get_volunteer_from_state(interface: abstractInterface) -> Volunteer:
    volunteer_id = get_current_volunteer_id_at_event(interface)
    volunteer = get_volunteer_from_id(
        object_store=interface.object_store, volunteer_id=volunteer_id
    )
    return volunteer


def get_volunteer_at_event_registration_data_from_form_contents(
    interface: abstractInterface, volunteer: Volunteer
) -> RegistrationDataForVolunteerAtEvent:
    event = get_event_from_state(interface)
    availability_in_form = get_availablity_from_form(
        interface=interface, event=event, input_name=AVAILABILITY
    )

    if no_days_selected_from_available_days(
        availability_in_form, possible_days=event.days_in_event()
    ):
        message = "Volunteer %s did not select any days in form" % volunteer.name
        interface.log_error(message)

        add_new_event_warning_checking_for_duplicate(object_store=interface.object_store,
                                                     event=get_event_from_state(interface),
                                                     warning=message, category=VOLUNTEER_AVAILABILITY,
                                                     priority=MEDIUM_PRIORITY,
                                                     auto_refreshed=False)  ## warning will sit on system until cleared


    any_other_information = get_any_other_information(
        interface=interface, volunteer=volunteer, event=event
    )
    preferred_duties_in_form = get_preferred_duties_from_form(interface)
    same_or_different_in_form = get_same_or_different_from_form(interface)
    status_in_form = get_status_from_form(interface)
    notes_in_form = interface.value_from_form(NOTES)

    return RegistrationDataForVolunteerAtEvent(
        availablity=availability_in_form,
        list_of_associated_cadets=ListOfCadets([]),
        any_other_information=any_other_information,
        preferred_duties=preferred_duties_in_form,
        same_or_different=same_or_different_in_form,
        self_declared_status=status_in_form,
        notes=notes_in_form
    )


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

def get_status_from_form(interface: abstractInterface) -> str:
    return interface.value_from_form(VOLUNTEER_STATUS_IN_FORM)


def get_same_or_different_from_form(interface: abstractInterface) -> str:
    try:
        return interface.value_from_form(SAME_OR_DIFFERENT)
    except:
        ## not in original form
        return ""

def log_any_alert_warnings(interface: abstractInterface, volunteer: Volunteer):
    alert = get_alert_warning_from_form(interface, volunteer)
    if len(alert)==0:
        return

    add_new_event_warning_checking_for_duplicate(object_store=interface.object_store,
                                                 event=get_event_from_state(interface),
                                                 warning=alert, category=VOLUNTEER_AVAILABILITY, priority=MEDIUM_PRIORITY,
                                                 auto_refreshed=False)  ## warning will sit on system until cleared


def get_alert_warning_from_form(interface: abstractInterface, volunteer: Volunteer):
    alert = interface.value_from_form(ALERT_FORM)
    if save_alert.pressed(interface.last_button_pressed()) and len(alert)==0:
        alert = "Issue with registration details for %s to be confirmed" % volunteer
    else:
        alert = "%s: %s flagged on import" % (volunteer, alert)

    return alert
