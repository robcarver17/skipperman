from typing import Union, List

from app.backend.mapping.check_field_mapping import (
    get_field_mapping_or_empty_list_from_raw_event_file,
    get_list_of_unused_skipperman_fields_at_event,
    get_list_of_unused_WA_fields_at_event_given_uploaded_file,
)
from app.backend.mapping.list_of_field_mappings import get_field_mapping_for_event
from app.data_access.configuration.field_list_groups import (
    ALL_FIELDS_EXPECTED_IN_WA_FILE_MAPPING,
)
from app.frontend.shared.events_state import get_event_from_state
from app.objects.abstract_objects.abstract_buttons import Button
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_tables import Table, RowInTable
from app.objects.abstract_objects.abstract_form import dropDownInput, textInput
from app.objects.events import Event
from app.objects.wa_field_mapping import WAFieldMap


def get_mapping_table(interface: abstractInterface, event: Event) -> Table:
    top_row = top_row_in_mapping_table()
    adding_row = add_fields_row_in_mapping_table(interface=interface, event=event)
    rows_in_mapping = body_of_mapping_table(interface=interface, event=event)

    return Table([top_row] + [adding_row] + rows_in_mapping, has_column_headings=True)


def top_row_in_mapping_table() -> RowInTable:
    return RowInTable(["Skipperman", "Wild Apricot", ""])


def body_of_mapping_table(
    interface: abstractInterface, event: Event
) -> List[RowInTable]:
    mapping = get_field_mapping_for_event(
        object_store=interface.object_store, event=event
    )

    rows_in_mapping = [
        row_in_mapping_table(event=event, wa_field_map=wa_field_map)
        for wa_field_map in mapping
    ]

    return rows_in_mapping


def row_in_mapping_table(event: Event, wa_field_map: WAFieldMap) -> RowInTable:
    delete_button = delete_button_for_row_in_mapping_table(wa_field_map)
    return RowInTable(
        [
            entry_for_skipperman_field_in_mapping_table(wa_field_map.skipperman_field),
            entry_for_WA_field_in_mapping_table(
                event=event, wa_field=wa_field_map.wa_field
            ),
            delete_button,
        ]
    )


def entry_for_skipperman_field_in_mapping_table(skipperman_field: str):
    flag = "(Bad field name)" if bad_skipperman_field(skipperman_field) else ""
    return "%s %s" % (skipperman_field, flag)


def bad_skipperman_field(skipperman_field: str):
    return not skipperman_field in ALL_FIELDS_EXPECTED_IN_WA_FILE_MAPPING


def entry_for_WA_field_in_mapping_table(event: Event, wa_field: str):
    flag = (
        "(Missing from uploaded file)"
        if WA_Field_is_missing_from_uploaded_file(event=event, wa_field=wa_field)
        else ""
    )
    return "%s %s" % (wa_field, flag)


def WA_Field_is_missing_from_uploaded_file(event: Event, wa_field: str):
    WA_mappings = get_field_mapping_or_empty_list_from_raw_event_file(event)

    if len(WA_mappings) == 0:
        return False

    return not wa_field in WA_mappings


def add_fields_row_in_mapping_table(
    interface: abstractInterface, event: Event
) -> RowInTable:
    dropdown_skipperman = dropdown_of_unused_skipperman_fields(
        interface=interface, event=event
    )
    add_skipperman_or_input_WA = (
        input_field_dropdown_of_unused_WA_fields_or_add_skipperman_button(
            interface=interface, event=event
        )
    )
    add_or_blank = blank_or_add_mapping_button(interface)

    return RowInTable([dropdown_skipperman, add_skipperman_or_input_WA, add_or_blank])


def dropdown_of_unused_skipperman_fields(interface: abstractInterface, event: Event):
    dict_of_options = _get_dict_for_dropdown_of_unused_skipperman_fields(
        interface=interface, event=event
    )

    current_field = get_current_skipperman_field_to_add_from_state(interface)
    if current_field is no_field_to_add:
        current_field = ADD_SKIPPERMAN_FIELD_DROPDOWN_EMPTY

    return dropDownInput(
        input_name=ADD_SKIPPERMAN_FIELD_DROPDOWN_NAME,
        input_label="Select skipperman field:",
        dict_of_options=dict_of_options,
        default_label=current_field,
    )


def _get_dict_for_dropdown_of_unused_skipperman_fields(
    interface: abstractInterface, event: Event
) -> dict:
    list_of_unused_skipperman_fields_at_event = (
        get_list_of_unused_skipperman_fields_at_event(
            object_store=interface.object_store, event=event
        )
    )
    list_of_unused_skipperman_fields_at_event.sort()
    list_of_unused_skipperman_fields_at_event.append(
        ADD_SKIPPERMAN_FIELD_DROPDOWN_EMPTY
    )

    dict_of_options = dict(
        [(field, field) for field in list_of_unused_skipperman_fields_at_event]
    )

    return dict_of_options


