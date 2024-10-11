import os

from werkzeug.exceptions import RequestEntityTooLarge

from app.data_access.file_access import (
    public_reporting_directory,
    web_pathname_of_file,
    get_files_in_directory,
)
from app.objects.abstract_objects.abstract_form import textInput, fileInput, Form
from app.objects.abstract_objects.abstract_buttons import (
    CANCEL_BUTTON_LABEL,
    Button,
    ButtonBar,
)
from app.objects.abstract_objects.abstract_lines import Line, ListOfLines
from app.objects.abstract_objects.abstract_interface import (
    abstractInterface,
    get_file_from_interface,
    form_with_message_and_finished_button,
)

empty_name = ""
FILE_NAME = "filename"
FILE_FIELD = "file"
UPLOAD_FILE_BUTTON_LABEL = "Upload file"


def display_form_for_upload_public_file(interface: abstractInterface):
    buttons = ButtonBar([cancel_button, upload_button])
    template_name_field = textInput(
        input_name=FILE_NAME, input_label="Enter filename name", value=empty_name
    )
    file_select_field = fileInput(input_name=FILE_FIELD)

    list_of_lines = ListOfLines(
        [
            Line("Choose file to upload which will be publically accesible"),
            Line(template_name_field),
            Line(file_select_field),
            buttons,
        ]
    )

    return Form(list_of_lines)


upload_button = Button(UPLOAD_FILE_BUTTON_LABEL, nav_button=True)
cancel_button = Button(CANCEL_BUTTON_LABEL, nav_button=True)


def post_form_for_upload_public_file(interface: abstractInterface):
    try:
        last_button = interface.last_button_pressed()
    except RequestEntityTooLarge:
        interface.log_error("File is too big to upload")
        return display_form_for_upload_public_file(interface)

    if cancel_button.pressed(last_button):
        previous_form = interface.get_new_display_form_for_parent_of_function(
            display_form_for_upload_public_file
        )
        return previous_form

    return get_filename_and_save_new_file(interface)


def get_filename_and_save_new_file(interface: abstractInterface) -> Form:
    try:
        filename = get_filename_from_form(interface)
    except Exception as e:
        interface.log_error(str(e))
        return display_form_for_upload_public_file(interface)

    full_filename = os.path.join(public_reporting_directory, filename)
    web_path = web_pathname_of_file(filename)
    try:
        file = get_file_from_interface(FILE_FIELD, interface=interface)
        file.save(full_filename)
    except Exception as e:
        interface.log_error("Something went wrong uploading file: error %s" % str(e))
        return display_form_for_upload_public_file(interface)

    return form_with_message_and_finished_button(
        "Uploaded new file %s" % (web_path),
        interface=interface,
        function_whose_parent_go_to_on_button_press=display_form_for_upload_public_file,
    )



def get_filename_from_form(interface: abstractInterface) -> str:
    filename = interface.value_from_form(FILE_NAME)
    if len(filename) == 0:
        raise Exception("You need to enter the filename")

    if filename in get_files_in_directory(public_reporting_directory):
        raise Exception("Filename already exists - use update button instead")

    return filename