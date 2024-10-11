from typing import Union

from app.objects_OLD.relevant_information_for_volunteers import missing_relevant_information

from app.frontend.forms.form_utils import get_food_requirements_input, get_food_requirements_from_form
from app.objects_OLD.food import guess_food_requirements_from_food_field

from app.OLD_backend.volunteers.volunteer_allocation import    get_list_of_relevant_information
from app.OLD_backend.volunteers.volunteers import  DEPRECATE_get_volunteer_from_id
from app.frontend.shared.events_state import get_event_from_state
from app.frontend.events.volunteer_allocation.track_state_in_volunteer_allocation import \
    clear_volunteer_id_at_event_in_state, \
    get_and_save_next_volunteer_id_in_mapped_event_data, get_current_volunteer_id_at_event
from app.objects.abstract_objects.abstract_form import Form, NewForm
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_buttons import Button, SAVE_BUTTON_LABEL
from app.objects.abstract_objects.abstract_lines import ListOfLines
from app.objects.exceptions import NoMoreData
from app.objects.events import Event
from app.OLD_backend.food import add_new_volunteer_with_food_to_event, is_volunteer_with_id_already_at_event_with_food

def display_interactively_add_volunteer_food_to_event(interface: abstractInterface)  -> Union[Form, NewForm]:
    clear_volunteer_id_at_event_in_state(interface)

    return next_volunteer_with_food_in_event(interface)

def next_volunteer_with_food_in_event(interface: abstractInterface) -> Union[Form, NewForm]:

    try:
        get_and_save_next_volunteer_id_in_mapped_event_data(interface)
    except NoMoreData:
        clear_volunteer_id_at_event_in_state(interface)
        return return_to_controller(interface)

    return process_identified_volunteer_with_food_at_event(interface)




def process_identified_volunteer_with_food_at_event(interface: abstractInterface) -> Union[Form, NewForm]:
    volunteer_id = get_current_volunteer_id_at_event(interface)
    event =get_event_from_state(interface)
    already_added = is_volunteer_with_id_already_at_event_with_food(interface=interface, event=event, volunteer_id=volunteer_id)

    if already_added:
        return next_volunteer_with_food_in_event(interface)
    else:
        ## this volunteer is new at this event
        return display_form_for_volunteer_food_details(interface=interface, volunteer_id=volunteer_id, event=event)


OTHER_FOOD = "other"
CHECKBOX_FOOD = "food_check"

def display_form_for_volunteer_food_details(interface: abstractInterface, volunteer_id: str, event: Event)-> Form:

    volunteer = DEPRECATE_get_volunteer_from_id(interface=interface, volunteer_id=volunteer_id)

    list_of_food_preferences_as_single_str = get_volunteer_food_preferences_as_single_str(
        interface=interface,
        event=event,
        volunteer_id=volunteer_id
    )
    food_guess = guess_food_requirements_from_food_field(list_of_food_preferences_as_single_str)
    food_inputs = get_food_requirements_input(existing_food_requirements=food_guess,
                                              other_input_name=OTHER_FOOD,
                                              checkbox_input_name=CHECKBOX_FOOD,
                                              other_input_label="Other")


    button = Button(SAVE_BUTTON_LABEL)

    message = "Select food requirements for volunteer %s, in form was %s" % (volunteer.name, list_of_food_preferences_as_single_str)

    form = Form(
        ListOfLines(
            [
                message,

            ]+food_inputs+[button]
        ).add_Lines()
    )

    return form

def get_volunteer_food_preferences_as_single_str(interface: abstractInterface, event: Event, volunteer_id: str) -> str:
    list_of_relevant_information = get_list_of_relevant_information(volunteer_id=volunteer_id, event=event, interface=interface)
    list_of_relevant_information = [relevant_information for relevant_information in list_of_relevant_information if relevant_information is not missing_relevant_information]
    list_of_food_preferences = [relevant_information.details.food_preference for relevant_information in list_of_relevant_information]
    list_of_food_preferences = [food for food in list_of_food_preferences if len(food)>0]
    list_of_food_preferences_as_single_str = ", ".join(list_of_food_preferences)

    return list_of_food_preferences_as_single_str

def post_form_add_volunteer_food_to_event(interface: abstractInterface):
    food_requirements = get_food_requirements_from_form(interface=interface,
                                    other_input_name=OTHER_FOOD,
                                    checkbox_input_name=CHECKBOX_FOOD)

    volunteer_id = get_current_volunteer_id_at_event(interface)
    event = get_event_from_state(interface)

    add_new_volunteer_with_food_to_event(interface=interface, event=event, food_requirements=food_requirements, volunteer_id=volunteer_id)
    interface._save_data_store_cache()
    interface._clear_data_store_cache()


    return next_volunteer_with_food_in_event(interface)

def return_to_controller(interface: abstractInterface) -> NewForm:
    return interface.get_new_display_form_for_parent_of_function(display_interactively_add_volunteer_food_to_event)

