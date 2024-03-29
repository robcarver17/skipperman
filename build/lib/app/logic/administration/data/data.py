import shutil
from typing import Union

from app.data_access.backups.find_and_restore_backups import delete_all_master_data
from app.objects.abstract_objects.abstract_lines import Line, ListOfLines

from app.objects.abstract_objects.abstract_buttons import ButtonBar, main_menu_button, Button

from app.logic.administration.users.parse_user_form import delete_user_from_user_list, save_changes_in_security_form
from app.logic.administration.users.render_users_form import display_form_edit_list_of_users, list_of_deletion_buttons_names, BACK_BUTTON_LABEL
from app.objects.abstract_objects.abstract_form import Form, NewForm
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.backend.data.security import load_all_users

DELETE_ALL_DATA_BUTTON_LABEL = "Delete all data"

nav_buttons = ButtonBar([main_menu_button])
config_option_buttons = Line([Button(DELETE_ALL_DATA_BUTTON_LABEL, tile=True)])

def display_form_data(interface: abstractInterface) -> Union[Form, NewForm]:
    lines_inside_form = ListOfLines(
        [
            nav_buttons,
            config_option_buttons
        ]
    )

    return Form(lines_inside_form)


def post_form_data(interface: abstractInterface) -> Union[Form, NewForm]:
    last_button = interface.last_button_pressed()
    if last_button==BACK_BUTTON_LABEL:
        return interface.get_new_display_form_for_parent_of_function(post_form_data)

    if last_button ==DELETE_ALL_DATA_BUTTON_LABEL:
        delete_all_master_data()
        interface.log_error("Deleted all data except users/passwords")
        return interface.get_new_form_given_function(display_form_data)