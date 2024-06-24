import os
from typing import Union

from app.backend.reporting.all_event_data.all_event_data import create_csv_event_report_and_return_filename
from app.backend.ticks_and_qualifications.ticksheets import get_expected_qualifications_for_cadets_at_event
from app.objects.abstract_objects.abstract_text import Heading

from app.objects.events import Event

from app.logic.events.events_in_state import     get_event_from_list_of_events_given_event_description

from app.backend.events import confirm_event_exists_given_description

from app.logic.events.ENTRY_view_events import display_list_of_events_with_buttons

from app.data_access.file_access import download_directory

from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_form import (
    Form,
    File, NewForm, )
from app.objects.abstract_objects.abstract_lines import ListOfLines
from app.objects.abstract_objects.abstract_buttons import CANCEL_BUTTON_LABEL, Button, ButtonBar, main_menu_button, \
    cancel_menu_button


def display_form_for_all_event_data_report(interface: abstractInterface):

    event_buttons = display_list_of_events_with_buttons(interface)
    title = Heading("Select to dump giant spreadsheet of all event data", centred=True, size=4)
    contents_of_form = ListOfLines(
        [
            ButtonBar([main_menu_button, cancel_menu_button]),
            title,
            event_buttons
        ]
    )

    return Form(contents_of_form)


def post_form_for_for_all_event_data_report(
    interface: abstractInterface,
) -> Union[File, Form, NewForm]:
    last_button = interface.last_button_pressed()
    if cancel_menu_button.pressed(last_button):
        return previous_form(interface)
    else:
        return action_when_event_button_clicked(interface)

def action_when_event_button_clicked(interface: abstractInterface) -> File:
    event_description = interface.last_button_pressed()
    confirm_event_exists_given_description(interface=interface, event_description=event_description)

    event = get_event_from_list_of_events_given_event_description(interface=interface,
                                                                  event_description=event_description)

    filename = create_csv_event_report_and_return_filename(interface=interface, event=event)

    return File(filename)


def previous_form(interface: abstractInterface):
    return interface.get_new_display_form_for_parent_of_function(display_form_for_all_event_data_report)

