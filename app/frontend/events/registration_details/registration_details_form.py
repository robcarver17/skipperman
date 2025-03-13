from dataclasses import dataclass
from typing import List

from app.objects.composed.cadets_at_event_with_registration_data import (
    DictOfCadetsWithRegistrationData,
    CadetRegistrationData,
)

from app.objects.abstract_objects.abstract_interface import abstractInterface

from app.frontend.forms.form_utils import (
    get_availability_checkbox,
    input_name_from_column_name_and_cadet_id,
)
from app.frontend.forms.form_utils import dropdown_input_for_status_change

from app.frontend.events.constants import ROW_STATUS
from app.objects.abstract_objects.abstract_form import (
    dropDownInput,
    checkboxInput,
    textInput,
    intInput,
)
from app.objects.abstract_objects.abstract_tables import RowInTable
from app.objects.cadets import Cadet
from app.objects.day_selectors import DaySelector
from app.objects.events import Event
from app.data_access.configuration.field_list_groups import (
    FIELDS_WITH_INTEGERS,
    FIELDS_VIEW_ONLY_IN_EDIT_VIEW,
    FIELDS_TO_EDIT_IN_EDIT_VIEW,
)
from app.objects.exceptions import arg_not_passed
from app.objects.registration_status import (
    RegistrationStatus,
    get_states_allowed_give_current_status,
)

DAYS_ATTENDING = "days_attending_field"
NOTES = "Notes"
HEALTH = "Health"


@dataclass
class RegistrationDetailsForEvent:
    event: Event
    all_columns_excluding_special_fields: list
    registration_data: DictOfCadetsWithRegistrationData


from app.backend.registration_data.cadet_registration_data import (
    get_dict_of_cadets_with_registration_data,
)


def get_registration_data(
    interface: abstractInterface, event: Event, sort_order: str = arg_not_passed
) -> RegistrationDetailsForEvent:
    dict_of_registration_data = get_dict_of_cadets_with_registration_data(
        object_store=interface.object_store, event=event
    )
    dict_of_registration_data = dict_of_registration_data.sort_by(sort_order)

    all_columns = dict_of_registration_data.list_of_registration_fields()

    return RegistrationDetailsForEvent(
        registration_data=dict_of_registration_data,
        event=event,
        all_columns_excluding_special_fields=all_columns,
    )


def get_list_of_columns_excluding_special_fields(
    registration_data: DictOfCadetsWithRegistrationData,
) -> list:
    field_names = registration_data.list_of_registration_fields()
    all_columns = get_columns_to_edit(field_names) + get_columns_to_view(field_names)

    return all_columns


def get_top_row_for_table_of_registration_details(all_columns: list) -> RowInTable:
    return RowInTable(["Cadet", "Status", "Attending", "Health", "Notes"] + all_columns)


def row_for_cadet_in_event(
    cadet: Cadet, registration_details: RegistrationDetailsForEvent
) -> RowInTable:

    registration_details_for_cadet = registration_details.registration_data[cadet]
    status_button = get_status_button(
        registration_details_for_cadet.status, cadet_id=cadet.id
    )
    days_attending_field = get_days_attending_field(
        registration_details_for_cadet.availability,
        cadet_id=cadet.id,
        event=registration_details_for_cadet.event,
    )
    health_field = get_health_field(
        registration_details_for_cadet.health, cadet_id=cadet.id
    )
    notes_field = get_notes_field(
        registration_details_for_cadet.notes, cadet_id=cadet.id
    )

    other_columns = get_list_of_column_forms_excluding_reserved_fields(
        cadet=cadet, registration_details=registration_details
    )

    return RowInTable(
        [str(cadet), status_button, days_attending_field, health_field, notes_field]
        + other_columns
    )


def get_list_of_column_forms_excluding_reserved_fields(
    cadet: Cadet,
    registration_details: RegistrationDetailsForEvent,
) -> list:
    registration_details_for_cadet = registration_details.registration_data[cadet]

    column_form_entries = [
        form_item_for_key_value_pair_in_row_data(
            column_name=column_name,
            cadet=cadet,
            registration_details_for_cadet=registration_details_for_cadet,
        )
        for column_name in registration_details.all_columns_excluding_special_fields
    ]

    return column_form_entries


def get_columns_to_edit(all_columns: List[str]) -> list:

    columns_to_edit = [
        column_name
        for column_name in FIELDS_TO_EDIT_IN_EDIT_VIEW
        if column_name in all_columns
    ]  ## preserve order

    return columns_to_edit


def get_columns_to_view(all_columns: List[str]) -> list:

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
    column_name: str,
    cadet: Cadet,
    registration_details_for_cadet: CadetRegistrationData,
):
    current_value = registration_details_for_cadet.data_in_row[column_name]
    cadet_id = cadet.id
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
