from app.objects.volunteers import Volunteer

from app.objects.cadets import Cadet

from app.backend.food.active_cadets_and_volunteers_with_food import \
    get_dict_of_active_cadets_with_food_requirements_at_event, \
    get_dict_of_active_volunteers_with_food_requirements_at_event
from app.frontend.forms.form_utils import get_food_requirements_input_as_tuple
from app.frontend.shared.events_state import get_event_from_state
from app.objects.abstract_objects.abstract_buttons import (
    ButtonBar,
    Button,
    save_menu_button,
    cancel_menu_button,
)
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_tables import Table, RowInTable
from app.objects.food import  FoodRequirements


DOWNLOAD_FOOD = "Download food requirements to spreadsheet"
download_food_button = Button(DOWNLOAD_FOOD, nav_button=True)

def get_button_bar_for_food_required() -> ButtonBar:
    button_bar = ButtonBar([cancel_menu_button, save_menu_button, download_food_button])

    return button_bar


def get_table_of_cadets_with_food(interface: abstractInterface) -> Table:
    event = get_event_from_state(interface)

    cadets_with_food_at_event = get_dict_of_active_cadets_with_food_requirements_at_event(object_store=interface.object_store,
                                                                                          event=event)

    rows_in_table = [
        get_row_in_table_of_cadets_with_food(
             cadet=cadet, food_requirements=food_requirements
        )
        for cadet, food_requirements in cadets_with_food_at_event.items()
    ]

    return Table(rows_in_table)


def get_row_in_table_of_cadets_with_food(
        cadet: Cadet,
    food_requirements: FoodRequirements
) -> RowInTable:

    checkbox, other_input = get_food_requirements_input_as_tuple(
        existing_food_requirements=food_requirements,
        other_input_name=get_input_name_other_food_for_cadet(cadet_id=cadet.id),
        checkbox_input_name=get_input_name_food_checkbox_for_cadet(cadet_id=cadet.id),
        other_input_label="Other",
    )

    return RowInTable([cadet.name, checkbox, other_input])


def get_input_name_other_food_for_cadet(cadet_id: str) -> str:
    return "OtherFoodCadet_%s" % cadet_id


def get_input_name_food_checkbox_for_cadet(cadet_id: str) -> str:
    return "CheckBoxFoodCadet_%s" % cadet_id


def get_table_of_volunteers_with_food(interface: abstractInterface) -> Table:
    event = get_event_from_state(interface)
    volunteers_with_food_at_event = get_dict_of_active_volunteers_with_food_requirements_at_event(object_store=interface.object_store,
                                                                                                  event=event)

    rows_in_table = [
        get_row_in_table_of_volunteers_with_food(
            volunteer=volunteer,
            food_requirements=food_requirements
        )
        for volunteer, food_requirements in volunteers_with_food_at_event.items()
    ]

    return Table(rows_in_table)


def get_row_in_table_of_volunteers_with_food(
    volunteer: Volunteer,
        food_requirements: FoodRequirements
) -> RowInTable:

    checkbox, other_input = get_food_requirements_input_as_tuple(
        existing_food_requirements=food_requirements,
        other_input_name=get_input_name_other_food_for_volunteer(
            volunteer_id=volunteer.id
        ),
        checkbox_input_name=get_input_name_food_checkbox_for_volunteer(
            volunteer_id=volunteer.id
        ),
        other_input_label="Other",
    )

    return RowInTable([volunteer.name, checkbox, other_input])


def get_input_name_other_food_for_volunteer(volunteer_id: str):
    return "OtherFoodVolunteer_%s" % volunteer_id


def get_input_name_food_checkbox_for_volunteer(volunteer_id: str):
    return "CheckBoxFoodVolunteer_%s" % volunteer_id
