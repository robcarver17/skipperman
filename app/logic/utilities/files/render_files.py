import os.path
from typing import List, Tuple

from app.data_access.file_access import public_reporting_directory, download_directory, upload_directory, \
    get_files_in_directory, web_pathname_of_file
from app.objects.abstract_objects.abstract_buttons import Button, ButtonBar, main_menu_button, BACK_BUTTON_LABEL
from app.objects.abstract_objects.abstract_form import checkboxInput
from app.objects.abstract_objects.abstract_tables import Table, RowInTable


def list_of_all_public_files_with_options()-> Table:
    return list_of_all_files_in_directory_with_options(public_reporting_directory,
                                                       show_replace_button=True,
                                                       show_qr_code_button=True,
                                                       include_web_path=True)


def list_of_all_private_download_files_with_options()-> Table:
    return list_of_all_files_in_directory_with_options(download_directory, show_qr_code_button=False, show_replace_button=False)


def list_of_all_upload_files_with_options()-> Table:
    return list_of_all_files_in_directory_with_options(upload_directory, show_replace_button=False, show_qr_code_button=False)


def list_of_all_files_in_directory_with_options(directory_name: str, show_qr_code_button: bool = False,show_replace_button: bool= False,
                                                include_web_path: bool = False) -> Table:
    all_files = get_files_in_directory(directory_name)

    return Table([
        line_for_file_in_directory(directory_name=directory_name,
                                   filename=filename,
                                   show_replace_button=show_replace_button,
                                   show_qr_code_button=show_qr_code_button,
                                   include_web_path=include_web_path)
        for filename in all_files
    ])


DELETE_IN_CHECKBOX = "Select"


def line_for_file_in_directory(directory_name: str, filename:str, show_qr_code_button: bool = False, show_replace_button: bool= False,
                               include_web_path: bool = False)-> RowInTable:
    if include_web_path:
        display_name = web_pathname_of_file(filename)
    else:
        display_name = filename

    checkbox = checkboxInput(input_name=checkbox_name_for_filename(directory_name=directory_name, filename=filename),
                             dict_of_labels={DELETE_IN_CHECKBOX: DELETE_IN_CHECKBOX},
                             dict_of_checked={DELETE_IN_CHECKBOX: False},
                             input_label='')
    delete_button = Button(label="Delete", value = button_name_for_filename(directory_name=directory_name, filename=filename, button_type=DELETE))
    line_for_file = [display_name, checkbox, delete_button]
    if show_qr_code_button:
        qr_button = Button("QR code", value=button_name_for_filename(directory_name=directory_name, filename=filename, button_type=QR))
        line_for_file.append(qr_button)
    if show_replace_button:
        replace_button = Button("Replace", value=button_name_for_filename(directory_name, filename=filename, button_type=REPLACE))
        line_for_file.append(replace_button)

    return RowInTable(line_for_file)


def checkbox_name_for_filename(directory_name: str, filename:str) -> str:
    return "check_%s_%s" % (directory_name, filename)


def get_list_of_all_qr_buttons() -> List[str]:
    qr_public = list_of_all_buttons_given_directory_and_button_name(public_reporting_directory, button_type=QR)
    ## Don't do QR for others

    return qr_public

def get_list_of_all_replace_buttons() -> List[str]:
    replace_public = list_of_all_buttons_given_directory_and_button_name(public_reporting_directory, button_type=REPLACE)
    ## Don't do replace for others

    return replace_public



def get_list_of_all_delete_buttons() -> List[str]:
    delete_public = list_of_all_buttons_given_directory_and_button_name(public_reporting_directory, button_type=DELETE)
    delete_downloads = list_of_all_buttons_given_directory_and_button_name(download_directory, button_type=DELETE)
    delete_uploads= list_of_all_buttons_given_directory_and_button_name(upload_directory, button_type=DELETE)

    return delete_uploads+delete_downloads+delete_public


def list_of_all_buttons_given_directory_and_button_name(directory_name: str, button_type:str) -> List[str]:
    all_files = get_files_in_directory(directory_name)

    return [button_name_for_filename(directory_name=directory_name, filename=filename, button_type=button_type) for filename in all_files]

QR="qr"
REPLACE = "replace"
DELETE = "delete"
def button_name_for_filename(directory_name: str, filename:str, button_type: str) -> str:
    ## may get underscores in directory and filename, so use a special seperator
    return "%s*%s*%s" % (button_type, directory_name, filename)

def type_directory_and_filename_from_button_name(button_name: str) -> Tuple[str,str,str]:
    type_directory_filename= button_name.split("*")
    return type_directory_filename[0], type_directory_filename[1], type_directory_filename[2]


CLEAR_TEMP_BUTTON_LABEL = "Delete temporary download files" # DOWNLOAD_DIRECTORY
CLEAR_STAGING_BUTTON_LABEL = "Delete all temporary uploaded files" ## STAGING
CLEAR_PUBLIC_BUTTON_LABEL= "Delete all public file(s)" # PUBLIC_REPORTING_SUBDIRECTORY
UPLOAD_PUBLIC_FILE = "Upload new public file"
DELETE_SELECTED_FILES = "Delete selected files"
nav_buttons = ButtonBar([main_menu_button, Button(BACK_BUTTON_LABEL, nav_button=True)
                         ])
public_file_header = ButtonBar([Button(UPLOAD_PUBLIC_FILE, nav_button=True),
                                Button(DELETE_SELECTED_FILES, nav_button=True),
                                Button(CLEAR_PUBLIC_BUTTON_LABEL, nav_button=True)])
downloads_file_header = ButtonBar([Button(CLEAR_TEMP_BUTTON_LABEL, nav_button=True),
                                   Button(DELETE_SELECTED_FILES, nav_button=True)])
uploads_file_hedaer = ButtonBar([Button(CLEAR_STAGING_BUTTON_LABEL, nav_button=True),
                                 Button(DELETE_SELECTED_FILES, nav_button=True)])
