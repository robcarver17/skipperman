from typing import List, Tuple

from app.data_access.file_access import (
    get_files_in_directory,
)
from app.data_access.init_directories import (
    public_reporting_directory,
    upload_directory,
    download_directory,
    web_pathname_of_file,
)
from app.objects.abstract_objects.abstract_buttons import (
    Button,
    ButtonBar,
    main_menu_button,
    back_menu_button,
    HelpButton,
)
from app.objects.abstract_objects.abstract_form import checkboxInput
from app.objects.abstract_objects.abstract_tables import Table, RowInTable
from app.frontend.shared.buttons import (
    get_attributes_from_button_pressed_of_known_type,
    get_button_value_given_type_and_attributes,
    is_button_of_type,
)


def list_of_all_public_files_with_options() -> Table:
    return list_of_all_files_in_directory_with_options(
        public_reporting_directory,
        show_replace_button=True,
        show_qr_code_button=True,
        include_web_path=True,
    )


def list_of_all_private_download_files_with_options() -> Table:
    return list_of_all_files_in_directory_with_options(
        download_directory, show_qr_code_button=False, show_replace_button=False
    )


def list_of_all_upload_files_with_options() -> Table:
    return list_of_all_files_in_directory_with_options(
        upload_directory, show_replace_button=False, show_qr_code_button=False
    )


def list_of_all_files_in_directory_with_options(
    directory_name: str,
    show_qr_code_button: bool = False,
    show_replace_button: bool = False,
    include_web_path: bool = False,
) -> Table:
    all_files = get_files_in_directory(directory_name)

    return Table(
        [
            line_for_file_in_directory(
                directory_name=directory_name,
                filename=filename,
                show_replace_button=show_replace_button,
                show_qr_code_button=show_qr_code_button,
                include_web_path=include_web_path,
            )
            for filename in all_files
        ]
    )


DELETE_IN_CHECKBOX = "Select"


def line_for_file_in_directory(
    directory_name: str,
    filename: str,
    show_qr_code_button: bool = False,
    show_replace_button: bool = False,
    include_web_path: bool = False,
) -> RowInTable:
    if include_web_path:
        display_name = web_pathname_of_file(filename)
    else:
        display_name = filename

    checkbox = checkboxInput(
        input_name=checkbox_name_for_filename(
            directory_name=directory_name, filename=filename
        ),
        dict_of_labels={DELETE_IN_CHECKBOX: DELETE_IN_CHECKBOX},
        dict_of_checked={DELETE_IN_CHECKBOX: False},
        input_label="",
    )
    delete_button = Button(
        label="Delete",
        value=button_name_for_delete(directory_name=directory_name, filename=filename),
    )
    line_for_file = [display_name, checkbox, delete_button]
    if show_qr_code_button:
        qr_button = Button(
            "QR code",
            value=button_name_for_qr(directory_name=directory_name, filename=filename),
        )
        line_for_file.append(qr_button)
    if show_replace_button:
        replace_button = Button(
            "Replace",
            value=button_name_for_replace(directory_name, filename=filename),
        )
        line_for_file.append(replace_button)

    return RowInTable(line_for_file)


def checkbox_name_for_filename(directory_name: str, filename: str) -> str:
    return "check_%s_%s" % (directory_name, filename)


QR = "qr"
REPLACE = "replace"
DELETE = "delete"


def button_name_for_qr(directory_name: str, filename: str) -> str:
    ## may get underscores in directory and filename, so use a special seperator
    return get_button_value_given_type_and_attributes(
        QR,
        directory_name,
        filename,
    )


def button_name_for_replace(directory_name: str, filename: str) -> str:
    ## may get underscores in directory and filename, so use a special seperator
    return get_button_value_given_type_and_attributes(
        REPLACE,
        directory_name,
        filename,
    )


def button_name_for_delete(directory_name: str, filename: str) -> str:
    ## may get underscores in directory and filename, so use a special seperator
    return get_button_value_given_type_and_attributes(
        DELETE,
        directory_name,
        filename,
    )


def directory_and_filename_from_qr_button_name(
    button_name: str,
) -> Tuple[str, str]:
    return get_attributes_from_button_pressed_of_known_type(
        value_of_button_pressed=button_name, type_to_check=QR
    )


def directory_and_filename_from_replace_button_name(
    button_name: str,
) -> Tuple[str, str]:
    return get_attributes_from_button_pressed_of_known_type(
        value_of_button_pressed=button_name, type_to_check=REPLACE
    )


def directory_and_filename_from_delete_button_name(
    button_name: str,
) -> Tuple[str, str]:
    return get_attributes_from_button_pressed_of_known_type(
        value_of_button_pressed=button_name, type_to_check=DELETE
    )


def is_qr_button(button_value: str):
    return is_button_of_type(button_value, type_to_check=QR)


def is_delete_button(button_value: str):
    return is_button_of_type(button_value, type_to_check=DELETE)


def is_replace_button(button_value: str):
    return is_button_of_type(button_value, type_to_check=REPLACE)


CLEAR_TEMP_BUTTON_LABEL = "Delete all temporary download files"  # DOWNLOAD_DIRECTORY
CLEAR_STAGING_BUTTON_LABEL = "Delete all temporary uploaded files"  ## STAGING
CLEAR_PUBLIC_BUTTON_LABEL = "Delete all public file(s)"  # PUBLIC_REPORTING_SUBDIRECTORY
UPLOAD_PUBLIC_FILE = "Upload new public file"
DELETE_SELECTED_FILES = "Delete selected files"


upload_public_file_button = Button(UPLOAD_PUBLIC_FILE, nav_button=True)
delete_selected_files_button = Button(DELETE_SELECTED_FILES, nav_button=True)
clear_public_file_button = Button(CLEAR_PUBLIC_BUTTON_LABEL, nav_button=True)
clear_temp_files_button = Button(CLEAR_TEMP_BUTTON_LABEL, nav_button=True)
clear_staging_files_button = Button(CLEAR_STAGING_BUTTON_LABEL, nav_button=True)
help_button = HelpButton("file_management_help")

nav_buttons = ButtonBar([main_menu_button, back_menu_button, help_button])


public_file_header = ButtonBar(
    [upload_public_file_button, delete_selected_files_button, clear_public_file_button]
)
downloads_file_header = ButtonBar(
    [clear_temp_files_button, delete_selected_files_button]
)
uploads_file_hedaer = ButtonBar(
    [clear_staging_files_button, delete_selected_files_button]
)
