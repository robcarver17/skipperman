from app.frontend.utilities.files.state import (
    retrieve_directory_and_filename,
    clear_directory_and_filename,
)
import os

from werkzeug.exceptions import RequestEntityTooLarge

from app.data_access.init_directories import web_pathname_of_file
from app.objects.abstract_objects.abstract_form import fileInput, Form
from app.objects.abstract_objects.abstract_buttons import (
    CANCEL_BUTTON_LABEL,
    Button,
    ButtonBar,
)
from app.objects.abstract_objects.abstract_lines import Line, ListOfLines
from app.objects.abstract_objects.abstract_interface import (
    abstractInterface, form_with_message_and_finished_button, get_file_from_interface,
)

empty_name = ""
FILE_FIELD = "file"
UPLOAD_FILE_BUTTON_LABEL = "Upload replacement file"


def display_form_to_replace_selected_files(interface: abstractInterface) -> Form:
    directory_name, filename = retrieve_directory_and_filename(interface)
    buttons = ButtonBar([cancel_button, upload_button])
    file_select_field = fileInput(input_name=FILE_FIELD)

    list_of_lines = ListOfLines(
        [
            Line("Choose file to upload, replacing existing file %s" % filename),
            Line(file_select_field),
            buttons,
        ]
    )

    return Form(list_of_lines)


upload_button = Button(UPLOAD_FILE_BUTTON_LABEL, nav_button=True)
cancel_button = Button(CANCEL_BUTTON_LABEL, nav_button=True)


def post_form_to_replace_selected_files(interface: abstractInterface):
    try:
        last_button = interface.last_button_pressed()
    except RequestEntityTooLarge:
        interface.log_error(
            "File is too big to upload - change configuration or use a smaller file"
        )
        return display_form_to_replace_selected_files(interface)

    if last_button == CANCEL_BUTTON_LABEL:
        previous_form = interface.get_new_display_form_for_parent_of_function(
            display_form_to_replace_selected_files
        )
        return previous_form

    directory_name, filename = retrieve_directory_and_filename(interface)
    full_filename = os.path.join(directory_name, filename)
    web_path = web_pathname_of_file(filename)

    try:
        file = get_file_from_interface(FILE_FIELD, interface=interface)
        file.save(full_filename)
    except Exception as e:
        interface.log_error("Something went wrong uploading file: error %s" % str(e))
        return display_form_to_replace_selected_files(interface)

    clear_directory_and_filename(interface)

    return form_with_message_and_finished_button(
        "Uploaded replacement file %s" % (web_path),
        interface=interface,
        function_whose_parent_go_to_on_button_press=display_form_to_replace_selected_files,
    )
