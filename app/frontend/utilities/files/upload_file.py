from copy import copy

from werkzeug.exceptions import RequestEntityTooLarge

from app.data_access.configuration.configuration import (
    PUBLIC_REPORTING_SUBDIRECTORY,
    HOMEPAGE,
)
from app.data_access.file_access import (
    PathAndFilename,
    get_newest_file_matching_filename,
    add_suffix_to_public_filename,
    get_filename_and_extension,
    get_files_in_directory_mask_suffix_and_extension_from_filename_remove_duplicates,
)
from app.data_access.init_directories import (
    public_reporting_directory,
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
    form_with_message_and_finished_button,
    get_file_from_interface,
)
from app.data_access.file_access import (
    web_pathname_of_public_version_of_local_file_without_extension,
)
from app.objects.utilities.exceptions import MissingData, MISSING_FROM_FORM

empty_name = ""
FILE_NAME = "filename"
FILE_FIELD = "file"
UPLOAD_FILE_BUTTON_LABEL = "Upload file"


def display_form_for_upload_public_file(interface: abstractInterface):
    buttons = ButtonBar([cancel_button, upload_button])
    template_name_field = textInput(
        input_name=FILE_NAME,
        input_label="Enter name of file to display",
        value=empty_name,
    )
    file_select_field = fileInput(input_name=FILE_FIELD)

    list_of_lines = ListOfLines(
        [
            Line("Choose file to upload which will be publicly accesible"),
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
    file_object = get_file_from_interface(FILE_FIELD, interface=interface)

    try:
        output_path_and_filename = get_extension_and_filename_from_form(interface)
    except Exception as e:
        interface.log_error(str(e))
        return display_form_for_upload_public_file(interface)

    output_path_and_filename = add_extension_if_missing(
        interface=interface,
        path_and_filename=output_path_and_filename,
        file_object=file_object,
    )

    original_raw_filename = copy(output_path_and_filename.filename_without_extension)
    web_path = web_pathname_of_public_version_of_local_file_without_extension(
        PathAndFilename(original_raw_filename),
        public_path=PUBLIC_REPORTING_SUBDIRECTORY,
        webserver_url=HOMEPAGE,
    )
    web_path = web_path.replace(" ", "%")

    add_suffix_to_public_filename(output_path_and_filename)
    output_path_and_filename.replace_path(public_reporting_directory)
    full_filename = output_path_and_filename.full_path_and_name

    try:
        file_object.save(full_filename)
    except Exception as e:
        interface.log_error("Something went wrong uploading file: error %s" % str(e))
        return display_form_for_upload_public_file(interface)

    return form_with_message_and_finished_button(
        "Uploaded new file %s" % (web_path),
        interface=interface,
        function_whose_parent_go_to_on_button_press=display_form_for_upload_public_file,
    )


def get_extension_and_filename_from_form(
    interface: abstractInterface,
) -> PathAndFilename:
    filename = interface.value_from_form(FILE_NAME, default=MISSING_FROM_FORM)
    if filename is MISSING_FROM_FORM:
        raise Exception("Problem with form")
    if len(filename) == 0:
        raise Exception("You need to enter the filename")

    filename_without_extension, extension = get_filename_and_extension(filename)
    list_of_bare_files = get_files_in_directory_mask_suffix_and_extension_from_filename_remove_duplicates(
        public_reporting_directory
    )
    if filename_without_extension in list_of_bare_files:
        raise Exception(
            "An identical filename %s already exists (perhaps with another extension) - change filename or use update button instead to replace it."
            % filename_without_extension
        )

    ## good, file doesn't exist yet
    return PathAndFilename(
        filename_without_extension=filename_without_extension, extension=extension
    )


def add_extension_if_missing(
    interface: abstractInterface, path_and_filename: PathAndFilename, file_object
) -> PathAndFilename:
    if len(path_and_filename.extension) > 0:
        return path_and_filename

    filename_without_extension, extension = get_filename_and_extension(
        file_object.filename
    )

    if len(extension) == 0:
        interface.log_error("No extension on uploaded file -may cause weird behaviour")
    else:
        interface.log_error(
            "No extension provided in filename, using %s from file" % extension
        )

    path_and_filename.extension = extension

    return path_and_filename
