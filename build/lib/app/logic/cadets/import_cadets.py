from typing import Union

from app.backend.wa_import.load_wa_file import WA_FILE
from app.data_access.configuration.configuration import WILD_APRICOT_FILE_TYPES
from app.logic.cadets.iterate_over_import_cadets_in_uploaded_file import begin_iteration_over_rows_in_temp_cadet_file
from app.backend.wa_import.import_cadets import create_temp_file_with_list_of_cadets
from app.objects.abstract_objects.abstract_form import Form, NewForm, fileInput
from app.objects.abstract_objects.abstract_buttons import Button
from app.objects.abstract_objects.abstract_lines import Line, ListOfLines
from app.logic.abstract_logic_api import button_error_and_back_to_initial_state_form
from app.objects.abstract_objects.abstract_interface import (
    abstractInterface,
)
from app.logic.cadets.constants import  BACK_BUTTON_LABEL

UPLOAD_FILE_BUTTON_LABEL = "Upload file"

def display_form_import_cadets(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    prompt="File to upload (for now must have columns: First name	Last name	Date of Birth)"
    buttons = get_upload_buttons()
    input_field = fileInput(input_name=WA_FILE, accept=WILD_APRICOT_FILE_TYPES)

    list_of_lines = ListOfLines([prompt, input_field, buttons])

    return Form(list_of_lines)

def get_upload_buttons():
    upload = Button(UPLOAD_FILE_BUTTON_LABEL)
    back_button = Button(BACK_BUTTON_LABEL)

    return Line([back_button, upload])


def post_form_import_cadets(interface: abstractInterface):

    button_pressed = interface.last_button_pressed()
    ## check button pressed (can only be upload or back - anything else treat as back as must be an error)
    if button_pressed == UPLOAD_FILE_BUTTON_LABEL:
        return respond_to_uploaded_file(interface)
    elif button_pressed == BACK_BUTTON_LABEL:
        return previous_form(interface)
    else:
        button_error_and_back_to_initial_state_form(interface)

def previous_form(interface: abstractInterface) -> NewForm:
    return interface.get_new_display_form_for_parent_of_function(post_form_import_cadets)


def respond_to_uploaded_file(interface: abstractInterface) -> Union[Form, NewForm]:
    create_temp_file_with_list_of_cadets(interface)

    return begin_iteration_over_rows_in_temp_cadet_file(interface)





