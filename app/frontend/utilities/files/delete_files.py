import os

from app.frontend.utilities.files.render_files import (
    checkbox_name_for_filename,
    DELETE_IN_CHECKBOX,
    directory_and_filename_from_delete_button_name,
)

from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.data_access.file_access import (
    get_files_in_directory, get_newest_file_matching_filename,
    get_files_in_directory_mask_suffix_and_extension_from_filename_remove_duplicates,
)
from app.data_access.init_directories import (
    public_reporting_directory,
    upload_directory,
    download_directory,
)
from app.objects.utilities.exceptions import MISSING_FROM_FORM


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
    if directory_name == public_reporting_directory:
        all_files = get_files_in_directory_mask_suffix_and_extension_from_filename_remove_duplicates(directory_name)
    else:
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
        default=MISSING_FROM_FORM,
    )  ## if file recently created won't be in list
    if checkbox_list is MISSING_FROM_FORM:
        return

    if DELETE_IN_CHECKBOX in checkbox_list:
        if directory_name == public_reporting_directory:
            full_filename = get_newest_file_matching_filename(filename=filename, pathname=public_reporting_directory)
        else:
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
    full_filename = directory_and_filename_from_delete_button_name(button_pressed)

    try:
        os.remove(full_filename)
    except:
        ## edge case if someone else has deleted file
        print("File %s already deleted" % full_filename)
