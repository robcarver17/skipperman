from typing import Union

from app.frontend.form_handler import button_error_and_back_to_initial_state_form
from app.frontend.utilities.data_and_backups.make_backup import (
    make_backup_and_return_file,
)
from app.frontend.utilities.data_and_backups.restore_backup_from_local import (
    display_form_for_upload_backup,
)
from app.frontend.utilities.data_and_backups.restore_backup_from_snapshot import (
    display_form_view_of_snapshots,
)
from app.objects.abstract_objects.abstract_form import Form, NewForm, File
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_lines import ListOfLines, Line
from app.objects.abstract_objects.abstract_buttons import (
    Button,
    ButtonBar,
    main_menu_button,
    back_menu_button,
    HelpButton,
)
from app.data_access.backups.make_backup import make_backup

BACKUP_FILES = "Backup all data to local machine"
UPLOAD_DATA = "Upload data from local machine"
RESTORE_DATA = "Restore data from data snapshot"
MAKE_SNAPSHOT = "Write a snapshot of data now"

backup_files_button = Button(BACKUP_FILES, tile=True)
upload_data_button = Button(UPLOAD_DATA, tile=True)
restore_data_button = Button(RESTORE_DATA, tile=True)
snapshot_data_button = Button(MAKE_SNAPSHOT, tile=True)
help_button = HelpButton("data_backup_help")


list_of_menu_buttons = Line(
    [backup_files_button, upload_data_button, restore_data_button, snapshot_data_button]
)

nav_buttons = ButtonBar([main_menu_button, back_menu_button, help_button])


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
    elif backup_files_button.pressed(button_pressed):
        return make_backup_and_return_file(interface)
    elif restore_data_button.pressed(button_pressed):
        return interface.get_new_form_given_function(display_form_view_of_snapshots)
    elif upload_data_button.pressed(button_pressed):
        return interface.get_new_form_given_function(display_form_for_upload_backup)
    elif snapshot_data_button.pressed(button_pressed):
        snapshot_data(interface)
        return display_form_data_and_backups(interface)
    else:
        return button_error_and_back_to_initial_state_form(interface)


def snapshot_data(interface: abstractInterface):
    interface.object_store.backup_underlying_data()

    interface.log_error("Data snapshotted for future retrieval")
