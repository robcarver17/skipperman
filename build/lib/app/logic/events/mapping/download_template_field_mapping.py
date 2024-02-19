from typing import Union
from app.backend.data.field_mapping import get_template, write_mapping_to_temp_csv_file_and_return_filename, \
    get_list_of_templates
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_form import (
    Form,
    File, NewForm, )
from app.objects.abstract_objects.abstract_lines import ListOfLines, _______________
from app.objects.abstract_objects.abstract_buttons import CANCEL_BUTTON_LABEL, Button
from app.logic.abstract_logic_api import initial_state_form



def display_form_for_download_template_field_mapping(interface: abstractInterface):
    list_of_templates_with_buttons = display_list_of_templates_with_buttons()
    if len(list_of_templates_with_buttons) == 0:
        interface.log_error("Can't download a template when none uploaded")
        return initial_state_form
    else:
        contents_of_form = ListOfLines(
            [
                cancel_button,
                "Choose template to download and edit in excel",
                _______________,
                list_of_templates_with_buttons,
            ]
        )

    return Form(contents_of_form)

cancel_button = Button(CANCEL_BUTTON_LABEL)

def post_form_for_download_template_field_mapping(
    interface: abstractInterface,
) -> Union[File, Form, NewForm]:
    template_name = interface.last_button_pressed()

    if template_name == CANCEL_BUTTON_LABEL:
        return previous_form(interface)

    try:
        mapping = get_template(template_name)
    except Exception as e:
        interface.log_error(
            "Template %s does not exist anymore? error code %s"
            % (template_name, str(e))
        )
        return initial_state_form

    filename = write_mapping_to_temp_csv_file_and_return_filename(mapping)
    return File(filename)

def previous_form(interface: abstractInterface):
    return interface.get_new_display_form_for_parent_of_function(display_form_for_download_template_field_mapping)


## repeats but avoids circular
def display_list_of_templates_with_buttons() -> ListOfLines:
    list_of_templates = get_list_of_templates()
    return ListOfLines([Button(template_name) for template_name in list_of_templates])
