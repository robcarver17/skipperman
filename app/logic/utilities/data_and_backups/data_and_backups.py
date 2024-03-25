from typing import Union

from app.logic.abstract_logic_api import button_error_and_back_to_initial_state_form
from app.logic.utilities.data_and_backups.make_backup import make_backup_and_return_file
from app.logic.utilities.data_and_backups.restore_backup_from_local import display_form_for_upload_backup
from app.logic.utilities.data_and_backups.restore_backup_from_snapshot import display_form_view_of_snapshots
from app.objects.abstract_objects.abstract_form import Form, NewForm, File
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_lines import ListOfLines
from app.objects.abstract_objects.abstract_buttons import BACK_BUTTON_LABEL, Button

BACKUP_FILES = "Backup all data to local machine"
UPLOAD_DATA = "Upload data from copy on local machine (CAREFUL: WILL OVERWRITE ALL DATA!)"
RESTORE_DATA = "Restore data from previous snapshot (useful for undoing mistakes - CAREFUL WILL OVERWRITE ANY WORK DONE SINCE!)"

def display_form_data_and_backups(interface: abstractInterface) -> Form:
    lines_inside_form = ListOfLines([
        Button(BACK_BUTTON_LABEL),
        "Selection option:",
        Button(BACKUP_FILES),
        Button(RESTORE_DATA),
        Button(UPLOAD_DATA)
    ])

    return Form(lines_inside_form)


def post_form_data_and_backups(interface: abstractInterface) -> Union[NewForm, File]:
    button_pressed = interface.last_button_pressed()
    if button_pressed == BACK_BUTTON_LABEL:
        return interface.get_new_display_form_for_parent_of_function(display_form_data_and_backups)
    elif button_pressed == BACKUP_FILES:
        return make_backup_and_return_file()
    elif button_pressed == RESTORE_DATA:
        return interface.get_new_form_given_function(display_form_view_of_snapshots)
    elif button_pressed == UPLOAD_DATA:
        return interface.get_new_form_given_function(display_form_for_upload_backup)
    else:
        return button_error_and_back_to_initial_state_form(interface)

