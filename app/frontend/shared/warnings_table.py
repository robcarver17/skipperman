from typing import Union

from app.frontend.shared.events_state import get_event_from_state
from app.objects.abstract_objects.abstract_buttons import Button
from app.objects.abstract_objects.abstract_form import checkboxInput
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_tables import Table, RowInTable
from app.objects.abstract_objects.abstract_lines import DetailListOfLines, ListOfLines
from app.objects.event_warnings import ListOfEventWarnings, EventWarningLog
from app.backend.events.event_warnings import get_list_of_active_warning_ids_at_event, mark_event_warning_with_id_as_ignore
from app.objects.events import Event

WARNING_FIELD_ID = "**warnings"



def display_warnings_tables(list_of_warnings: ListOfEventWarnings) -> ListOfLines:
    active_table = display_active_warnings_table(list_of_warnings.active_only(), detail_name="Active warnings")
    ignored_table = display_active_warnings_table(list_of_warnings.ignored_only(), detail_name="Ignored warnings")

    return ListOfLines([
        active_table,
        ignored_table
    ])

def display_active_warnings_table(list_of_warnings: ListOfEventWarnings, detail_name: str) -> Union[
    ListOfLines, DetailListOfLines]:

    if len(list_of_warnings) == 0:
        return ListOfLines([""])

    if len(list_of_warnings)==0:
        return ListOfLines([""])

    table = get_inside_table(list_of_warnings)
    return DetailListOfLines(
        ListOfLines(
            [
             table,
                save_warnings_button
            ]
        ),            name=detail_name)

def get_inside_table(list_of_warnings: ListOfEventWarnings):
    current_warning = None
    list_of_rows = [top_row()]
    for warning in list_of_warnings:
        if current_warning is None:
            list_of_rows.append(RowInTable([warning.priority, '', '']))
            list_of_rows.append(RowInTable(['', warning.category, '', '']))
        else:
            if warning.priority!=current_warning.priority:
                list_of_rows.append(RowInTable([warning.priority, '', '']))
            if warning.category!=current_warning.category:
                list_of_rows.append(RowInTable(['', warning.category, '', '']))

        current_warning = warning
        list_of_rows.append(row_for_warning(warning))

    table = Table(list_of_rows, has_column_headings=True)

    return table

def top_row():
    return ['Priority', 'Category', 'Message', 'Tick if dealt with or can be ignored']

def row_for_warning(warning: EventWarningLog) -> RowInTable:
    return RowInTable([
        '', '', warning.warning,
        checkbox_for_warning(warning)
    ])

def checkbox_for_warning(warning: EventWarningLog):
    return checkboxInput(
        dict_of_labels={IGNORE:IGNORE},
        dict_of_checked={IGNORE: warning.ignored},
        input_name=get_field_for_warning(warning.id),
        input_label=''
    )

IGNORE ='Ignore'

def get_field_for_warning(warning_id:str):
    return "%s_%s" % (WARNING_FIELD_ID,warning_id)


save_warnings_button = Button("Save changes to warnings")

def save_warnings_from_table(interface: abstractInterface):
    event =get_event_from_state(interface)
    list_of_ids = get_list_of_active_warning_ids_at_event(object_store=interface.object_store, event=event)
    for warning_id in list_of_ids:
        process_warning_with_id_from_table(interface=interface, event=event, warning_id=warning_id)

def process_warning_with_id_from_table(interface: abstractInterface, event: Event, warning_id:str):
    field_name = get_field_for_warning(warning_id)
    try:
        checkboxvalue_list =interface.value_of_multiple_options_from_form(field_name)
    except:
        # not all warnings are visible
        return

    if IGNORE in checkboxvalue_list:
        mark_event_warning_with_id_as_ignore(
            object_store=interface.object_store,
            event=event,
            warning_id=warning_id
        )