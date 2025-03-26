from typing import Union

from app.frontend.utilities.files.delete_files import (
    delete_selected_files,
    delete_public_files,
    delete_private_temporary_files,
    delete_uploaded_temporary_files,
    delete_specific_file,
)
from app.frontend.utilities.files.qr_codes import generate_qr_code
from app.frontend.utilities.files.replace_files import (
    display_form_to_replace_selected_files,
)
from app.frontend.utilities.files.state import store_directory_and_filename
from app.frontend.utilities.files.upload_file import display_form_for_upload_public_file

from app.frontend.form_handler import button_error_and_back_to_initial_state_form
from app.frontend.utilities.files.render_files import *

from app.objects.abstract_objects.abstract_form import Form, NewForm, File
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_lines import ListOfLines, _______________
from app.objects.abstract_objects.abstract_text import Heading
from app.objects.abstract_objects.abstract_buttons import (
    back_menu_button,
)
from app.objects.abstract_objects.abstract_tables import DetailTable
from app.frontend.utilities.files.render_files import is_delete_button, is_qr_button, is_replace_button

## Replace button - one per public file
## QR code - one per public file


def display_form_file_management(interface: abstractInterface) -> Form:
    public_files = DetailTable(
        list_of_all_public_files_with_options(), name="Public files"
    )
    private_files = DetailTable(
        list_of_all_private_download_files_with_options(),
        name="Private downloaded files (temporary)",
    )
    upload_files = DetailTable(
        list_of_all_upload_files_with_options(),
        name="Private uploaded files (temporary)",
    )
    lines_inside_form = ListOfLines(
        [
            nav_buttons,
            Heading("File Management"),
            _______________,
            public_file_header,
            public_files,
            _______________,
            downloads_file_header,
            private_files,
            _______________,
            uploads_file_hedaer,
            upload_files,
        ]
    )

    return Form(lines_inside_form)


def post_form_file_management(
    interface: abstractInterface,
) -> Union[NewForm, Form, File]:
    button_pressed = interface.last_button_pressed()
    if back_menu_button.pressed(button_pressed):
        return interface.get_new_display_form_for_parent_of_function(
            post_form_file_management
        )
    elif upload_public_file_button.pressed(button_pressed):
        return interface.get_new_form_given_function(
            display_form_for_upload_public_file
        )

    elif is_qr_button(button_pressed):
        return generate_qr_code(button_pressed)

    elif is_replace_button(button_pressed):
        return replace_button_pressed(interface)

    if clear_temp_files_button.pressed(button_pressed):
        delete_private_temporary_files()

    elif clear_staging_files_button.pressed(button_pressed):
        delete_uploaded_temporary_files()

    elif clear_public_file_button.pressed(button_pressed):
        delete_public_files()

    elif is_delete_button(button_pressed):
        delete_specific_file(button_pressed)

    elif delete_selected_files_button.pressed(button_pressed):
        delete_selected_files(interface)

    else:
        return button_error_and_back_to_initial_state_form(interface)

    return display_form_file_management(interface)

def replace_button_pressed(interface: abstractInterface) -> NewForm:
    button_pressed = interface.last_button_pressed()
    directory, filename = directory_and_filename_from_replace_button_name(
        button_pressed
    )
    store_directory_and_filename(
        interface=interface, directory_name=directory, filename=filename
    )
    return interface.get_new_form_given_function(
        display_form_to_replace_selected_files
    )