from app.objects.volunteers import Volunteer

from app.backend.volunteers.volunteers_with_roles_and_groups_at_event import (
    get_all_roles_across_recent_events_for_volunteer_as_dict_latest_first,
)

from app.frontend.forms.form_utils import (
    get_availablity_from_form,
    get_availability_checkbox,
)

from app.backend.volunteers.volunteers_at_event import delete_volunteer_at_event, update_volunteer_availability_at_event
from app.backend.registration_data.volunteer_registration_data import \
    get_dict_of_registration_data_for_volunteers_at_event
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.frontend.form_handler import button_error_and_back_to_initial_state_form
from app.frontend.shared.events_state import get_event_from_state
from app.frontend.shared.volunteer_state import (
    get_volunteer_from_state,
)

from app.objects.abstract_objects.abstract_buttons import Button, CANCEL_BUTTON_LABEL
from app.objects.abstract_objects.abstract_form import Form, NewForm
from app.objects.abstract_objects.abstract_lines import (
    ListOfLines,
    _______________,
    Line,
)
from app.objects.day_selectors import no_days_selected
from app.objects.events import Event


def display_form_confirm_volunteer_details_from_rota(interface: abstractInterface):
    event = get_event_from_state(interface)
    volunteer = get_volunteer_from_state(interface=interface)
    past_roles = get_text_of_last_roles(
        interface=interface, volunteer=volunteer
    )
    available_checkbox = Line(
        [
            get_availability_checkbox_for_volunteer_at_event(
                interface=interface, event=event, volunteer=volunteer
            )
        ]
    )

    return Form(
        ListOfLines(
            [
                "Following are details for volunteer %s at event %s"
                % (volunteer.name, str(event)),
                _______________,
                available_checkbox,
                past_roles,
                _______________,
                save_button,
                delete_button,
                cancel_button,
            ]
        )
    )


def get_text_of_last_roles(
    interface: abstractInterface, volunteer: Volunteer
) -> Line:
    all_roles_as_dict = (
        get_all_roles_across_recent_events_for_volunteer_as_dict_latest_first(
            object_store=interface.object_store, volunteer=volunteer
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
    registration_data = get_dict_of_registration_data_for_volunteers_at_event(object_store=interface.object_store,
                                                                              event=event)
    data_for_volunteer = registration_data.get(volunteer)
    availability = data_for_volunteer.availablity
    return get_availability_checkbox(
        availability=availability,
        event=event,
        input_name=AVAILABILITY,
        input_label="Confirm availability for volunteer:",
    )


def post_form_confirm_volunteer_details_from_rota(interface: abstractInterface):
    last_button = interface.last_button_pressed()
    if cancel_button.pressed(last_button):
        return go_back_to_parent_form(interface)
    elif delete_button.pressed(last_button):
        delete_volunteer_from_event(interface)
        interface.flush_cache_to_store()
        return go_back_to_parent_form(interface)

    elif save_button.pressed(last_button):
        form_ok = update_volunteer_at_event_from_rota_with_form_contents_and_return_true_if_ok(
            interface
        )
        if not form_ok:
            return display_form_confirm_volunteer_details_from_rota(interface)
        else:
            interface.flush_cache_to_store()
            return go_back_to_parent_form(interface)
    else:
        raise button_error_and_back_to_initial_state_form(interface)



def go_back_to_parent_form(interface: abstractInterface) -> NewForm:
    return interface.get_new_display_form_for_parent_of_function(
        display_form_confirm_volunteer_details_from_rota
    )


def delete_volunteer_from_event(interface: abstractInterface):
    volunteer = get_volunteer_from_state(interface)
    event = get_event_from_state(interface)
    delete_volunteer_at_event(
        object_store = interface.object_store, event=event, volunteer=volunteer
    )


def update_volunteer_at_event_from_rota_with_form_contents_and_return_true_if_ok(
    interface: abstractInterface,
) -> bool:
    volunteer = get_volunteer_from_state(interface)
    event = get_event_from_state(interface)
    availability = get_availablity_from_form(
        interface=interface, event=event, input_name=AVAILABILITY
    )

    if no_days_selected(availability, possible_days=event.weekdays_in_event()):
        interface.log_error(
            "No days selected for volunteer at event - delete if not using at event"
        )
        return False

    update_volunteer_availability_at_event(
        object_store = interface.object_store,
        event=event,
        volunteer=volunteer,
        availability=availability,
    )

    return True


AVAILABILITY = "Availability"
DELETE_VOLUNTEER_FROM_EVENT_BUTTON_LABEL = "Remove volunteer from event"
SAVE_CHANGES_BUTTON_LABEL = "Save changes"

save_button = Button(SAVE_CHANGES_BUTTON_LABEL)
delete_button = Button(DELETE_VOLUNTEER_FROM_EVENT_BUTTON_LABEL)
cancel_button = Button(CANCEL_BUTTON_LABEL)
