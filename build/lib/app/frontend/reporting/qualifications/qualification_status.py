import os
from typing import Union

from app.backend.qualifications_and_ticks.progress import (
    get_expected_qualifications_for_cadets_at_event,
)
from app.objects.abstract_objects.abstract_text import Heading

from app.objects.events import Event

from app.backend.events.list_of_events import (
    get_event_from_list_of_events_given_event_description,
)

from app.frontend.events.ENTRY_view_events import display_list_of_events_with_buttons

from app.data_access.init_directories import download_directory

from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_form import (
    Form,
    File,
    NewForm,
)
from app.objects.abstract_objects.abstract_lines import ListOfLines
from app.objects.abstract_objects.abstract_buttons import (
    CANCEL_BUTTON_LABEL,
    Button,
    ButtonBar,
    main_menu_button,
)


def display_form_for_qualification_status_report(interface: abstractInterface):
    ## LIST OF EVENTS AS TILES, THEN FROM THAT DOWNLOAD EXPECTED QUALIFICATIONS FOR EVENT
    event_buttons = display_list_of_events_with_buttons(interface)
    title = Heading(
        "Select event to see qualification status of registered cadets",
        centred=True,
        size=4,
    )
    contents_of_form = ListOfLines(
        [ButtonBar([main_menu_button, cancel_button]), title, event_buttons]
    )

    return Form(contents_of_form)


cancel_button = Button(CANCEL_BUTTON_LABEL, nav_button=True)


def post_form_for_qualification_status_report(
    interface: abstractInterface,
) -> Union[File, Form, NewForm]:
    last_button = interface.last_button_pressed()
    if cancel_button.pressed(last_button):
        return previous_form(interface)
    else:
        return action_when_event_button_clicked(interface)


def action_when_event_button_clicked(interface: abstractInterface) -> File:
    event_description = interface.last_button_pressed()

    event = get_event_from_list_of_events_given_event_description(
        object_store=interface.object_store, event_description=event_description
    )

    return download_expected_qualification_for_event(interface=interface, event=event)


def download_expected_qualification_for_event(
    interface: abstractInterface, event: Event
) -> File:
    filename = write_expected_qualifications_to_temp_csv_file_and_return_filename(
        interface=interface, event=event
    )
    return File(filename)


def previous_form(interface: abstractInterface):
    return interface.get_new_display_form_for_parent_of_function(
        post_form_for_qualification_status_report
    )


def write_expected_qualifications_to_temp_csv_file_and_return_filename(
    interface: abstractInterface, event: Event
) -> str:
    df_of_qualifications = get_expected_qualifications_for_cadets_at_event(
        object_store=interface.object_store, event=event
    )
    filename = temp_file_name()
    df_of_qualifications.to_csv(filename, index=False)

    return filename


def temp_file_name() -> str:
    return os.path.join(download_directory, "temp_file.csv")
