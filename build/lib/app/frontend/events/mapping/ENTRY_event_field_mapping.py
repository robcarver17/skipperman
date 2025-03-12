
from app.backend.registration_data.raw_mapped_registration_data import (
    does_event_have_imported_registration_data,
)

from app.frontend.events.mapping.mapping_table import *
from app.frontend.events.mapping.parse_field_mapping import template_mapping_form, clone_mapping_form, \
    create_mapping_form, add_skipperman_field_to_mapping, add_WA_and_skipperman_field_to_mapping, delete_mapping
from app.objects.abstract_objects.abstract_form import (
    Form,
    NewForm,
)
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
    back_menu_button,
    HelpButton,
)

from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.frontend.form_handler import button_error_and_back_to_initial_state_form
from app.frontend.shared.events_state import get_event_from_state
from app.backend.mapping.list_of_field_mappings import (
    does_event_already_have_mapping,
)
from app.backend.mapping.check_field_mapping import check_field_mapping
from app.objects.abstract_objects.abstract_text import Heading, bold
from app.objects.events import Event


def display_form_event_field_mapping(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    event = get_event_from_state(interface)
    existing_mapping = does_event_already_have_mapping(
        object_store=interface.object_store, event=event
    )
    if existing_mapping:
        return display_form_event_field_mapping_existing_mapping(
            interface=interface, event=event
        )
    else:
        return display_form_event_field_mapping_no_existing_mapping()


def display_form_event_field_mapping_existing_mapping(
    interface: abstractInterface,
    event: Event,
) -> Union[Form, NewForm]:

    mapping_table = get_mapping_table(interface=interface, event=event)
    check_mapping_lines = check_field_mapping(
        object_store=interface.object_store, event=event
    )
    warning_text = warning_text_for_mapping(interface=interface, event=event)
    nav_bar = mapping_buttons()

    return Form(
        ListOfLines(
            [
                nav_bar,
                Heading(
                    "Mapping already set up for %s" % str(event), centred=True, size=4
                ),
                _______________,
                Line(bold(warning_text)),
                Line(
                    "Press %s to keep existing, or modify"
                    % BACK_BUTTON_LABEL
                ),
                _______________,
                "Current field mapping:",
                mapping_table,
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


def display_form_event_field_mapping_no_existing_mapping(
) -> Union[Form, NewForm]:
    information = Line(
        "Mapping converts WA field names to our internal field names - we can't import an event without it"
    )

    return Form(
        ListOfLines(
            [information, _______________, mapping_buttons(), _______________]
        )
    )


def mapping_buttons() -> ButtonBar:

    return ButtonBar(
        [
            main_menu_button,
            back_menu_button,
            map_to_template_button,
            clone_event_button,
            create_mapping_button,
            help_button,
        ]
    )




def post_form_event_field_mapping(interface: abstractInterface) -> Union[Form, NewForm]:
    ## Called by post on view events form, so both stage and event name are set

    delete_buttons = list_of_delete_button_values_in_mapping_table(interface)
    button_pressed = interface.last_button_pressed()

    if map_to_template_button.pressed(button_pressed):
        return template_mapping_form(interface)
    elif clone_event_button.pressed(button_pressed):
        return clone_mapping_form(interface)
    elif create_mapping_button.pressed(button_pressed):
        return create_mapping_form(interface)
    elif back_menu_button.pressed(button_pressed):
        return previous_form(interface)
    elif add_skipperman_field_button.pressed(button_pressed):
        add_skipperman_field_to_mapping(interface)
        return display_form_event_field_mapping(interface)
    elif add_WA_field_button.pressed(button_pressed):
        add_WA_and_skipperman_field_to_mapping(interface)
        return display_form_event_field_mapping(interface)
    elif button_pressed in delete_buttons:
        delete_mapping(interface)
        return display_form_event_field_mapping(interface)
    else:
        button_error_and_back_to_initial_state_form(interface)


def previous_form(interface: abstractInterface) -> NewForm:
    return interface.get_new_display_form_for_parent_of_function(
        display_form_event_field_mapping
    )

MAP_TO_TEMPLATE_BUTTON_LABEL = "Use template mapping"
map_to_template_button = Button(MAP_TO_TEMPLATE_BUTTON_LABEL, nav_button=True)

CLONE_EVENT_MAPPING_BUTTON_LABEL = "Clone the mapping for an existing event"
clone_event_button = Button(CLONE_EVENT_MAPPING_BUTTON_LABEL, nav_button=True)

CREATE_MAPPING_BUTTON_LABEL = "Create your own mapping file"
create_mapping_button = Button(CREATE_MAPPING_BUTTON_LABEL, nav_button=True)

help_button = HelpButton("WA_field_mapping_help")
