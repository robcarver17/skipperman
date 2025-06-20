from typing import Union

from app.frontend.shared.events_state import get_event_from_state
from app.objects.abstract_objects.abstract_buttons import Button
from app.objects.abstract_objects.abstract_form import checkboxInput
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_tables import Table, RowInTable
from app.objects.abstract_objects.abstract_lines import DetailListOfLines, ListOfLines
from app.objects.event_warnings import ListOfEventWarnings, EventWarningLog
from app.backend.events.event_warnings import (
    get_list_of_all_warning_ids_at_event,
    mark_event_warning_with_id_as_ignore,
    mark_all_active_event_warnings_with_priority_and_category_as_ignored,
    mark_all_ignored_event_warnings_with_priority_and_category_as_unignored,
    mark_event_warning_with_id_as_unignore,
)
from app.objects.events import Event
from app.frontend.shared.buttons import (
    get_button_value_given_type_and_attributes,
    is_button_of_type,
    get_attributes_from_button_pressed_of_known_type,
)
from app.objects.utilities.exceptions import MISSING_FROM_FORM
from app.objects.utilities.generic_objects import from_bool_to_str, from_str_to_bool

WARNING_FIELD_ID = "**warnings"


def display_warnings_tables(list_of_warnings: ListOfEventWarnings) -> ListOfLines:
    active_table = display_active_warnings_table(
        list_of_warnings.active_only(), detail_name="Active warnings", active=True
    )
    ignored_table = display_active_warnings_table(
        list_of_warnings.ignored_only(), detail_name="Ignored warnings", active=False
    )

    return ListOfLines([active_table, ignored_table])


def display_active_warnings_table(
    list_of_warnings: ListOfEventWarnings, detail_name: str, active: bool
) -> Union[ListOfLines, DetailListOfLines]:

    if len(list_of_warnings) == 0:
        return ListOfLines([""])

    if len(list_of_warnings) == 0:
        return ListOfLines([""])

    table = get_inside_table(list_of_warnings, active=active)
    return DetailListOfLines(
        ListOfLines([table, save_warnings_button]), name=detail_name
    )


def get_inside_table(list_of_warnings: ListOfEventWarnings, active: bool):
    current_warning = None
    list_of_rows = [top_row()]
    ignore_on = active

    for warning in list_of_warnings:
        if current_warning is None:
            list_of_rows.append(RowInTable([warning.priority, "", ""]))
            list_of_rows.append(
                RowInTable(
                    [
                        "",
                        warning.category,
                        get_button_for_multiple_warning(
                            priority=warning.priority,
                            category=warning.category,
                            ignore_on=ignore_on,
                        ),
                        "",
                    ]
                )
            )
        else:
            if warning.priority != current_warning.priority:
                list_of_rows.append(RowInTable([warning.priority, "", ""]))
                current_warning.category = ""  ## force reset
            if warning.category != current_warning.category:
                list_of_rows.append(
                    RowInTable(
                        [
                            "",
                            warning.category,
                            get_button_for_multiple_warning(
                                priority=warning.priority,
                                category=warning.category,
                                ignore_on=ignore_on,
                            ),
                            "",
                        ]
                    )
                )

        current_warning = warning
        list_of_rows.append(row_for_warning(warning))

    table = Table(list_of_rows, has_column_headings=True)

    return table


def top_row():
    return ["Priority", "Category", "Message", "Tick if dealt with or can be ignored"]


def row_for_warning(warning: EventWarningLog) -> RowInTable:
    return RowInTable(["", "", warning.warning, checkbox_for_warning(warning)])


def checkbox_for_warning(warning: EventWarningLog):
    return checkboxInput(
        dict_of_labels={IGNORE: IGNORE},
        dict_of_checked={IGNORE: warning.ignored},
        input_name=get_field_for_warning(warning.id),
        input_label="",
    )


IGNORE = "Ignore"


def get_field_for_warning(warning_id: str):
    return "%s_%s" % (WARNING_FIELD_ID, warning_id)


