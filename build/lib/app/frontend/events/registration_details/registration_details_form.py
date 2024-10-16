from dataclasses import dataclass

from app.objects.abstract_objects.abstract_interface import abstractInterface

from app.OLD_backend.cadets import (
    get_cadet_from_id, load_list_of_all_cadets,
)
from app.frontend.forms.form_utils import (
    get_availability_checkbox,
    input_name_from_column_name_and_cadet_id,
)
from app.frontend.forms.form_utils import dropdown_input_for_status_change
from app.OLD_backend.data.cadets_at_event_id_level import CadetsAtEventIdLevelData

from app.frontend.events.constants import ROW_STATUS
from app.objects.abstract_objects.abstract_form import (
    dropDownInput,
    checkboxInput,
    textInput,
    intInput,
)
from app.objects.abstract_objects.abstract_tables import RowInTable
from app.objects.cadets import ListOfCadets
from app.objects.day_selectors import DaySelector
from app.objects.events import Event
from app.objects.cadet_with_id_at_event import (
    CadetWithIdAtEvent,
    ListOfCadetsWithIDAtEvent,
)
from app.data_access.configuration.field_list_groups import (
    FIELDS_WITH_INTEGERS,
    FIELDS_VIEW_ONLY_IN_EDIT_VIEW,
    FIELDS_TO_EDIT_IN_EDIT_VIEW,
)
from app.objects.exceptions import arg_not_passed
from app.objects.registration_data import (
    RowInRegistrationData,
    RegistrationStatus,
    get_states_allowed_give_current_status,
)

DAYS_ATTENDING = "days_attending_field"
NOTES = "Notes"
HEALTH = "Health"


@dataclass
class RegistrationDetailsForEvent:
    event: Event
    list_of_cadets: ListOfCadets
    all_columns_excluding_special_fields: list
    cadets_at_event: ListOfCadetsWithIDAtEvent

    def columns_to_parse_including_special_fields(self):
        ## order not important
        return [ROW_STATUS, DAYS_ATTENDING]


def get_registration_data(
    interface: abstractInterface, event: Event, sort_order: str = arg_not_passed
) -> RegistrationDetailsForEvent:
    cadets_at_event = get_sorted_list_of_cadets_at_event(
        interface=interface, event=event, sort_order=sort_order
    )
    all_columns = get_list_of_columns_excluding_special_fields(cadets_at_event)
    list_of_cadets = load_list_of_all_cadets(interface.data)

    return RegistrationDetailsForEvent(
        cadets_at_event=cadets_at_event,
        list_of_cadets=list_of_cadets,
        event=event,
        all_columns_excluding_special_fields=all_columns,
    )


def get_sorted_list_of_cadets_at_event(
    interface: abstractInterface, event: Event, sort_order: str
):
    cadets_at_event_data = CadetsAtEventIdLevelData(interface.data)
    return cadets_at_event_data.get_sorted_list_of_cadets_at_event(
        event=event, sort_by=sort_order
    )


def get_list_of_columns_excluding_special_fields(
    cadets_at_event: ListOfCadetsWithIDAtEvent,
) -> list:
    first_cadet = cadets_at_event[0]
    top_row = first_cadet.data_in_row  ## should all be the same
    all_columns = get_columns_to_edit(top_row) + get_columns_to_view(top_row)

    return all_columns


def get_top_row_for_table_of_registration_details(all_columns: list) -> RowInTable:
    return RowInTable(["Cadet", "Status", "Attending", "Health", "Notes"] + all_columns)


def row_for_cadet_in_event(
        interface: abstractInterface,
    cadet_at_event: CadetWithIdAtEvent,
    registration_details: RegistrationDetailsForEvent,
) -> RowInTable:
    cadet_id = cadet_at_event.cadet_id
    cadet = get_cadet_from_id(
        data_layer=interface.data,
        cadet_id=cadet_id
    )

    status_button = get_status_button(cadet_at_event.status, cadet_id=cadet_id)
    days_attending_field = get_days_attending_field(
        cadet_at_event.availability, cadet_id=cadet_id, event=registration_details.event
    )
    health_field = get_health_field(cadet_at_event.health, cadet_id=cadet_id)
    notes_field = get_notes_field(cadet_at_event.notes, cadet_id=cadet_id)

    other_columns = get_list_of_column_forms_excluding_reserved_fields(
        cadet_at_event=cadet_at_event, registration_details=registration_details
    )

    return RowInTable(
        [str(cadet), status_button, days_attending_field, health_field, notes_field]
        + other_columns
    )


