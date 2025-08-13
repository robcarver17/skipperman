from app.backend.reporting.process_stages.create_file_from_list_of_columns import (
    delete_existing_public_files,
    get_public_filename_with_suffix_given_local_file,
)
from app.data_access.configuration.configuration import (
    PUBLIC_REPORTING_SUBDIRECTORY,
    HOMEPAGE,
)
from app.data_access.init_directories import public_reporting_directory
from app.frontend.utilities.files.state import (
    retrieve_directory_and_filename,
    clear_directory_and_filename,
)
import os

from werkzeug.exceptions import RequestEntityTooLarge

from app.objects.abstract_objects.abstract_form import fileInput, Form
from app.objects.abstract_objects.abstract_buttons import (
    CANCEL_BUTTON_LABEL,
    Button,
    ButtonBar,
)
from app.objects.abstract_objects.abstract_lines import Line, ListOfLines
from app.objects.abstract_objects.abstract_interface import (
    abstractInterface,
    form_with_message_and_finished_button,
    get_file_from_interface,
)
from app.data_access.file_access import (
    web_pathname_of_public_version_of_local_file_without_extension,
    PathAndFilename,
)

empty_name = ""
FILE_FIELD = "file"
UPLOAD_FILE_BUTTON_LABEL = "Upload replacement file"


def display_form_to_replace_selected_files(interface: abstractInterface) -> Form:
    directory_name, filename = retrieve_directory_and_filename(interface)
    try:
        assert directory_name == public_reporting_directory
    except:
        raise Exception("Can only replace public files")

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

    __, original_raw_filename = retrieve_directory_and_filename(interface)
    original_path_and_filename = PathAndFilename(
        filename_without_extension=original_raw_filename,
        path=public_reporting_directory,
    )

    web_path = web_pathname_of_public_version_of_local_file_without_extension(
        original_path_and_filename,
        public_path=PUBLIC_REPORTING_SUBDIRECTORY,
        webserver_url=HOMEPAGE,
    )

    try:
        file = get_file_from_interface(FILE_FIELD, interface=interface)
        extension= file.content_type
        delete_existing_public_files(original_path_and_filename)
        full_filename = get_public_filename_with_suffix_given_local_file(
            original_path_and_filename
        )
        full_filename.add_or_replace_extension(extension)

        file.save(full_filename.full_path_and_name)

    except Exception as e:
        interface.log_error("Something went wrong uploading file: error %s" % str(e))
        return display_form_to_replace_selected_files(interface)

    clear_directory_and_filename(interface)

    return form_with_message_and_finished_button(
        "Uploaded replacement file %s" % (web_path),
        interface=interface,
        function_whose_parent_go_to_on_button_press=display_form_to_replace_selected_files,
    )
