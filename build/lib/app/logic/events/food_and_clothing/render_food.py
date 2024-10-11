from app.objects.events import Event

from app.OLD_backend.volunteers.volunteers import DEPRECATE_get_volunteer_from_id

from app.OLD_backend.cadets import DEPRECATE_get_cadet_from_id
from app.OLD_backend.data.food import FoodData
from app.frontend.forms.form_utils import get_food_requirements_input_as_tuple
from app.frontend.shared.events_state import get_event_from_state
from app.objects.abstract_objects.abstract_buttons import ButtonBar, Button, SAVE_BUTTON_LABEL, CANCEL_BUTTON_LABEL
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_tables import Table, RowInTable
from app.objects_OLD.food import CadetWithFoodRequirementsAtEvent, VolunteerWithFoodRequirementsAtEvent

GET_FOOD_FOR_CADETS = "Get food requirements for cadets from registration data"
GET_FOOD_FOR_VOLUNTEERS = "Get food requirements for volunteers from registration data"
DOWNLOAD_FOOD = "Download food requirements to spreadsheet"

def get_button_bar_for_food_required(event: Event) -> ButtonBar:
    save_button = Button(SAVE_BUTTON_LABEL, nav_button=True)
    back_button = Button(CANCEL_BUTTON_LABEL, nav_button=True)
    cadet_button = Button(GET_FOOD_FOR_CADETS, nav_button=True)
    volunteer_button = Button(GET_FOOD_FOR_VOLUNTEERS, nav_button=True)
    download_button = Button(DOWNLOAD_FOOD, nav_button=True)

    button_bar = ButtonBar([back_button, save_button, download_button])

    if event.contains_cadets:
        button_bar.append(cadet_button)

    if event.contains_volunteers:
        button_bar.append(volunteer_button)

    return button_bar


def get_table_of_cadets_with_food(interface: abstractInterface) -> Table:
    food_data = FoodData(interface.data)
    event = get_event_from_state(interface)

    cadets_with_food_at_event = food_data.list_of_active_cadets_with_food_at_event(event=event)

    rows_in_table = [
        get_row_in_table_of_cadets_with_food(interface=interface, cadet_with_food_required=cadet_with_food_required)
        for cadet_with_food_required in cadets_with_food_at_event
    ]

    return Table(rows_in_table)


def get_row_in_table_of_cadets_with_food(interface: abstractInterface, cadet_with_food_required:  CadetWithFoodRequirementsAtEvent) -> RowInTable:
    cadet = DEPRECATE_get_cadet_from_id(interface=interface, cadet_id=cadet_with_food_required.cadet_id)
    checkbox, other_input =     get_food_requirements_input_as_tuple(existing_food_requirements=
                                                                     cadet_with_food_required.food_requirements,
                                                                     other_input_name=get_input_name_other_food_for_cadet(cadet_id=cadet.id),
                                                                     checkbox_input_name=get_input_name_food_checkbox_for_cadet(cadet_id=cadet.id),
                                                                     other_input_label="Other")

    return RowInTable([
        cadet.name,
        checkbox,
        other_input
    ])


def get_input_name_other_food_for_cadet(cadet_id: str) -> str:
    return "OtherFoodCadet_%s" % cadet_id


def get_input_name_food_checkbox_for_cadet(cadet_id: str) -> str:
    return "CheckBoxFoodCadet_%s" % cadet_id


def get_table_of_volunteers_with_food(interface: abstractInterface) -> Table:
    food_data = FoodData(interface.data)
    event = get_event_from_state(interface)
    volunteers_with_food_at_event = food_data.list_of_active_volunteers_with_food_at_event(event=event)

    rows_in_table = [
        get_row_in_table_of_volunteers_with_food(interface=interface, volunteer_with_food_required=volunteer_with_food_required)
        for volunteer_with_food_required in volunteers_with_food_at_event
    ]

    return Table(rows_in_table)


def get_row_in_table_of_volunteers_with_food(interface: abstractInterface,
                                         volunteer_with_food_required: VolunteerWithFoodRequirementsAtEvent) -> RowInTable:
    volunteer = DEPRECATE_get_volunteer_from_id(interface=interface, volunteer_id=volunteer_with_food_required.volunteer_id)
    checkbox, other_input = get_food_requirements_input_as_tuple(existing_food_requirements=
                                                                 volunteer_with_food_required.food_requirements,
                                                                 other_input_name=get_input_name_other_food_for_volunteer(
                                                                     volunteer_id=volunteer.id),
                                                                 checkbox_input_name=get_input_name_food_checkbox_for_volunteer(
                                                                     volunteer_id=volunteer.id),
                                                                 other_input_label="Other")

    return RowInTable([
        volunteer.name,
        checkbox,
        other_input
    ])

def get_input_name_other_food_for_volunteer(volunteer_id: str):
    return "OtherFoodVolunteer_%s" % volunteer_id


def get_input_name_food_checkbox_for_volunteer(volunteer_id: str):
    return "CheckBoxFoodVolunteer_%s" % volunteer_id

## FIX ME OPTION TO ADD GUESTS (NAMED PERSON WITH FOOD REQUIREMENTS - IN THE FOOD ONLY EVENTS THIS IS THE ONLY TYPE OF PERSON THERE WOULD BE)

##
def get_other_food_table(interface: abstractInterface) -> Table:
    return ''

