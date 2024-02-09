from typing import Union
from app.backend.data.field_mapping import write_field_mapping_for_event, get_list_of_templates, get_template
from app.logic.abstract_interface import (
    abstractInterface,
    form_with_message_and_finished_button,
)
from app.objects.abstract_objects.abstract_form import (
    Form,
    NewForm,
)
from app.objects.abstract_objects.abstract_buttons import CANCEL_BUTTON_LABEL, Button
from app.objects.abstract_objects.abstract_lines import ListOfLines, _______________
from app.logic.events.events_in_state import get_event_from_state
from app.logic.abstract_logic_api import initial_state_form
from app.logic.events.constants import (
    UPLOAD_TEMPLATE_BUTTON_LABEL,
    WA_UPLOAD_MAPPING_TEMPLATE_IN_VIEW_EVENT_STAGE,
    DOWNLOAD_MAPPING_BUTTON_LABEL,
    WA_DOWNLOAD_EVENT_TEMPLATE_MAPPING_IN_VIEW_EVENT_STAGE, WA_FIELD_MAPPING_IN_VIEW_EVENT_STAGE,

)


def display_form_for_choose_template_field_mapping(interface: abstractInterface):
    list_of_templates_with_buttons = display_list_of_templates_with_buttons()
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
                "Event field mapping - using templates",
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
) -> Union[Form, NewForm]:
    last_button_pressed = interface.last_button_pressed()
    if last_button_pressed == UPLOAD_TEMPLATE_BUTTON_LABEL:
        return NewForm(WA_UPLOAD_MAPPING_TEMPLATE_IN_VIEW_EVENT_STAGE)
    elif last_button_pressed == DOWNLOAD_MAPPING_BUTTON_LABEL:
        return NewForm(WA_DOWNLOAD_EVENT_TEMPLATE_MAPPING_IN_VIEW_EVENT_STAGE)
    elif last_button_pressed == CANCEL_BUTTON_LABEL:
        return NewForm(WA_FIELD_MAPPING_IN_VIEW_EVENT_STAGE)
    else:
        ## should be a template
        return post_form_when_template_chosen(interface)

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
        set_stage_name_to_go_to_on_button_press=WA_FIELD_MAPPING_IN_VIEW_EVENT_STAGE
    )


