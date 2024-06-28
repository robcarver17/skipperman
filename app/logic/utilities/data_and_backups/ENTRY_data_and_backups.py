from typing import Union

from app.logic.abstract_logic_api import button_error_and_back_to_initial_state_form
from app.logic.utilities.data_and_backups.make_backup import make_backup_and_return_file
from app.logic.utilities.data_and_backups.restore_backup_from_local import (
    display_form_for_upload_backup,
)
from app.logic.utilities.data_and_backups.restore_backup_from_snapshot import (
    display_form_view_of_snapshots,
)
from app.objects.abstract_objects.abstract_form import Form, NewForm, File
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_lines import ListOfLines, Line
from app.objects.abstract_objects.abstract_buttons import (
    BACK_BUTTON_LABEL,
    Button,
    ButtonBar,
    main_menu_button,
    back_menu_button,
)
from app.data_access.backups.make_backup import make_backup

BACKUP_FILES = "Backup all data to local machine"
UPLOAD_DATA = "Upload data from local machine"
RESTORE_DATA = "Restore data from hourly snapshot"
MAKE_SNAPSHOT = "Write a snapshot of data now"

list_of_menu_buttons = Line(
    [
        Button(label, tile=True)
        for label in [BACKUP_FILES, UPLOAD_DATA, RESTORE_DATA, MAKE_SNAPSHOT]
    ]
)

nav_buttons = ButtonBar([back_menu_button, main_menu_button])


def display_form_data_and_backups(interface: abstractInterface) -> Form:
    lines_inside_form = ListOfLines([nav_buttons, list_of_menu_buttons])

    return Form(lines_inside_form)


def post_form_data_and_backups(
    interface: abstractInterface,
) -> Union[NewForm, Form, File]:
    button_pressed = interface.last_button_pressed()
    if back_menu_button.pressed(button_pressed):
        return interface.get_new_display_form_for_parent_of_function(
            display_form_data_and_backups
        )
    elif button_pressed == BACKUP_FILES:
        return make_backup_and_return_file(interface)
    elif button_pressed == RESTORE_DATA:
        return interface.get_new_form_given_function(display_form_view_of_snapshots)
    elif button_pressed == UPLOAD_DATA:
        return interface.get_new_form_given_function(display_form_for_upload_backup)
    elif button_pressed == MAKE_SNAPSHOT:
        make_backup_given_data(interface)
        return display_form_data_and_backups(interface)
    else:
        return button_error_and_back_to_initial_state_form(interface)


def make_backup_given_data(interface: abstractInterface):
    make_backup(
        backup_data_path=interface.data.data.backup_data_path,
        master_data_path=interface.data.data.master_data_path,
    )
    interface.log_error("Data snapshotted for future retrieval")
