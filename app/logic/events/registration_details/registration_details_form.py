from dataclasses import dataclass

from app.backend.cadets import get_sorted_list_of_cadets, cadet_from_id_with_passed_list
from app.backend.data.mapped_events import load_master_event
from app.backend.form_utils import get_food_requirements_input_as_tuple, get_availability_checkbox
from app.logic.events.constants import ROW_STATUS
from app.backend.form_utils import dropdown_input_for_status_change
from app.objects.abstract_objects.abstract_form import dropDownInput, checkboxInput, textInput, intInput
from app.objects.abstract_objects.abstract_tables import RowInTable
from app.objects.cadets import ListOfCadets
from app.objects.day_selectors import DaySelector
from app.objects.events import Event
from app.objects.field_list import FIELDS_TO_EDIT_IN_EDIT_VIEW, FIELDS_VIEW_ONLY_IN_EDIT_VIEW, \
    FIELDS_WITH_INTEGERS
from app.objects.cadet_at_event import RowStatus
from app.objects.master_event import RowInMasterEvent, MasterEvent
from app.objects.constants import arg_not_passed
from app.objects.food import FoodRequirements

FOOD_REQUIRED_CHECKBOX_FORM_NAME="food_required_checkbox"
FOOD_REQUIRED_OTHER_FORM_NAME = "food_required_other"
DAYS_ATTENDING = "days_attending_field"

@dataclass
class RegistrationDetailsForEvent:
    event: Event
    list_of_cadets: ListOfCadets
    all_columns_excluding_special_fields: list
    master_event_details: MasterEvent

    def columns_to_parse_including_special_fields(self):
        ## order not important
        return [ROW_STATUS, DAYS_ATTENDING, FOOD_REQUIRED_CHECKBOX_FORM_NAME, FOOD_REQUIRED_OTHER_FORM_NAME]

def get_registration_data(event: Event, sort_order: str = arg_not_passed) -> RegistrationDetailsForEvent:
    master_event_details = load_master_event(event)
    list_of_cadets = get_sorted_list_of_cadets(sort_by=sort_order)
    master_event_details = master_event_details.sort_given_superset_of_cadet_ids(list_of_cadets.list_of_ids)
    all_columns = get_list_of_columns_excluding_special_fields(master_event_details)

    return RegistrationDetailsForEvent(
        master_event_details=master_event_details,
        list_of_cadets=list_of_cadets,
        event=event,
        all_columns_excluding_special_fields=all_columns
    )


def get_list_of_columns_excluding_special_fields(master_event_details) -> list:
    top_row = master_event_details[0]
    all_columns = get_columns_to_edit(top_row) + get_columns_to_view(top_row)

    return all_columns


def get_top_row_for_table_of_registration_details(all_columns: list)-> RowInTable:
    return RowInTable(["Cadet", "Status", "Attending", "Cadet Food Requirements", "Other Food Requirements"]+all_columns)


def row_for_cadet_in_event(row_in_event: RowInMasterEvent, registration_details: RegistrationDetailsForEvent) -> RowInTable:
    cadet_id =row_in_event.cadet_id
    cadet =  cadet_from_id_with_passed_list(cadet_id, list_of_cadets=registration_details.list_of_cadets)

    status_button = get_status_button(row_in_event.status, cadet_id=cadet_id)
    days_attending_field = get_days_attending_field(row_in_event.attendance, cadet_id=cadet_id, event=registration_details.event)
    checkbox_food_preference, other_input_food_preference = get_food_preference_fields(row_in_event.food_requirements, cadet_id=cadet_id)

    other_columns = get_list_of_column_forms_excluding_reserved_fields(row_in_event=row_in_event, registration_details=registration_details)

    return RowInTable([str(cadet), status_button, days_attending_field, checkbox_food_preference, other_input_food_preference]+other_columns)


def get_list_of_column_forms_excluding_reserved_fields(row_in_event: RowInMasterEvent, registration_details: RegistrationDetailsForEvent) -> list:

    column_form_entries = [
        form_item_for_key_value_pair_in_row_data(column_name=column_name,
                                                 registration_details=registration_details,
                                                 row_in_event=row_in_event) for column_name in registration_details.all_columns_excluding_special_fields
    ]

    return column_form_entries


