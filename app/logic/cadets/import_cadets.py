from typing import Union

from app.backend.wa_import.load_wa_file import WA_FILE
from app.data_access.configuration.configuration import WILD_APRICOT_FILE_TYPES
from app.logic.cadets.iterate_over_import_cadets_in_uploaded_file import (
    begin_iteration_over_rows_in_temp_cadet_file,
)
from app.backend.wa_import.import_cadets import (
    create_temp_file_with_list_of_cadets,
    DESCRIBE_ALL_FIELDS_IN_WA_CADET_LIST_FILE,
)
from app.objects.abstract_objects.abstract_form import Form, NewForm, fileInput
from app.objects.abstract_objects.abstract_buttons import (
    Button,
    ButtonBar,
    back_menu_button,
)
from app.objects.abstract_objects.abstract_lines import Line, ListOfLines
from app.logic.abstract_logic_api import button_error_and_back_to_initial_state_form
from app.objects.abstract_objects.abstract_interface import (
    abstractInterface,
)

UPLOAD_FILE_BUTTON_LABEL = "Upload file"


def display_form_import_cadets(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    prompt = Line(
        "File to upload (for now must be a csv or xls with following columns: %s)"
        % DESCRIBE_ALL_FIELDS_IN_WA_CADET_LIST_FILE
    )
    buttons = ButtonBar([back_menu_button, upload_button])
    input_field = Line(fileInput(input_name=WA_FILE, accept=WILD_APRICOT_FILE_TYPES))

    list_of_lines = ListOfLines([prompt, input_field, buttons])

    return Form(list_of_lines)


upload_button = Button(UPLOAD_FILE_BUTTON_LABEL, nav_button=True)


def post_form_import_cadets(interface: abstractInterface):
    button_pressed = interface.last_button_pressed()
    ## check button pressed (can only be upload or back - anything else treat as back as must be an error)
    if upload_button.pressed(button_pressed):
        return respond_to_uploaded_file(interface)
    elif back_menu_button.pressed(button_pressed):
        return previous_form(interface)
    else:
        button_error_and_back_to_initial_state_form(interface)


def previous_form(interface: abstractInterface) -> NewForm:
    return interface.get_new_display_form_for_parent_of_function(
        post_form_import_cadets
    )


def respond_to_uploaded_file(interface: abstractInterface) -> Union[Form, NewForm]:
    try:
        create_temp_file_with_list_of_cadets(interface)
    except Exception as e:
        interface.log_error(
            "Can't read file so not uploading cadets, error: %s" % str(e)
        )
        return previous_form(interface)

    return begin_iteration_over_rows_in_temp_cadet_file(interface)
