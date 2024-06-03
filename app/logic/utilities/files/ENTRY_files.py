from typing import Union

from app.logic.utilities.files.delete_files import delete_selected_files, delete_public_files, \
    delete_private_temporary_files, delete_uploaded_temporary_files, delete_specific_file
from app.logic.utilities.files.qr_codes import generate_qr_code
from app.logic.utilities.files.replace_files import display_form_to_replace_selected_files
from app.logic.utilities.files.state import store_directory_and_filename
from app.logic.utilities.files.upload_file import display_form_for_upload_public_file

from app.logic.abstract_logic_api import button_error_and_back_to_initial_state_form
from app.logic.utilities.files.render_files import list_of_all_public_files_with_options, \
    list_of_all_private_download_files_with_options, list_of_all_upload_files_with_options, nav_buttons, \
    public_file_header, downloads_file_header, uploads_file_hedaer, CLEAR_TEMP_BUTTON_LABEL, CLEAR_STAGING_BUTTON_LABEL, \
    CLEAR_PUBLIC_BUTTON_LABEL, UPLOAD_PUBLIC_FILE, DELETE_SELECTED_FILES, get_list_of_all_qr_buttons, \
    get_list_of_all_delete_buttons, get_list_of_all_replace_buttons, type_directory_and_filename_from_button_name
from app.objects.abstract_objects.abstract_form import Form, NewForm, File
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_lines import ListOfLines,  _______________
from app.objects.abstract_objects.abstract_text import Heading
from app.objects.abstract_objects.abstract_buttons import BACK_BUTTON_LABEL
from app.objects.abstract_objects.abstract_tables import DetailTable


## Replace button - one per public file
## QR code - one per public file

def display_form_file_management(interface: abstractInterface) -> Form:
    public_files = DetailTable(list_of_all_public_files_with_options(), name='Public files')
    private_files = DetailTable(list_of_all_private_download_files_with_options(), name='Private downloaded files (temporary)')
    upload_files = DetailTable(list_of_all_upload_files_with_options(), name='Private uploaded files (temporary)')
    lines_inside_form = ListOfLines([
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
        upload_files
    ])

    return Form(lines_inside_form)




def post_form_file_management(interface: abstractInterface) -> Union[NewForm, Form, File]:
    button_pressed = interface.last_button_pressed()
    if button_pressed == BACK_BUTTON_LABEL:
        return interface.get_new_display_form_for_parent_of_function(post_form_file_management)
    if button_pressed == CLEAR_TEMP_BUTTON_LABEL:
        delete_private_temporary_files()
    elif button_pressed == CLEAR_STAGING_BUTTON_LABEL:
        delete_uploaded_temporary_files()
    elif button_pressed == CLEAR_PUBLIC_BUTTON_LABEL:
        delete_public_files()
    elif button_pressed == UPLOAD_PUBLIC_FILE:
        return interface.get_new_form_given_function(display_form_for_upload_public_file)

    elif button_pressed in get_list_of_all_qr_buttons():
        return generate_qr_code(button_pressed)

    elif button_pressed in get_list_of_all_delete_buttons():
        delete_specific_file(button_pressed)
    elif button_pressed in get_list_of_all_replace_buttons():
        type, directory, filename = type_directory_and_filename_from_button_name(button_pressed)
        store_directory_and_filename(interface=interface, directory_name=directory, filename=filename)
        print("replace %s %s" % (directory, filename))
        return interface.get_new_form_given_function(display_form_to_replace_selected_files)

    elif button_pressed == DELETE_SELECTED_FILES:
        delete_selected_files(interface)
    else:
        return button_error_and_back_to_initial_state_form(interface)

    return display_form_file_management(interface)


