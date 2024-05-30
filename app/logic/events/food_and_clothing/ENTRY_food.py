from app.logic.events.food_and_clothing.parse_food_data import save_food_data_in_form
from app.logic.events.food_and_clothing.render_food import get_button_bar_for_food_required, \
    get_table_of_cadets_with_food, get_table_of_volunteers_with_food, get_other_food_table

from app.logic.abstract_logic_api import button_error_and_back_to_initial_state_form
from app.logic.events.patrol_boats.parse_patrol_boat_table import *

from app.objects.abstract_objects.abstract_form import (
    Form,
    NewForm, )
from app.objects.abstract_objects.abstract_buttons import CANCEL_BUTTON_LABEL, SAVE_BUTTON_LABEL
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_lines import ListOfLines, _______________
from app.logic.events.events_in_state import get_event_from_state

from app.objects.abstract_objects.abstract_text import Heading


### OPTION TO EDIT CADET FOOD REQUIRED
### OPTION TO EDIT VOLUNTEER FOOD REQUIRED
### OPTION TO APPLY # OF DAYS SERVICE TO VOLUNTEERS
###
### REPORT: FOOD BY DAY, FILTERED FOR ACTUALLY THERE

## Questions: how do we combine with wristbands and gala dinners (seperate event - manual)



def display_form_view_for_food_requirements(interface: abstractInterface) -> Form:

    event =get_event_from_state(interface)
    title = Heading("Food requirements for event %s" % str(event), centred=True, size=4)

    button_bar = get_button_bar_for_food_required()
    cadet_food_table = get_table_of_cadets_with_food(interface)
    volunteer_food_table = get_table_of_volunteers_with_food(interface)
    other_food_table = get_other_food_table(interface)

    return Form(
        ListOfLines(
            [
                button_bar,
                title,
                _______________,
                "Cadets:",
                cadet_food_table,
                _______________,
                "Volunteers:",
                volunteer_food_table,
                _______________,
                "Other:",
                other_food_table
            ]
        )
    )


def post_form_view_for_food_requirements(
    interface: abstractInterface
) -> Union[Form, NewForm]:

    last_button_pressed = interface.last_button_pressed()

    if last_button_pressed==CANCEL_BUTTON_LABEL:
        return previous_form(interface)

    ### save
    save_food_data_in_form(interface)

    if last_button_pressed==SAVE_BUTTON_LABEL:
        pass

    else:
        return button_error_and_back_to_initial_state_form(interface)

    interface.save_stored_items()
    interface.clear_stored_items()

    return display_form_view_for_food_requirements(interface)

def previous_form(interface: abstractInterface):
    return interface.get_new_display_form_for_parent_of_function(display_form_view_for_food_requirements)