def get_columns_to_edit(row_in_event: RowInMasterEvent) -> list:
    all_columns = list(row_in_event.data_in_row.keys())
    columns_to_edit =  [column_name for column_name in FIELDS_TO_EDIT_IN_EDIT_VIEW if column_name in all_columns] ## preserve order

    return columns_to_edit


def get_columns_to_view(row_in_event: RowInMasterEvent) -> list:
    all_columns = list(row_in_event.data_in_row.keys())

    columns_to_view = [column_name for column_name in FIELDS_VIEW_ONLY_IN_EDIT_VIEW if column_name in all_columns] ## preserve order

    return columns_to_view


def get_status_button(current_status: RowStatus, cadet_id: str)-> dropDownInput:
    return dropdown_input_for_status_change(input_label="",
                                            input_name=input_name_from_column_name_and_cadet_id(ROW_STATUS, cadet_id),
                                            default_status=current_status
                                            )

def get_days_attending_field(attendance: DaySelector, cadet_id: str, event: Event) -> checkboxInput:
    return get_availability_checkbox(availability=attendance,
                              event=event,
                              input_name = input_name_from_column_name_and_cadet_id(DAYS_ATTENDING, cadet_id=cadet_id),
                              line_break=True)

def get_food_preference_fields(food_requirements: FoodRequirements, cadet_id: str):
    checkbox_food_preference, other_input_food_preference = get_food_requirements_input_as_tuple(
        existing_food_requirements=food_requirements,
        checkbox_input_name=input_name_from_column_name_and_cadet_id(FOOD_REQUIRED_CHECKBOX_FORM_NAME,
                                                                     cadet_id=cadet_id),
        other_input_name=input_name_from_column_name_and_cadet_id(FOOD_REQUIRED_OTHER_FORM_NAME,cadet_id=cadet_id),
        line_break=True
    )
    return checkbox_food_preference, other_input_food_preference



def input_name_from_column_name_and_cadet_id(column_name: str, cadet_id: str) -> str:
    return "%s-%s" % (column_name, cadet_id)


def form_item_for_key_value_pair_in_row_data(column_name: str, row_in_event: RowInMasterEvent, registration_details: RegistrationDetailsForEvent):
    current_value = row_in_event.data_in_row[column_name]
    cadet_id = row_in_event.cadet_id
    if _column_can_be_edited(column_name):
        return form_item_for_key_value_pair_in_row_data_if_editable(column_name=column_name, current_value=current_value, cadet_id=cadet_id, registration_details=registration_details)
    else:
        return form_item_for_key_value_pair_in_row_data_if_view_only(current_value=current_value)


def form_item_for_key_value_pair_in_row_data_if_view_only( current_value) -> str:
    return str(current_value)


def form_item_for_key_value_pair_in_row_data_if_editable(column_name: str, current_value, cadet_id: str, registration_details: RegistrationDetailsForEvent):

    if column_name in FIELDS_WITH_INTEGERS:
        return form_value_for_integer_input(current_value=current_value, column_name=column_name, cadet_id=cadet_id)
    else:
        return form_value_for_text_input(current_value=current_value, column_name=column_name, cadet_id=cadet_id)




def form_value_for_text_input(column_name: str,current_value, cadet_id: str):
    return textInput(
    input_label="",
    input_name = input_name_from_column_name_and_cadet_id(column_name=column_name, cadet_id=cadet_id),
    value=str(current_value)

    )


def form_value_for_integer_input(column_name: str,current_value, cadet_id: str):
    return intInput(
    input_label="",
    input_name = input_name_from_column_name_and_cadet_id(column_name=column_name, cadet_id=cadet_id),
    value=int(current_value)

    )


def _column_can_be_edited(column_name:str) -> bool:
    return  (column_name in FIELDS_TO_EDIT_IN_EDIT_VIEW)