def get_list_of_column_forms_excluding_reserved_fields(
    cadet_at_event: CadetWithIdAtEvent,
    registration_details: RegistrationDetailsForEvent,
) -> list:
    column_form_entries = [
        form_item_for_key_value_pair_in_row_data(
            column_name=column_name, cadet_at_event=cadet_at_event
        )
        for column_name in registration_details.all_columns_excluding_special_fields
    ]

    return column_form_entries


def get_columns_to_edit(data_in_row: RowInRegistrationData) -> list:
    all_columns = list(data_in_row.keys())
    columns_to_edit = [
        column_name
        for column_name in FIELDS_TO_EDIT_IN_EDIT_VIEW
        if column_name in all_columns
    ]  ## preserve order

    return columns_to_edit


def get_columns_to_view(data_in_row: RowInRegistrationData) -> list:
    all_columns = list(data_in_row.keys())

    columns_to_view = [
        column_name
        for column_name in FIELDS_VIEW_ONLY_IN_EDIT_VIEW
        if column_name in all_columns
    ]  ## preserve order

    return columns_to_view


def get_status_button(
    current_status: RegistrationStatus, cadet_id: str
) -> dropDownInput:
    allowable_status = get_states_allowed_give_current_status(current_status)

    return dropdown_input_for_status_change(
        input_label="",
        input_name=input_name_from_column_name_and_cadet_id(ROW_STATUS, cadet_id),
        default_status=current_status,
        allowable_status=allowable_status,
    )


def get_days_attending_field(
    attendance: DaySelector, cadet_id: str, event: Event
) -> checkboxInput:
    return get_availability_checkbox(
        availability=attendance,
        event=event,
        input_name=input_name_from_column_name_and_cadet_id(
            DAYS_ATTENDING, cadet_id=cadet_id
        ),
        line_break=True,
    )


def get_notes_field(notes: str, cadet_id: str) -> textInput:
    return textInput(
        input_name=input_name_from_column_name_and_cadet_id(
            column_name=NOTES, cadet_id=cadet_id
        ),
        input_label="",
        value=notes,
    )


def get_health_field(notes: str, cadet_id: str) -> textInput:
    return textInput(
        input_name=input_name_from_column_name_and_cadet_id(
            column_name=HEALTH, cadet_id=cadet_id
        ),
        input_label="",
        value=notes,
    )


def form_item_for_key_value_pair_in_row_data(
    column_name: str, cadet_at_event: CadetWithIdAtEvent
):
    current_value = cadet_at_event.data_in_row[column_name]
    cadet_id = cadet_at_event.cadet_id
    if _column_can_be_edited(column_name):
        return form_item_for_key_value_pair_in_row_data_if_editable(
            column_name=column_name, current_value=current_value, cadet_id=cadet_id
        )
    else:
        return form_item_for_key_value_pair_in_row_data_if_view_only(
            current_value=current_value
        )


def form_item_for_key_value_pair_in_row_data_if_view_only(current_value) -> str:
    return str(current_value)


def form_item_for_key_value_pair_in_row_data_if_editable(
    column_name: str, current_value, cadet_id: str
):
    if column_name in FIELDS_WITH_INTEGERS:
        return form_value_for_integer_input(
            current_value=current_value, column_name=column_name, cadet_id=cadet_id
        )
    else:
        return form_value_for_text_input(
            current_value=current_value, column_name=column_name, cadet_id=cadet_id
        )


def form_value_for_text_input(column_name: str, current_value, cadet_id: str):
    return textInput(
        input_label="",
        input_name=input_name_from_column_name_and_cadet_id(
            column_name=column_name, cadet_id=cadet_id
        ),
        value=str(current_value),
    )


def form_value_for_integer_input(column_name: str, current_value, cadet_id: str):
    return intInput(
        input_label="",
        input_name=input_name_from_column_name_and_cadet_id(
            column_name=column_name, cadet_id=cadet_id
        ),
        value=int(current_value),
    )


def _column_can_be_edited(column_name: str) -> bool:
    return column_name in FIELDS_TO_EDIT_IN_EDIT_VIEW
