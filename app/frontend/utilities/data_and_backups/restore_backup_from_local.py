import os

from app.data_access.init_directories import download_directory

import shutil
from typing import Union

from app.frontend.form_handler import button_error_and_back_to_initial_state_form
from app.objects.abstract_objects.abstract_buttons import (
    BACK_BUTTON_LABEL,
    Button,
    ButtonBar,
    HelpButton,
)
from app.objects.abstract_objects.abstract_form import fileInput, Form, NewForm
from app.objects.abstract_objects.abstract_interface import (
    abstractInterface,
    get_file_from_interface,
)
from app.objects.abstract_objects.abstract_lines import ListOfLines, Line
from app.objects.abstract_objects.abstract_text import Heading

ZIPPED_FILE = "zipped_file"
UPLOAD_FILE_BUTTON_LABEL = (
    "Upload file - will delete all existing data - be *VERY* sure about this!"
)


def display_form_for_upload_backup(interface: abstractInterface):
    buttons = get_upload_buttons()
    prompts = [
        Heading(
            "Choose file. Must be a .zip file with the correct directory structure",
            size=4,
        ),
        Heading(
            "WILL OVERWRITE ALL EXISTING DATA - THERE IS NO 'ARE YOU SURE' DIALOG",
            size=2,
        ),
        Heading(
            " Wrong file will result in messed up data and unpredictable effects!",
            size=3,
        ),
        Heading(
            "Can only be undone by going to a more recent snapshot or restoring data from another zip file",
            size=3,
        ),
        Heading(
            "I *strongly* recommend you snapshot the data first before doing this, just in case",
            size=3,
        ),
        Heading("Click 'Back' if unsure about doing this", size=4),
    ]

    input_field = Line(fileInput(input_name=ZIPPED_FILE, accept=".zip"))

    list_of_lines = ListOfLines(prompts + [input_field, buttons])

    return Form(list_of_lines)


def get_upload_buttons():
    return ButtonBar([back_button, upload_button, help_button])


upload_button = Button(UPLOAD_FILE_BUTTON_LABEL, nav_button=True)
back_button = Button(BACK_BUTTON_LABEL, nav_button=True)
help_button = HelpButton("data_backup_help")


def post_form_upload_backup_file(interface: abstractInterface) -> Union[Form, NewForm]:
    ## Called by post on view events form, so both stage and event name are set

    button_pressed = interface.last_button_pressed()
    ## check button pressed (can only be upload or back - anything else treat as back as must be an error)
    if upload_button.pressed(button_pressed):
        return respond_to_uploaded_file(interface)
    elif back_button.pressed(button_pressed):
        return previous_form(interface)
    else:
        button_error_and_back_to_initial_state_form(interface)


def previous_form(interface: abstractInterface) -> NewForm:
    return interface.get_new_display_form_for_parent_of_function(
        display_form_for_upload_backup
    )


def respond_to_uploaded_file(interface: abstractInterface) -> Union[Form, NewForm]:
    try:
        file = get_file_from_interface(ZIPPED_FILE, interface=interface)
        process_uploaded_zip_file(file=file, interface=interface)
    except Exception as e:
        interface.log_error("Error %s when uploading file" % str(e))

    return previous_form(interface)


def process_uploaded_zip_file(interface: abstractInterface, file):
    master_data_path = interface.object_store.master_data_path
    temp_filename = os.path.join(download_directory, "tempzipfile.zip")
    file.save(temp_filename)
    temp_dir = os.path.join(download_directory, "temp")
    try:
        os.mkdir(temp_dir)
    except:
        pass
    shutil.unpack_archive(temp_filename, temp_dir)
    shutil.rmtree(master_data_path)
    shutil.copytree(temp_dir, master_data_path, dirs_exist_ok=True)
    shutil.rmtree(temp_dir)
    interface.log_error("Restore backup done")

    ## otherwise backup won't be seen
    interface.flush_cache_to_store()