def get_button_for_multiple_warning(priority: str, category: str, ignore_on: bool):
    if ignore_on:
        label = "Set all active warnings of priority '%s', category '%s' to ignored" % (
            priority,
            category,
        )
    else:
        label = (
            "Set all currently ignored warnings of priority '%s', category '%s' to un-ignored"
            % (priority, category)
        )

    return Button(
        label=label,
        value=get_button_value_for_multiple_warning(
            priority=priority, category=category, ignore_on=ignore_on
        ),
    )


def get_button_value_for_multiple_warning(
    priority: str, category: str, ignore_on: bool
):
    return get_button_value_given_type_and_attributes(
        WARNINGS_BUTTON_TYPE, priority, category, from_bool_to_str(ignore_on)
    )


def get_attributes_from_button_pressed(last_button: str):
    priority, category, ignore_on = get_attributes_from_button_pressed_of_known_type(
        last_button, type_to_check=WARNINGS_BUTTON_TYPE, collapse_singleton=False
    )
    ignore_on = from_str_to_bool(ignore_on)

    return priority, category, ignore_on


PSEUDO_PRIORITY_FOR_SAVE_ALL_WARNINGS = "save_allwarnings"
WARNINGS_BUTTON_TYPE = "warnings_in_event-button_type"


def is_warning_button(last_button: str):
    return is_button_of_type(
        value_of_button_pressed=last_button, type_to_check=WARNINGS_BUTTON_TYPE
    )


def was_specific_button_to_flag_warnings_pressed(last_button: str):
    if not is_warning_button(last_button):
        return False

    priority, category, ignore_on = get_attributes_from_button_pressed(last_button)

    was_save_all_button = priority == PSEUDO_PRIORITY_FOR_SAVE_ALL_WARNINGS

    return not was_save_all_button


save_warnings_button = Button(
    "Save changes to warnings",
    value=get_button_value_for_multiple_warning(
        priority=PSEUDO_PRIORITY_FOR_SAVE_ALL_WARNINGS, category="", ignore_on=False
    ),
)


def is_save_warnings_button_pressed(last_button: str):
    return is_button_of_type(last_button, type_to_check=WARNINGS_BUTTON_TYPE)


def save_warnings_from_table(interface: abstractInterface):
    event = get_event_from_state(interface)
    save_warnings_from_table_checkboxes(interface, event)

    last_button = interface.last_button_pressed()
    if was_specific_button_to_flag_warnings_pressed(last_button):
        save_multiple_warnings_given_specific_button_pressed(
            interface=interface, last_button=last_button
        )


def save_warnings_from_table_checkboxes(interface: abstractInterface, event: Event):
    list_of_ids = get_list_of_all_warning_ids_at_event(
        object_store=interface.object_store, event=event
    )
    for warning_id in list_of_ids:
        process_warning_with_id_from_table(
            interface=interface, event=event, warning_id=warning_id
        )


def process_warning_with_id_from_table(
    interface: abstractInterface, event: Event, warning_id: str
):
    field_name = get_field_for_warning(warning_id)
    checkboxvalue_list = interface.value_of_multiple_options_from_form(
        field_name, default=MISSING_FROM_FORM
    )
    if checkboxvalue_list is MISSING_FROM_FORM:
        # not all warnings are visible, might be on wrong page
        print("%s not visible" % field_name)
        return
    if IGNORE in checkboxvalue_list:
        mark_event_warning_with_id_as_ignore(
            object_store=interface.object_store, event=event, warning_id=warning_id
        )
    else:
        mark_event_warning_with_id_as_unignore(
            object_store=interface.object_store, event=event, warning_id=warning_id
        )


def save_multiple_warnings_given_specific_button_pressed(
    interface: abstractInterface, last_button: str
):
    priority, category, ignore_on = get_attributes_from_button_pressed(last_button)
    event = get_event_from_state(interface)
    if ignore_on:
        mark_all_active_event_warnings_with_priority_and_category_as_ignored(
            object_store=interface.object_store,
            event=event,
            priority=priority,
            category=category,
        )
    else:
        mark_all_ignored_event_warnings_with_priority_and_category_as_unignored(
            object_store=interface.object_store,
            event=event,
            priority=priority,
            category=category,
        )
