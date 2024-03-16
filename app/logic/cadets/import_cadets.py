import os
from typing import Union
from app.data_access.csv.generic_csv_data import write_object

from app.backend.wa_import.load_wa_file import load_raw_wa_file, verify_and_return_uploaded_wa_event_file, WA_FILE, \
    save_uploaded_wa_as_local_file
from app.data_access.configuration.configuration import WILD_APRICOT_FILE_TYPES
from app.logic.cadets.iterate_over_import_cadets_in_uploaded_file import cadet_from_row_in_imported_list, \
    begin_iteration_over_rows_in_temp_cadet_file, temp_list_of_cadets_file_name
from app.objects.abstract_objects.abstract_form import Form, NewForm, fileInput
from app.objects.abstract_objects.abstract_buttons import Button
from app.objects.abstract_objects.abstract_lines import Line, ListOfLines
from app.logic.abstract_logic_api import button_error_and_back_to_initial_state_form
from app.objects.abstract_objects.abstract_interface import (
    abstractInterface,
)
from app.logic.cadets.constants import  BACK_BUTTON_LABEL
from app.objects.cadets import ListOfCadets

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


def create_temp_file_with_list_of_cadets(interface: abstractInterface):
    original_filename = create_local_file_from_uploaded_and_return_filename(interface)
    as_list_of_cadets = read_imported_list_of_cadets(original_filename)
    write_object(as_list_of_cadets, path_and_filename=temp_list_of_cadets_file_name)
    os.remove(original_filename)

def create_local_file_from_uploaded_and_return_filename(interface:abstractInterface)->str:
    original_file = verify_and_return_uploaded_wa_event_file(interface)
    original_filename = save_uploaded_wa_as_local_file(original_file)

    return original_filename

def read_imported_list_of_cadets(filename)-> ListOfCadets:
    data = load_raw_wa_file(filename)
    list_of_cadets = [cadet_from_row_in_imported_list(cadet_row, id) for id, cadet_row in data.iterrows()]

    return ListOfCadets(list_of_cadets)