def input_field_dropdown_of_unused_WA_fields_or_add_skipperman_button(
    interface: abstractInterface, event: Event
) -> Union[Button, dropDownInput, textInput]:
    current_field = get_current_skipperman_field_to_add_from_state(interface)
    no_skipperman_field_selected = current_field is no_field_to_add
    WA_file_uploaded = uploaded_WA_file_exists(event=event)

    if no_skipperman_field_selected:
        return add_skipperman_field_button
    elif WA_file_uploaded:
        return dropdown_of_unused_WA_fields(interface=interface, event=event)
    else:
        return input_for_WA_fields()


def uploaded_WA_file_exists(event: Event):
    WA_mappings = get_field_mapping_or_empty_list_from_raw_event_file(event)
    return len(WA_mappings) > 0


def dropdown_of_unused_WA_fields(
    interface: abstractInterface, event: Event
) -> dropDownInput:
    dict_of_options = _get_dict_for_dropdown_of_unused_WA_fields(
        interface=interface, event=event
    )

    return dropDownInput(
        input_name=ADD_WA_FIELD_DROPDOWN_NAME,
        input_label="Select WA field:",
        dict_of_options=dict_of_options,
        default_label=ADD_WA_FIELD_DROPDOWN_EMPTY,
    )


def _get_dict_for_dropdown_of_unused_WA_fields(
    interface: abstractInterface, event: Event
) -> dict:
    list_of_unused_WA_fields_at_event = (
        get_list_of_unused_WA_fields_at_event_given_uploaded_file(
            event=event, object_store=interface.object_store
        )
    )
    list_of_unused_WA_fields_at_event.sort()
    list_of_unused_WA_fields_at_event.append(ADD_WA_FIELD_DROPDOWN_EMPTY)

    dict_of_options = dict(
        [(field, field) for field in list_of_unused_WA_fields_at_event]
    )

    return dict_of_options


def input_for_WA_fields() -> textInput:
    return textInput(
        input_name=ADD_WA_FIELD_INPUT_FIELD_NAME,
        input_label="Type WA field *exactly* as it appears on form (or upload an exported file to choose a field)",
    )


def blank_or_add_mapping_button(interface: abstractInterface) -> Union[Button, str]:
    current_field = get_current_skipperman_field_to_add_from_state(interface)
    if current_field is no_field_to_add:
        return ""
    else:
        return add_WA_field_button


## Buttons
add_skipperman_field_button = Button(
    label="Add selected skipperman field to mapping", value="add_skipperman_field"
)

add_WA_field_button = Button(
    label="Add selected skipperman & WA field to mapping", value="add_wa_field"
)


def delete_button_for_row_in_mapping_table(wa_field_map: WAFieldMap):
    return Button(
        label="Delete", value=delete_button_value_for_row_in_mapping_table(wa_field_map)
    )


def list_of_delete_button_values_in_mapping_table(interface: abstractInterface):
    event = get_event_from_state(interface)
    mapping = get_field_mapping_for_event(
        object_store=interface.object_store, event=event
    )

    list_of_buttons = [
        delete_button_value_for_row_in_mapping_table(wa_field_map)
        for wa_field_map in mapping
    ]

    return list_of_buttons


delete_marker = "DELETE*"


def delete_button_value_for_row_in_mapping_table(wa_field_map: WAFieldMap):
    return delete_marker + wa_field_map.skipperman_field


def get_skipperman_field_from_delete_button(delete_button: str):
    return delete_button[len(delete_marker) :]


ADD_SKIPPERMAN_FIELD_DROPDOWN_NAME = "**ADD_skipperman_field_dropdown"
ADD_SKIPPERMAN_FIELD_DROPDOWN_EMPTY = "Choose Skipperman field to add to mapping"

ADD_WA_FIELD_DROPDOWN_NAME = "**ADD_WA_field_dropdown"
ADD_WA_FIELD_DROPDOWN_EMPTY = "Choose WA field to add to mapping"
ADD_WA_FIELD_INPUT_FIELD_NAME = "**ADD_WA_Field_freetext"

## store skipperman field to be added in state

no_field_to_add = "((a***NOFIELDTOADD"
SKIPPERMANFIELD_TO_ADD_STATE = "skipperman_field_to_add_in_form"


def get_current_skipperman_field_to_add_from_state(interface: abstractInterface):
    return interface.get_persistent_value(SKIPPERMANFIELD_TO_ADD_STATE, no_field_to_add)


def save_current_skipperman_field_to_add_from_state(
    interface: abstractInterface, skipperman_field: str
):
    interface.set_persistent_value(SKIPPERMANFIELD_TO_ADD_STATE, skipperman_field)


def clear_current_skipperman_field_to_add_from_state(interface: abstractInterface):
    interface.clear_persistent_value(SKIPPERMANFIELD_TO_ADD_STATE)
