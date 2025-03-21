from app.objects.volunteers import Volunteer

from app.backend.volunteers.volunteers_with_roles_and_groups_at_event import (
    get_all_roles_across_recent_events_for_volunteer_as_dict_latest_first,
)

from app.frontend.forms.form_utils import (
    get_availablity_from_form,
    get_availability_checkbox,
)

from app.backend.volunteers.volunteers_at_event import (
    update_volunteer_availability_at_event,
)
from app.backend.registration_data.volunteer_registration_data import (
    get_dict_of_registration_data_for_volunteers_at_event,
)
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_lines import (
    ListOfLines,
    _______________,
    Line,
)
from app.objects.day_selectors import no_days_selected_from_available_days
from app.objects.events import Event


def get_volunteer_history_and_attendace_checkbox_for_selected_volunteer(interface: abstractInterface, event: Event, volunteer: Volunteer) -> list:
    past_roles = get_text_of_last_roles(
        interface=interface, event=event, volunteer=volunteer
    )
    available_checkbox = Line(
        [
            get_availability_checkbox_for_volunteer_at_event(
                interface=interface, event=event, volunteer=volunteer
            )
        ]
    )


    return ListOfLines([past_roles, _______________, available_checkbox
        ])



def get_text_of_last_roles(
    interface: abstractInterface, event: Event, volunteer: Volunteer
) -> Line:
    all_roles_as_dict = (
        get_all_roles_across_recent_events_for_volunteer_as_dict_latest_first(
            object_store=interface.object_store, volunteer=volunteer, avoid_event=event
        )
    )
    text_as_list = [
        "%s: %s" % (str(event), role) for event, role in all_roles_as_dict.items()
    ]

    text = ", ".join(text_as_list)
    text = "Previous roles: " + text

    return Line([text])


def get_availability_checkbox_for_volunteer_at_event(
    interface: abstractInterface, event: Event, volunteer: Volunteer
):
    registration_data = get_dict_of_registration_data_for_volunteers_at_event(
        object_store=interface.object_store, event=event
    )
    data_for_volunteer = registration_data.get(volunteer)
    availability = data_for_volunteer.availablity
    return get_availability_checkbox(
        availability=availability,
        event=event,
        input_name=input_name_for_volunteer_availability(volunteer),
        input_label="Confirm availability (click volunteers name to save):",
    )


def update_volunteer_availability_at_event_from_rota_with_form_contents(
    interface: abstractInterface,
        event: Event,
        volunteer: Volunteer
):
    availability = get_availablity_from_form(
        interface=interface, event=event, input_name=input_name_for_volunteer_availability(volunteer)
    )

    if no_days_selected_from_available_days(
        availability, possible_days=event.days_in_event()
    ):
        interface.log_error(
            "No days selected for volunteer at event - can't do this - delete volunteer if not available for event"
        )
        return

    update_volunteer_availability_at_event(
        object_store=interface.object_store,
        event=event,
        volunteer=volunteer,
        availability=availability,
    )
    interface.flush_cache_to_store()


AVAILABILITY = "Availability"

def input_name_for_volunteer_availability(volunteer: Volunteer):
    return AVAILABILITY+volunteer.id
