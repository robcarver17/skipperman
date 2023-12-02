from typing import Union
from app.logic.events.mapping.read_and_write_mapping_files import (
    get_list_of_templates,
    write_field_mapping_for_event,
    get_template,
    write_template,
    read_mapping_from_csv_file_object,
)
from app.logic.forms_and_interfaces.abstract_interface import (
    abstractInterface,
    get_file_from_interface,
    form_with_message_and_finished_button,
)
from app.logic.forms_and_interfaces.abstract_form import (
    cancel_button,
    Form,
    ListOfLines,
    _______________,
    Line,
    Button,
    NewForm,
    fileInput,
    textInput,
)
from app.logic.events.utilities import get_event_from_state
from app.logic.abstract_logic_api import initial_state_form
from app.logic.events.constants import (
    UPLOAD_TEMPLATE_BUTTON_LABEL,
    WA_UPLOAD_MAPPING_TEMPLATE_IN_VIEW_EVENT_STAGE,
    UPLOAD_FILE_BUTTON_LABEL,
    MAPPING_FILE,
    TEMPLATE_NAME,
    DOWNLOAD_MAPPING_BUTTON_LABEL,
    WA_DOWNLOAD_EVENT_TEMPLATE_MAPPING_IN_VIEW_EVENT_STAGE,
)


def display_form_for_choose_template_field_mapping(interface: abstractInterface):
    list_of_templates_with_buttons = display_list_of_templates_with_buttons()
    if len(list_of_templates_with_buttons) == 0:
        contents_of_form = ListOfLines(
            [
                cancel_button,
                "Click to upload a new template",
                _______________,
                Button(UPLOAD_TEMPLATE_BUTTON_LABEL),
            ]
        )
    else:
        contents_of_form = ListOfLines(
            [
                cancel_button,
                _______________,
                "Choose template to use, or...",
                list_of_templates_with_buttons,
                _______________,
                "... or upload a new one, or...",
                Button(UPLOAD_TEMPLATE_BUTTON_LABEL),
                _______________,
                "... download a template to edit in excel then upload",
                _______________,
                Button(DOWNLOAD_MAPPING_BUTTON_LABEL),
            ]
        )

    return Form(contents_of_form)


def display_list_of_templates_with_buttons() -> ListOfLines:
    list_of_templates = get_list_of_templates()
    return ListOfLines([Button(template_name) for template_name in list_of_templates])


def post_form_for_choose_template_field_mapping(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    last_button_pressed = interface.last_button_pressed()
    if last_button_pressed == UPLOAD_TEMPLATE_BUTTON_LABEL:
        return NewForm(WA_UPLOAD_MAPPING_TEMPLATE_IN_VIEW_EVENT_STAGE)
    elif last_button_pressed == DOWNLOAD_MAPPING_BUTTON_LABEL:
        return NewForm(WA_DOWNLOAD_EVENT_TEMPLATE_MAPPING_IN_VIEW_EVENT_STAGE)
    ## should be a template
    template_name = last_button_pressed

    try:
        mapping = get_template(template_name)
    except Exception as e:
        interface.log_error(
            "Template %s does not exist anymore? error code %s"
            % (template_name, str(e))
        )
        return initial_state_form

    event = get_event_from_state(interface)
    write_field_mapping_for_event(event=event, new_mapping=mapping)

    return form_with_message_and_finished_button(
        "Selected mapping template %s for event %s" % (template_name, str(event)),
        interface=interface,
    )


empty_name = ""


def display_form_for_upload_template_field_mapping(interface: abstractInterface):
    buttons = get_upload_buttons()
    template_name_field = textInput(
        input_name=TEMPLATE_NAME, input_label="Enter template name", value=empty_name
    )
    file_select_field = fileInput(input_label=MAPPING_FILE, accept=".csv")

    list_of_lines = ListOfLines(
        [
            "Choose .csv file to upload as a mapping template, providing template name",
            template_name_field,
            file_select_field,
            buttons,
        ]
    )

    return Form(list_of_lines)


def get_upload_buttons():
    upload = Button(UPLOAD_FILE_BUTTON_LABEL)

    return Line([cancel_button, upload])


def post_form_for_upload_template_field_mapping(interface: abstractInterface):
    template_name = interface.value_from_form(TEMPLATE_NAME)
    if len(template_name) < 4:
        interface.log_error("Template name needs to be longer")
        return initial_state_form
    try:
        file = get_file_from_interface(MAPPING_FILE, interface=interface)
        mapping = read_mapping_from_csv_file_object(file)
    except Exception as e:
        interface.log_error("Something went wrong uploading file %s" % str(e))
        return initial_state_form

    write_template(template_name=template_name, new_mapping=mapping)

    return form_with_message_and_finished_button(
        "Uploaded new template %s" % (template_name), interface=interface
    )
