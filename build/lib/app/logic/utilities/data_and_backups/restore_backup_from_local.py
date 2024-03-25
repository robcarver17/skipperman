import os

from app.data_access.data import master_data_path
from app.data_access.uploads_and_downloads import download_directory

import shutil
from typing import Union

from app.logic.abstract_logic_api import button_error_and_back_to_initial_state_form
from app.objects.abstract_objects.abstract_buttons import BACK_BUTTON_LABEL, Button
from app.objects.abstract_objects.abstract_form import fileInput, Form, NewForm
from app.objects.abstract_objects.abstract_interface import abstractInterface, get_file_from_interface
from app.objects.abstract_objects.abstract_lines import ListOfLines, Line

ZIPPED_FILE = "zipped_file"
UPLOAD_FILE_BUTTON_LABEL = "Upload file - will delete all existing data - be *VERY* sure about this!"

def display_form_for_upload_backup(interface: abstractInterface):

    buttons = get_upload_buttons()
    prompt = "Choose file. Must be a zip file with the correct directory structure. Wrong file will result in messed up data with no recourse except restoring!"
    input_field = fileInput(input_name=ZIPPED_FILE, accept=".zip")

    list_of_lines = ListOfLines([prompt, input_field, buttons])

    return Form(list_of_lines)


def get_upload_buttons():
    upload = Button(UPLOAD_FILE_BUTTON_LABEL)
    back_button = Button(BACK_BUTTON_LABEL)

    return Line([back_button, upload])


def post_form_upload_backup_file(interface: abstractInterface) -> Union[Form, NewForm]:
    ## Called by post on view events form, so both stage and event name are set

    button_pressed = interface.last_button_pressed()
    ## check button pressed (can only be upload or back - anything else treat as back as must be an error)
    if button_pressed == UPLOAD_FILE_BUTTON_LABEL:
        return respond_to_uploaded_file(interface)
    elif button_pressed == BACK_BUTTON_LABEL:
        return previous_form(interface)
    else:
        button_error_and_back_to_initial_state_form(interface)

def previous_form(interface: abstractInterface) -> NewForm:
    return interface.get_new_display_form_for_parent_of_function(display_form_for_upload_backup)

def respond_to_uploaded_file(interface: abstractInterface) -> Union[Form, NewForm]:
    try:
        file = get_file_from_interface(ZIPPED_FILE, interface=interface)
        process_uploaded_zip_file(file=file, interface=interface)
    except Exception as e:
        interface.log_error("Error %s when uploading file" % str(e))

    return previous_form(interface)

def process_uploaded_zip_file(interface: abstractInterface, file):
    temp_filename = os.path.join(download_directory, "tempzipfile.zip")
    file.save(temp_filename)
    temp_dir = os.path.join(download_directory, "temp")
    interface.log_message("Creating temporary directory")
    try:
        os.mkdir(temp_dir)
    except:
        pass
    interface.log_message("Unpacking zip file")
    shutil.unpack_archive(temp_filename, temp_dir)
    interface.log_message("Deleting existing data")
    shutil.rmtree(master_data_path)
    interface.log_message("Copying over data from temporary director")
    shutil.copytree(temp_dir, master_data_path, dirs_exist_ok=True)
    interface.log_message("Deleting temporary directory")
    shutil.rmtree(temp_dir)
    interface.log_message("Restore backup done")
