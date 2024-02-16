from app.backend.form_utils import get_availablity_from_form, get_availability_checkbox
from app.backend.volunteers.volunteer_allocation import    update_volunteer_availability_at_event
from app.backend.volunteers.volunteers import get_volunteer_from_id
from app.backend.data.volunteer_allocation import delete_volunteer_with_id_at_event, get_volunteer_at_event
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.logic.abstract_logic_api import button_error_and_back_to_initial_state_form
from app.logic.events.constants import SAVE_CHANGES
from app.logic.events.events_in_state import get_event_from_state
from app.logic.events.volunteer_allocation.add_volunteer_to_event_form_contents import AVAILABILITY
from app.logic.volunteers.volunteer_state import get_volunteer_id_selected_from_state
from app.objects.abstract_objects.abstract_buttons import Button, BACK_BUTTON_LABEL
from app.objects.abstract_objects.abstract_form import Form, NewForm
from app.objects.abstract_objects.abstract_lines import ListOfLines, _______________
from app.objects.day_selectors import no_days_selected
from app.objects.events import Event
from app.objects.volunteers_at_event import VolunteerAtEvent

DELETE_VOLUNTEER_FROM_EVENT_BUTTON_LABEL = "Remove volunteer from event"

def display_form_confirm_volunteer_details_from_rota(interface: abstractInterface):
    volunteer_id = get_volunteer_id_selected_from_state(interface) ## NEEDS TO BE SET
    event =get_event_from_state(interface)
    volunteer_at_event = get_volunteer_at_event(volunteer_id=volunteer_id, event=event)
    volunteer = get_volunteer_from_id(volunteer_id)

    available_checkbox = get_availability_checkbox_for_volunteer_at_event(volunteer_at_event=volunteer_at_event, event=event)

    return Form(ListOfLines([
        "Following are details for volunteer %s at event %s" % (volunteer.name, str(event)),
        _______________,
        available_checkbox,
        _______________,
        Button(SAVE_CHANGES),
        Button(DELETE_VOLUNTEER_FROM_EVENT_BUTTON_LABEL),
        Button(BACK_BUTTON_LABEL)
    ]))


def get_availability_checkbox_for_volunteer_at_event(volunteer_at_event: VolunteerAtEvent, event: Event):
    availability = volunteer_at_event.availablity
    return get_availability_checkbox(availability=availability,
                                     event=event,
                                     input_name=AVAILABILITY,
                                     input_label="Confirm availability for volunteer:")



def post_form_confirm_volunteer_details_from_rota(interface: abstractInterface):
    last_button = interface.last_button_pressed()
    if last_button==BACK_BUTTON_LABEL:
        return go_back_to_parent_form(interface)
    elif last_button==DELETE_VOLUNTEER_FROM_EVENT_BUTTON_LABEL:
        delete_volunteer_from_event(interface)
        return go_back_to_parent_form(interface)
    elif last_button==SAVE_CHANGES:
        form_ok = update_volunteer_at_event_from_rota_with_form_contents_and_return_true_if_ok(interface)
        if not form_ok:
            return display_form_confirm_volunteer_details_from_rota(interface)
        return go_back_to_parent_form(interface)
    else:
        raise button_error_and_back_to_initial_state_form(interface)

def go_back_to_parent_form(interface:abstractInterface)-> NewForm:
    return interface.get_new_display_form_for_parent_of_function(display_form_confirm_volunteer_details_from_rota)

def delete_volunteer_from_event(interface: abstractInterface):
    volunteer_id = get_volunteer_id_selected_from_state(interface)
    event =get_event_from_state(interface)
    delete_volunteer_with_id_at_event(volunteer_id=volunteer_id, event=event)


def update_volunteer_at_event_from_rota_with_form_contents_and_return_true_if_ok(interface: abstractInterface) -> bool:

    volunteer_id = get_volunteer_id_selected_from_state(interface)
    event =get_event_from_state(interface)
    availability = get_availablity_from_form(interface=interface, event=event, input_name=AVAILABILITY)

    if no_days_selected(availability, possible_days=event.weekdays_in_event()):
        interface.log_error("No days selected for volunteer at event")
        return False

    update_volunteer_availability_at_event(volunteer_id=volunteer_id, availability=availability, event=event)

    return True


