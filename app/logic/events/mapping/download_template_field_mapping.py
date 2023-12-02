from typing import Union
from app.logic.events.mapping.read_and_write_mapping_files import (
    get_template,
    csv_path_and_filename_for_template,
)
from app.logic.forms_and_interfaces.abstract_interface import abstractInterface
from app.logic.forms_and_interfaces.abstract_form import (
    cancel_button,
    Form,
    ListOfLines,
    _______________,
    File,
)
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


def post_form_for_download_template_field_mapping(
    interface: abstractInterface,
) -> Union[File]:
    template_name = interface.last_button_pressed()

    try:
        mapping = get_template(template_name)
    except Exception as e:
        interface.log_error(
            "Template %s does not exist anymore? error code %s"
            % (template_name, str(e))
        )
        return initial_state_form

    # FIXME: technically should read the mapping file and then write to temp csv file as this assumes data is always stored in csv format
    filename = csv_path_and_filename_for_template(template_name)
    return File(filename)
