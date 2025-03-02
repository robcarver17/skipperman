from typing import Union

from app.backend.events.list_of_events import get_list_of_last_N_events
from app.backend.mapping.list_of_field_mappings import (
    get_field_mapping_template,
    get_list_of_field_mapping_template_names, does_event_already_have_mapping,
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
    get_nav_bar_with_just_cancel_button,
)
from app.frontend.form_handler import initial_state_form
from app.objects.events import Event


def display_form_for_download_field_mapping(interface: abstractInterface):

    list_of_templates_with_buttons = display_list_of_templates_with_buttons(interface)
    list_of_events_with_buttons = display_list_of_other_events_with_buttons_except_this_one(interface)
    this_event_button = get_button_for_this_event(interface)
    contents_of_form = ListOfLines(
        [
            get_nav_bar_with_just_cancel_button(),
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
            this_event_button
        ]
    )

    return Form(contents_of_form)


def post_form_for_download_field_mapping(
    interface: abstractInterface,
) -> Union[File, Form, NewForm]:
    last_button = interface.last_button_pressed()
    other_event_button_values = get_list_of_other_event_button_values(interface)
    template_button_values = get_list_of_template_button_values(interface)
    if cancel_menu_button.pressed():
        return previous_form(interface)
    elif last_button in other_event_button_values:
        pass
    elif last_button in template_button_values:
        pass
    elif last_button == 

def download_template(interface: abstractInterface):
    template_name = pass
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

    filename = write_mapping_to_temp_csv_file_and_return_filename(mapping)
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
    return ListOfLines([get_button_for_template(template_name) for template_name in list_of_templates])



def display_list_of_other_events_with_buttons_except_this_one(interface: abstractInterface) -> ListOfLines:
    list_of_events = get_other_events(interface)

    return ListOfLines([get_button_for_other_event(event) for event in list_of_events])

BUTTON_VALUE_THIS_EVENT = "button(**thisevent"

def get_button_for_this_event(interface: abstractInterface):
    event = get_event_from_state(interface)

    existing_field_mapping = does_event_already_have_mapping(
        object_store=interface.object_store, event=event
    )
    if existing_field_mapping:
        return Button(label="Current event (%s)" % str(event), value=BUTTON_VALUE_THIS_EVENT)
    else:
        return ""

def get_button_for_template(template_name:str):
    return Button(label=template_name, value = get_button_value_for_template(template_name))

def get_button_for_other_event(event: Event):
    return Button(label = str(event), value=get_button_value_for_other_event(event))

template_prefix = "template*"
def get_button_value_for_template(template_name:str):
    return template_prefix+template_name

other_event_prefix = "otherevent*"
def get_button_value_for_other_event(event: Event):
    return other_event_prefix+event.event_name

def get_list_of_template_button_values(interface: abstractInterface):
    list_of_templates = get_list_of_field_mapping_template_names(
        object_store=interface.object_store
    )
    return [get_button_value_for_template(template_name) for template_name in list_of_templates]

def get_list_of_other_event_button_values(interface: abstractInterface):
    list_of_events = get_other_events(interface)
    return [get_button_value_for_other_event(event) for event in list_of_events]

def get_other_events(interface: abstractInterface):
    event = get_event_from_state(interface)
    return get_list_of_last_N_events(
        object_store=interface.object_store,
        excluding_event=event,
        only_events_before_excluded_event=False
    )

