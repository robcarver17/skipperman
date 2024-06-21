from typing import Union

from app.backend.wa_import.load_wa_file import WA_FILE
from app.data_access.configuration.configuration import WILD_APRICOT_FILE_TYPES
from app.data_access.configuration.fixed import BACK_KEYBOARD_SHORTCUT
from app.logic.cadets.iterate_over_import_cadets_in_uploaded_file import begin_iteration_over_rows_in_temp_cadet_file
from app.backend.wa_import.import_cadets import create_temp_file_with_list_of_cadets, \
    DESCRIBE_ALL_FIELDS_IN_WA_CADET_LIST_FILE
from app.objects.abstract_objects.abstract_form import Form, NewForm, fileInput
from app.objects.abstract_objects.abstract_buttons import Button, ButtonBar, BACK_BUTTON_LABEL
from app.objects.abstract_objects.abstract_lines import Line, ListOfLines
from app.logic.abstract_logic_api import button_error_and_back_to_initial_state_form
from app.objects.abstract_objects.abstract_interface import (
    abstractInterface,
)

UPLOAD_FILE_BUTTON_LABEL = "Upload file"

def display_form_import_cadets(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    prompt=Line("File to upload (for now must be a csv or xls with following columns: %s)" % DESCRIBE_ALL_FIELDS_IN_WA_CADET_LIST_FILE)
    buttons = get_upload_buttons()
    input_field = Line(fileInput(input_name=WA_FILE, accept=WILD_APRICOT_FILE_TYPES))

    list_of_lines = ListOfLines([prompt, input_field, buttons])

    return Form(list_of_lines)

def get_upload_buttons():
    upload = Button(UPLOAD_FILE_BUTTON_LABEL)
    back_button = Button(BACK_BUTTON_LABEL, shortcut=BACK_KEYBOARD_SHORTCUT)

    return ButtonBar([back_button, upload])


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
    try:
        create_temp_file_with_list_of_cadets(interface)
    except Exception as e:
        interface.log_error("Can't read file so not uploading cadets, error: %s" % str(e))
        return previous_form(interface)

    return begin_iteration_over_rows_in_temp_cadet_file(interface)





