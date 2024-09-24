from typing import Union

from app.frontend.events.mapping.clone_field_mapping import (
    display_form_for_clone_event_field_mapping,
)
from app.frontend.events.mapping.create_mapping import (
    display_form_for_create_custom_field_mapping,
)
from app.frontend.events.mapping.template_field_mapping import (
    display_form_for_choose_template_field_mapping,
)
from app.objects_OLD.abstract_objects.abstract_form import (
    Form,
    NewForm,
)
from app.objects_OLD.abstract_objects.abstract_tables import PandasDFTable
from app.objects.abstract_objects.abstract_lines import (
    Line,
    ListOfLines,
    _______________,
)
from app.objects_OLD.abstract_objects.abstract_buttons import (
    BACK_BUTTON_LABEL,
    Button,
    ButtonBar,
    main_menu_button,
    back_menu_button,
)

from app.objects_OLD.abstract_objects.abstract_interface import abstractInterface
from app.frontend.abstract_logic_api import button_error_and_back_to_initial_state_form
from app.frontend.events.constants import *
from app.frontend.shared.events_state import get_event_from_state
from app.OLD_backend.wa_import.map_wa_fields import get_field_mapping_for_event
from app.OLD_backend.wa_import.check_mapping import check_field_mapping
from app.OLD_backend.wa_import.map_wa_files import is_wa_file_mapping_setup_for_event
from app.objects_OLD.abstract_objects.abstract_text import Heading
from app.objects_OLD.events import Event


def display_form_event_field_mapping(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    existing_mapping = does_event_already_have_mapping(interface)
    if existing_mapping:
        return display_form_event_field_mapping_existing_mapping(interface)
    else:
        return display_form_event_field_mapping_no_existing_mapping()


def display_form_event_field_mapping_existing_mapping(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    event = get_event_from_state(interface)

    pre_existing_text = text_for_pre_existing_mapping(interface=interface, event=event)
    check_mapping_lines = check_field_mapping(interface=interface, event=event)
    warning_text = warning_text_for_mapping(interface=interface, event=event)

    return Form(
        ListOfLines(
            [
                mapping_buttons(),
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
    wa_import_done = is_wa_file_mapping_setup_for_event(
        event=event, interface=interface
    )

    if wa_import_done:
        warning_text = "*WARNING* WA import has already been done for this event. Changing the mapping could break things. DO NOT CHANGE UNLESS YOU ARE SURE."
    else:
        warning_text = ""

    return warning_text


def display_form_event_field_mapping_no_existing_mapping() -> Union[Form, NewForm]:
    information = Line(
        "Mapping converts WA field names to our internal field names - we can't import_wa an event without it"
    )

    return Form(
        ListOfLines([information, _______________, mapping_buttons(), _______________])
    )


def does_event_already_have_mapping(interface: abstractInterface):
    event = get_event_from_state(interface)
    try:
        mapping = get_field_mapping_for_event(interface=interface, event=event)
        assert len(mapping) > 0
        return True
    except:
        return False


def text_for_pre_existing_mapping(
    interface: abstractInterface, event: Event
) -> PandasDFTable:
    try:
        mapping = get_field_mapping_for_event(interface=interface, event=event)
    except:
        return PandasDFTable()

    return PandasDFTable(mapping.as_df_of_str())


def mapping_buttons() -> ButtonBar:
    return ButtonBar(
        [
            main_menu_button,
            back_menu_button,
            Button(MAP_TO_TEMPLATE_BUTTON_LABEL, nav_button=True),
            Button(CLONE_EVENT_MAPPING_BUTTON_LABEL, nav_button=True),
            Button(CREATE_MAPPING_BUTTON_LABEL, nav_button=True),
        ]
    )


def post_form_event_field_mapping(interface: abstractInterface) -> Union[Form, NewForm]:
    ## Called by post on view events form, so both stage and event name are set

    button_pressed = interface.last_button_pressed()
    if button_pressed == MAP_TO_TEMPLATE_BUTTON_LABEL:
        return template_mapping_form(interface)
    elif button_pressed == CLONE_EVENT_MAPPING_BUTTON_LABEL:
        return clone_mapping_form(interface)
    elif button_pressed == BACK_BUTTON_LABEL:
        return previous_form(interface)
    elif button_pressed == CREATE_MAPPING_BUTTON_LABEL:
        return create_mapping_form(interface)
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
