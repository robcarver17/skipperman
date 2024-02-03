from app.backend.form_utils import get_availablity_from_form, get_food_requirements_from_form
from app.backend.volunteers.volunteer_allocation import get_volunteer_at_event, get_volunteer_from_id, delete_volunteer_with_id_at_event
from app.logic.abstract_interface import abstractInterface
from app.logic.events.constants import SAVE_CHANGES, EDIT_VOLUNTEER_ROTA_EVENT_STAGE
from app.logic.events.events_in_state import get_event_from_state
from app.logic.events.volunteer_allocation.confirm_volunteer_details import \
    update_volunteer_at_event_with_new_food_and_availability
from app.logic.events.volunteer_allocation.volunteer_details_form_contents import \
    get_food_requirements_input_for_volunteer_at_event, get_availability_checkbox_for_volunteer_at_event, AVAILABILITY, \
    FOOD_REQUIREMENTS, OTHER_FOOD
from app.logic.volunteers.volunteer_state import get_volunteer_id_selected_from_state
from app.objects.abstract_objects.abstract_buttons import Button, BACK_BUTTON_LABEL
from app.objects.abstract_objects.abstract_form import Form, NewForm
from app.objects.abstract_objects.abstract_lines import ListOfLines, _______________
from app.objects.day_selectors import no_days_selected

DELETE_VOLUNTEER_FROM_EVENT_BUTTON_LABEL = "Remove volunteer from event"

def display_form_confirm_volunteer_details_from_rota(interface: abstractInterface):
    volunteer_id = get_volunteer_id_selected_from_state(interface) ## NEEDS TO BE SET
    event =get_event_from_state(interface)
    volunteer_at_event = get_volunteer_at_event(volunteer_id=volunteer_id, event=event)
    volunteer = get_volunteer_from_id(volunteer_id)

    food_requirements_input = get_food_requirements_input_for_volunteer_at_event(volunteer_at_event)
    available_checkbox = get_availability_checkbox_for_volunteer_at_event(volunteer_at_event=volunteer_at_event, event=event)

    return Form(ListOfLines([
        "Following are details for volunteer %s at event %s" % (volunteer.name, str(event)),
        _______________,
        food_requirements_input,
        _______________,
        available_checkbox,
        _______________,
        Button(SAVE_CHANGES),
        Button(DELETE_VOLUNTEER_FROM_EVENT_BUTTON_LABEL),
        Button(BACK_BUTTON_LABEL)
    ]))


def post_form_confirm_volunteer_details_from_rota(interface: abstractInterface):
    last_button = interface.last_button_pressed()
    if last_button==BACK_BUTTON_LABEL:
        pass
    elif last_button==DELETE_VOLUNTEER_FROM_EVENT_BUTTON_LABEL:
        delete_volunteer_from_event(interface)
    elif last_button==SAVE_CHANGES:
        form_ok = update_volunteer_at_event_from_rota_with_form_contents_and_return_true_if_ok(interface)
        if not form_ok:
            return display_form_confirm_volunteer_details_from_rota(interface)
    else:
        raise Exception("Button %s not known" % last_button)

    return NewForm(EDIT_VOLUNTEER_ROTA_EVENT_STAGE)

def delete_volunteer_from_event(interface: abstractInterface):
    volunteer_id = get_volunteer_id_selected_from_state(interface)
    event =get_event_from_state(interface)
    delete_volunteer_with_id_at_event(volunteer_id=volunteer_id, event=event)


def update_volunteer_at_event_from_rota_with_form_contents_and_return_true_if_ok(interface: abstractInterface) -> bool:

    volunteer_id = get_volunteer_id_selected_from_state(interface)
    event =get_event_from_state(interface)
    availability = get_availablity_from_form(interface=interface, event=event, input_name=AVAILABILITY)
    food_requirement = get_food_requirements_from_form(interface=interface, checkbox_input_name =FOOD_REQUIREMENTS, other_input_name =OTHER_FOOD)

    if no_days_selected(availability, possible_days=event.weekdays_in_event()):
        interface.log_error("No days selected for volunteer at event")
        return False

    update_volunteer_at_event_with_new_food_and_availability(event=event,
                                                             volunteer_id=volunteer_id,
                                                             availability=availability,
                                                             food_requirements=food_requirement)

    return True
