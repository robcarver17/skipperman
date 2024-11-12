from typing import Union

from app.backend.registration_data.raw_mapped_registration_data import does_event_have_imported_registration_data

from app.frontend.events.mapping.clone_field_mapping import (
    display_form_for_clone_event_field_mapping,
)
from app.frontend.events.mapping.create_mapping import (
    display_form_for_create_custom_field_mapping
)
from app.frontend.events.mapping.template_field_mapping import (
    display_form_for_choose_template_field_mapping,
)
from app.objects.abstract_objects.abstract_form import (
    Form,
    NewForm,
)
from app.objects.abstract_objects.abstract_tables import PandasDFTable
from app.objects.abstract_objects.abstract_lines import (
    Line,
    ListOfLines,
    _______________,
)
from app.objects.abstract_objects.abstract_buttons import (
    BACK_BUTTON_LABEL,
    Button,
    ButtonBar,
    main_menu_button,
    back_menu_button, HelpButton,
)

from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.frontend.form_handler import button_error_and_back_to_initial_state_form
from app.frontend.shared.events_state import get_event_from_state
from app.backend.mapping.list_of_field_mappings import get_field_mapping_for_event, does_event_already_have_mapping
from app.backend.mapping.check_field_mapping import check_field_mapping
from app.objects.abstract_objects.abstract_text import Heading
from app.objects.events import Event


def display_form_event_field_mapping(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    event = get_event_from_state(interface)
    existing_mapping = does_event_already_have_mapping(object_store=interface.object_store, event=event)
    if existing_mapping:
        return display_form_event_field_mapping_existing_mapping(interface=interface, event=event)
    else:
        return display_form_event_field_mapping_no_existing_mapping(event)


def display_form_event_field_mapping_existing_mapping(
    interface: abstractInterface,
        event: Event,
) -> Union[Form, NewForm]:

    pre_existing_text = text_for_pre_existing_mapping(interface=interface, event=event)
    check_mapping_lines = check_field_mapping(object_store=interface.object_store, event=event)
    warning_text = warning_text_for_mapping(interface=interface, event=event)
    nav_bar = mapping_buttons(event)

    return Form(
        ListOfLines(
            [
                nav_bar,
                Heading(
                    "Mapping already set up for %s" % str(event), centred=True, size=4
                ),
                _______________,
                Heading(warning_text, centred=False, size=6),
                Line(
                    "Press %s to keep existing, or choose another option to change (see diagnostic information below)"
                    % BACK_BUTTON_LABEL
                ),
                _______________,
                "Current field mapping:",
                pre_existing_text,
                _______________,
                check_mapping_lines,
            ]
        )
    )


def warning_text_for_mapping(interface: abstractInterface, event: Event) -> str:
    ## CHANGE TO ANY REGISTRATION DATA
    wa_import_done = does_event_have_imported_registration_data(
        event=event, object_store=interface.object_store
    )

    if wa_import_done:
        warning_text = "*WARNING* Looks like data import has already been done for this event. Changing the mapping could break things. DO NOT CHANGE UNLESS YOU ARE SURE."
    else:
        warning_text = ""

    return warning_text


def display_form_event_field_mapping_no_existing_mapping(event: Event) -> Union[Form, NewForm]:
    information = Line(
        "Mapping converts WA field names to our internal field names - we can't import an event without it"
    )

    return Form(
        ListOfLines([information,
                     _______________,
                     mapping_buttons(event),
                     _______________
                    ])
    )


def text_for_pre_existing_mapping(
    interface: abstractInterface, event: Event
) -> PandasDFTable:

    mapping = get_field_mapping_for_event(object_store=interface.object_store, event=event)

    return PandasDFTable(mapping.as_df_of_str())


def mapping_buttons(event: Event) -> ButtonBar:

    return ButtonBar(
        [
            main_menu_button,
            back_menu_button,
            map_to_template_button,
            clone_event_button,
            create_mapping_button,
            help_button
        ]
    )


MAP_TO_TEMPLATE_BUTTON_LABEL = "Use template mapping"
map_to_template_button = Button(MAP_TO_TEMPLATE_BUTTON_LABEL, nav_button=True)

CLONE_EVENT_MAPPING_BUTTON_LABEL = "Clone the mapping for an existing event"
clone_event_button = Button(CLONE_EVENT_MAPPING_BUTTON_LABEL, nav_button=True)

CREATE_MAPPING_BUTTON_LABEL = "Create your own mapping file"
create_mapping_button = Button(CREATE_MAPPING_BUTTON_LABEL, nav_button=True)

help_button = HelpButton("WA_field_mapping")

def post_form_event_field_mapping(interface: abstractInterface) -> Union[Form, NewForm]:
    ## Called by post on view events form, so both stage and event name are set

    button_pressed = interface.last_button_pressed()
    if map_to_template_button.pressed(button_pressed):
        return template_mapping_form(interface)
    elif clone_event_button.pressed(button_pressed):
        return clone_mapping_form(interface)
    elif create_mapping_button.pressed(button_pressed):
        return create_mapping_form(interface)
    elif back_menu_button.pressed(button_pressed):
        return previous_form(interface)
    else:
        button_error_and_back_to_initial_state_form(interface)


def template_mapping_form(interface: abstractInterface) -> NewForm:
    return interface.get_new_form_given_function(
        display_form_for_choose_template_field_mapping
    )


def clone_mapping_form(interface: abstractInterface) -> NewForm:
    return interface.get_new_form_given_function(
        display_form_for_clone_event_field_mapping
    )


def create_mapping_form(interface: abstractInterface) -> NewForm:
    return interface.get_new_form_given_function(
        display_form_for_create_custom_field_mapping
    )


def previous_form(interface: abstractInterface) -> NewForm:
    return interface.get_new_display_form_for_parent_of_function(
        display_form_event_field_mapping
    )


