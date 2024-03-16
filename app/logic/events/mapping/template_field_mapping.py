from typing import Union
from app.backend.data.field_mapping import write_field_mapping_for_event, get_list_of_templates, get_template, \
    temp_mapping_file_name
from app.data_access.configuration.field_list_groups import ALL_FIELDS_AS_PD_SERIES
from app.logic.events.mapping.download_template_field_mapping import display_form_for_download_template_field_mapping
from app.logic.events.mapping.upload_template_field_mapping import display_form_for_upload_template_field_mapping
from app.objects.abstract_objects.abstract_interface import (
    abstractInterface,
    form_with_message_and_finished_button,
)
from app.objects.abstract_objects.abstract_form import (
    Form,
    NewForm, File,
)
from app.objects.abstract_objects.abstract_buttons import CANCEL_BUTTON_LABEL, Button
from app.objects.abstract_objects.abstract_lines import ListOfLines, _______________
from app.logic.events.events_in_state import get_event_from_state
from app.logic.abstract_logic_api import initial_state_form

UPLOAD_TEMPLATE_BUTTON_LABEL = "Upload a new template"


def display_form_for_choose_template_field_mapping(interface: abstractInterface):
    list_of_templates_with_buttons = display_list_of_templates_with_buttons()
    event = get_event_from_state(interface)
    if len(list_of_templates_with_buttons) == 0:
        contents_of_form = ListOfLines(
            [
                "Click to upload a new template for mapping fields",
                _______________,
                Button(UPLOAD_TEMPLATE_BUTTON_LABEL),
                cancel_button,
            ]
        )
    else:
        contents_of_form = ListOfLines(
            [
                "Event field mapping - using templates - for event %s" % str(event),
                _______________,
                "Choose template to use, or...",
                list_of_templates_with_buttons,
                _______________,
                "... or upload a new one",
                Button(UPLOAD_TEMPLATE_BUTTON_LABEL),
                _______________,
                cancel_button,
            ]
        )

    return Form(contents_of_form)

cancel_button = Button(CANCEL_BUTTON_LABEL)

def display_list_of_templates_with_buttons() -> ListOfLines:
    list_of_templates = get_list_of_templates()
    return ListOfLines([Button(template_name) for template_name in list_of_templates])


def post_form_for_choose_template_field_mapping(
    interface: abstractInterface,
) -> Union[Form, NewForm, File]:
    last_button_pressed = interface.last_button_pressed()
    if last_button_pressed == UPLOAD_TEMPLATE_BUTTON_LABEL:
        return upload_template_form(interface)

    elif last_button_pressed == CANCEL_BUTTON_LABEL:
        return previous_form(interface)
    else:
        ## should be a template
        return post_form_when_template_chosen(interface)

def previous_form(interface: abstractInterface):
    return interface.get_new_display_form_for_parent_of_function(display_form_for_choose_template_field_mapping)

def upload_template_form(interface: abstractInterface):
    return interface.get_new_form_given_function(display_form_for_upload_template_field_mapping)

def post_form_when_template_chosen(interface: abstractInterface,
) -> Union[Form, NewForm]:
    template_name = interface.last_button_pressed()

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
        function_whose_parent_go_to_on_button_press=display_form_for_choose_template_field_mapping
    )


