from typing import Union

from app.backend.reporting.all_event_data.all_event_data import (
    create_csv_event_report_and_return_filename,
)
from app.frontend.form_handler import button_error_and_back_to_initial_state_form
from app.frontend.shared.buttons import is_button_event_selection, event_from_button_pressed

from app.objects.abstract_objects.abstract_text import Heading
from app.objects.events import SORT_BY_START_DSC

from app.frontend.shared.event_selection import display_list_of_events_with_buttons

from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_form import (
    Form,
    File,
    NewForm,
)
from app.objects.abstract_objects.abstract_lines import ListOfLines
from app.objects.abstract_objects.abstract_buttons import (
    ButtonBar,
    main_menu_button,
    back_menu_button, HelpButton,
)


def display_form_for_all_event_data_report(interface: abstractInterface):
    event_buttons = display_list_of_events_with_buttons(interface, sort_by=SORT_BY_START_DSC)
    title = Heading(
        "Select to dump giant spreadsheet of all event data", centred=True, size=4
    )
    contents_of_form = ListOfLines(
        [ButtonBar([main_menu_button, back_menu_button]), title, event_buttons]
    )

    return Form(contents_of_form)


def post_form_for_for_all_event_data_report(
    interface: abstractInterface,
) -> Union[File, Form, NewForm]:
    last_button = interface.last_button_pressed()
    if back_menu_button.pressed(last_button):
        return previous_form(interface)
    elif is_button_event_selection(last_button):
        return action_when_event_button_clicked(interface)
    else:
        return button_error_and_back_to_initial_state_form(interface)



def action_when_event_button_clicked(interface: abstractInterface) -> File:
    event = event_from_button_pressed(value_of_button_pressed=interface.last_button_pressed(), object_store=interface.object_store)

    filename = create_csv_event_report_and_return_filename(
        object_store=interface.object_store, event=event
    )

    return File(filename)


def previous_form(interface: abstractInterface):
    return interface.get_new_display_form_for_parent_of_function(
        display_form_for_all_event_data_report
    )
