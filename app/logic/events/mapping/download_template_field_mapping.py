from typing import Union
from app.backend.wa_import.read_and_write_mapping_files import (
    get_template,
    write_mapping_to_temp_csv_file_and_return_filename
)
from app.logic.abstract_interface import abstractInterface
from app.logic.events.constants import WA_SELECT_MAPPING_TEMPLATE_IN_VIEW_EVENT_STAGE
from app.objects.abstract_objects.abstract_form import (
    Form,
    File, NewForm, )
from app.objects.abstract_objects.abstract_lines import ListOfLines, _______________
from app.objects.abstract_objects.abstract_buttons import CANCEL_BUTTON_LABEL, Button
from app.logic.abstract_logic_api import initial_state_form
from app.logic.events.mapping.template_field_mapping import (
    display_list_of_templates_with_buttons,
)


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
        return NewForm(WA_SELECT_MAPPING_TEMPLATE_IN_VIEW_EVENT_STAGE)

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
