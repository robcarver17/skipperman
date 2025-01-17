from typing import Union
from app.backend.mapping.list_of_field_mappings import (
    get_list_of_field_mapping_template_names,
    get_field_mapping_template,
    save_field_mapping_template,
    save_field_mapping_for_event,
)

from app.frontend.events.mapping.upload_template_field_mapping import (
    display_form_for_upload_template_field_mapping,
)
from app.objects.abstract_objects.abstract_interface import (
    abstractInterface,
    form_with_message_and_finished_button,
)
from app.objects.abstract_objects.abstract_form import (
    Form,
    NewForm,
    File,
)
from app.objects.abstract_objects.abstract_buttons import (
    Button,
    ButtonBar,
    cancel_menu_button,
)
from app.objects.abstract_objects.abstract_lines import ListOfLines, _______________
from app.frontend.shared.events_state import get_event_from_state
from app.frontend.form_handler import initial_state_form

upload_template_button = Button("Upload a new template")


def display_form_for_choose_template_field_mapping(interface: abstractInterface):
    list_of_templates_with_buttons = display_list_of_templates_with_buttons(interface)
    event = get_event_from_state(interface)
    if len(list_of_templates_with_buttons) == 0:
        contents_of_form = ListOfLines(
            [
                "Click to upload a new template for mapping fields",
                _______________,
                upload_template_button,
                cancel_menu_button,
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
                upload_template_button,
                _______________,
                _______________,
                ButtonBar([cancel_menu_button]),
            ]
        )

    return Form(contents_of_form)


def display_list_of_templates_with_buttons(interface: abstractInterface) -> ListOfLines:
    list_of_templates = get_list_of_field_mapping_template_names(interface.object_store)
    return ListOfLines([Button(template_name) for template_name in list_of_templates])


def post_form_for_choose_template_field_mapping(
    interface: abstractInterface,
) -> Union[Form, NewForm, File]:
    last_button_pressed = interface.last_button_pressed()
    if upload_template_button.pressed(last_button_pressed):
        return upload_template_form(interface)

    elif cancel_menu_button.pressed(last_button_pressed):
        return previous_form(interface)
    else:
        ## should be a template
        return post_form_when_template_chosen(interface)


def previous_form(interface: abstractInterface):
    return interface.get_new_display_form_for_parent_of_function(
        display_form_for_choose_template_field_mapping
    )


def upload_template_form(interface: abstractInterface):
    return interface.get_new_form_given_function(
        display_form_for_upload_template_field_mapping
    )


def post_form_when_template_chosen(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    template_name = interface.last_button_pressed()

    try:
        mapping = get_field_mapping_template(
            object_store=interface.object_store, template_name=template_name
        )
    except Exception as e:
        interface.log_error(
            "Template %s does not exist anymore? error code %s"
            % (template_name, str(e))
        )
        return initial_state_form

    event = get_event_from_state(interface)
    save_field_mapping_for_event(
        object_store=interface.object_store, event=event, mapping=mapping
    )
    interface.flush_cache_to_store()

    return form_with_message_and_finished_button(
        "Selected mapping template %s for event %s" % (template_name, str(event)),
        interface=interface,
        function_whose_parent_go_to_on_button_press=display_form_for_choose_template_field_mapping,
    )
