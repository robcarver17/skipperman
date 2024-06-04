import os
from typing import Union

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
from app.objects.abstract_objects.abstract_buttons import CANCEL_BUTTON_LABEL, Button, ButtonBar, main_menu_button


def display_form_for_data_dump_report(interface: abstractInterface):


    title = Heading("Under construction", centred=True, size=4)
    contents_of_form = ListOfLines(
        [
            ButtonBar([main_menu_button, cancel_button]),
            title,
        ]
    )

    return Form(contents_of_form)

cancel_button = Button(CANCEL_BUTTON_LABEL, nav_button=True)


def post_form_for_data_dump_report(
    interface: abstractInterface,
) -> Union[File, Form, NewForm]:
    last_button = interface.last_button_pressed()
    if last_button == CANCEL_BUTTON_LABEL:
        return previous_form(interface)

def previous_form(interface: abstractInterface) -> NewForm:
    return interface.get_new_display_form_for_parent_of_function(display_form_for_data_dump_report)
