import os

from app.frontend.utilities.files.render_files import (
    checkbox_name_for_filename,
    DELETE_IN_CHECKBOX,
    type_directory_and_filename_from_button_name,
)

from app.objects_OLD.abstract_objects.abstract_interface import abstractInterface
from app.data_access.file_access import (
    public_reporting_directory,
    download_directory,
    upload_directory,
    get_files_in_directory,
)


def delete_selected_files(interface: abstractInterface):
    delete_selected_files_in_directory(
        interface=interface, directory_name=public_reporting_directory
    )
    delete_selected_files_in_directory(
        interface=interface, directory_name=download_directory
    )
    delete_selected_files_in_directory(
        interface=interface, directory_name=upload_directory
    )


def delete_selected_files_in_directory(
    interface: abstractInterface, directory_name: str
):
    all_files = get_files_in_directory(directory_name)
    for filename in all_files:
        check_if_file_selected_and_delete(
            interface=interface, directory_name=directory_name, filename=filename
        )


def check_if_file_selected_and_delete(
    interface: abstractInterface, directory_name: str, filename: str
):
    checkbox_list = interface.value_of_multiple_options_from_form(
        checkbox_name_for_filename(directory_name=directory_name, filename=filename),
        default=[],
    )  ## if file recently created won't be in list

    if DELETE_IN_CHECKBOX in checkbox_list:
        full_filename = os.path.join(directory_name, filename)
        try:
            os.remove(full_filename)
        except:
            ## edge case if someone else has deleted file
            print("File %s already deleted" % full_filename)


def delete_public_files():
    delete_all_files_in_directory(public_reporting_directory)


def delete_private_temporary_files():
    delete_all_files_in_directory(download_directory)


def delete_uploaded_temporary_files():
    delete_all_files_in_directory(upload_directory)


def delete_all_files_in_directory(directory_name: str):
    all_files = get_files_in_directory(directory_name)
    for filename in all_files:
        full_filename = os.path.join(directory_name, filename)
        try:
            os.remove(full_filename)
        except:
            ## edge case if someone else has deleted file
            print("File %s already deleted" % full_filename)


def delete_specific_file(button_pressed: str):
    type, directory, filename = type_directory_and_filename_from_button_name(
        button_pressed
    )
    full_filename = os.path.join(directory, filename)

    try:
        os.remove(full_filename)
    except:
        ## edge case if someone else has deleted file
        print("File %s already deleted" % full_filename)
