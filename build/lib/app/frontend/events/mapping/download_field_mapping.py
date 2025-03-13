from typing import Union

from app.backend.events.list_of_events import (
    get_list_of_last_N_events,
    get_event_from_id,
)
from app.backend.mapping.list_of_field_mappings import (
    get_field_mapping_template,
    get_list_of_field_mapping_template_names,
    does_event_already_have_mapping,
    get_field_mapping_for_event,
)
from app.backend.mapping.list_of_field_mappings import (
    write_mapping_to_temp_csv_file_and_return_filename,
)
from app.frontend.shared.events_state import get_event_from_state
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_form import (
    Form,
    File,
    NewForm,
)
from app.objects.abstract_objects.abstract_lines import ListOfLines, _______________
from app.objects.abstract_objects.abstract_buttons import (
    cancel_menu_button,
    Button,
    ButtonBar,
    HelpButton,
)
from app.frontend.form_handler import (
    initial_state_form,
    button_error_and_back_to_initial_state_form,
)
from app.objects.events import Event


def display_form_for_download_field_mapping(interface: abstractInterface):

    list_of_templates_with_buttons = display_list_of_templates_with_buttons(interface)
    list_of_events_with_buttons = (
        display_list_of_other_events_with_buttons_except_this_one(interface)
    )
    this_event_button = get_button_for_this_event(interface)

    contents_of_form = ListOfLines(
        [
            ButtonBar([cancel_menu_button, help_button]),
            _______________,
            _______________,
            "Choose mapping to download and edit in excel",
            _______________,
            _______________,
            "Templates:",
            _______________,
            list_of_templates_with_buttons,
            _______________,
            _______________,
            "Existing event mappings",
            _______________,
            list_of_events_with_buttons,
            _______________,
            "Current event",
            this_event_button,
        ]
    )

    return Form(contents_of_form)


def post_form_for_download_field_mapping(
    interface: abstractInterface,
) -> Union[File, Form, NewForm]:
    last_button = interface.last_button_pressed()
    other_event_button_values = get_list_of_other_event_button_values(interface)
    template_button_values = get_list_of_template_button_values(interface)
    this_event_button = get_button_for_this_event(interface)
    print("last button %s" % last_button)

    if cancel_menu_button.pressed(last_button):
        return previous_form(interface)
    elif last_button in other_event_button_values:
        print()
        event_id = get_other_event_id_from_button_value(last_button)
        return download_mapping_another_event(interface=interface, event_id=event_id)
    elif last_button in template_button_values:
        template_name = get_template_name_from_button_value(last_button)
        return download_template(interface=interface, template_name=template_name)
    elif this_event_button.pressed(last_button):
        return download_mapping_this_event(interface)
    else:
        return button_error_and_back_to_initial_state_form(interface)


def download_template(interface: abstractInterface, template_name: str):
    mapping = get_field_mapping_template(
        object_store=interface.object_store, template_name=template_name
    )

    filename = write_mapping_to_temp_csv_file_and_return_filename(
        mapping, filename="Mapping template %s" % template_name
    )
    return File(filename)


def download_mapping_this_event(interface: abstractInterface):
    event = get_event_from_state(interface)
    return download_mapping_generic_event(interface=interface, event=event)


def download_mapping_another_event(interface: abstractInterface, event_id: str):
    event = get_event_from_id(object_store=interface.object_store, event_id=event_id)
    return download_mapping_generic_event(interface=interface, event=event)


def download_mapping_generic_event(interface: abstractInterface, event: Event):
    mapping = get_field_mapping_for_event(
        object_store=interface.object_store, event=event
    )
    filename = write_mapping_to_temp_csv_file_and_return_filename(
        mapping, filename="Mapping for %s" % str(event)
    )
    return File(filename)


def previous_form(interface: abstractInterface):
    return interface.get_new_display_form_for_parent_of_function(
        display_form_for_download_field_mapping
    )


## repeats but avoids circular
def display_list_of_templates_with_buttons(interface: abstractInterface) -> ListOfLines:
    list_of_templates = get_list_of_field_mapping_template_names(
        object_store=interface.object_store
    )
    return ListOfLines(
        [get_button_for_template(template_name) for template_name in list_of_templates]
    )


def display_list_of_other_events_with_buttons_except_this_one(
    interface: abstractInterface,
) -> ListOfLines:
    list_of_events = get_other_events(interface)

    return ListOfLines([get_button_for_other_event(event) for event in list_of_events])


BUTTON_VALUE_THIS_EVENT = "button(**thisevent"


def get_button_for_this_event(interface: abstractInterface):
    event = get_event_from_state(interface)

    existing_field_mapping = does_event_already_have_mapping(
        object_store=interface.object_store, event=event
    )
    if existing_field_mapping:
        return Button(
            label="Current event (%s)" % str(event), value=BUTTON_VALUE_THIS_EVENT
        )
    else:
        return ""


def get_button_for_template(template_name: str):
    return Button(
        label=template_name, value=get_button_value_for_template(template_name)
    )


def get_button_for_other_event(event: Event):
    return Button(label=str(event), value=get_button_value_for_other_event(event))


template_prefix = "template*"


def get_button_value_for_template(template_name: str):
    return template_prefix + template_name


def get_template_name_from_button_value(button_value: str):
    return button_value[len(template_prefix) :]


other_event_prefix = "otherevent*"


def get_button_value_for_other_event(event: Event):
    return other_event_prefix + event.id


def get_other_event_id_from_button_value(button_value: str):
    return button_value[len(other_event_prefix) :]


def get_list_of_template_button_values(interface: abstractInterface):
    list_of_templates = get_list_of_field_mapping_template_names(
        object_store=interface.object_store
    )
    return [
        get_button_value_for_template(template_name)
        for template_name in list_of_templates
    ]


def get_list_of_other_event_button_values(interface: abstractInterface):
    list_of_events = get_other_events(interface)
    return [get_button_value_for_other_event(event) for event in list_of_events]


def get_other_events(interface: abstractInterface):
    event = get_event_from_state(interface)
    return get_list_of_last_N_events(
        object_store=interface.object_store,
        excluding_event=event,
        only_events_before_excluded_event=False,
    )


help_button = HelpButton("WA_create_your_own_mapping_help")
