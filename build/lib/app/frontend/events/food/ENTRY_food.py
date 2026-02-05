from app.backend.food.summarise_food import summarise_food_data_by_day
from app.frontend.events.food.parse_food_data import (
    save_food_data_in_form,
    download_food_data,
)
from app.frontend.events.food.render_food import *

from app.frontend.form_handler import button_error_and_back_to_initial_state_form
from app.frontend.events.patrol_boats.parse_patrol_boat_table import *

from app.objects.abstract_objects.abstract_form import (
    Form,
    NewForm,
    File,
)
from app.objects.abstract_objects.abstract_buttons import (
    cancel_menu_button,
    save_menu_button,
)
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_lines import (
    ListOfLines,
    _______________,
    DetailListOfLines,
)
from app.frontend.shared.events_state import get_event_from_state

from app.objects.abstract_objects.abstract_text import Heading


def display_form_view_for_food_requirements(interface: abstractInterface) -> Form:
    event = get_event_from_state(interface)
    title = Heading("Food requirements for event %s" % str(event), centred=True, size=4)

    button_bar = get_button_bar_for_food_required()

    summary_by_day = summarise_food_data_by_day(
        object_store=interface.object_store, event=event
    )
    summaries = DetailListOfLines(ListOfLines([summary_by_day]), name="Summary")

    cadet_food_table = DetailListOfLines(
        ListOfLines([get_table_of_cadets_with_food(interface)]),
        name="Cadet food requirements",
    )
    volunteer_food_table = DetailListOfLines(
        ListOfLines([get_table_of_volunteers_with_food(interface)]),
        name="Volunteer food requirements",
    )

    return Form(
        ListOfLines(
            [
                button_bar,
                title,
                _______________,
                summaries,
                _______________,
                cadet_food_table,
                _______________,
                volunteer_food_table,
                _______________,
            ]
        )
    )


def post_form_view_for_food_requirements(
    interface: abstractInterface,
) -> Union[Form, NewForm, File]:
    last_button_pressed = interface.last_button_pressed()

    if cancel_menu_button.pressed(last_button_pressed):
        return previous_form(interface)


    
    if save_menu_button.pressed(last_button_pressed):
        save_food_data_in_form(interface)
        interface.clear()

    elif download_food_button.pressed(last_button_pressed):
        return download_food_data(interface)

    else:
        return button_error_and_back_to_initial_state_form(interface)

    return interface.get_new_form_given_function(display_form_view_for_food_requirements)


def previous_form(interface: abstractInterface):
    return interface.get_new_display_form_for_parent_of_function(
        display_form_view_for_food_requirements
    )
