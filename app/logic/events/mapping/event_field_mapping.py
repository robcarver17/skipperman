from typing import Union

from app.objects.abstract_objects.abstract_form import (
    Form,
    NewForm,
)
from app.objects.abstract_objects.abstract_tables import PandasDFTable
from app.objects.abstract_objects.abstract_lines import Line, ListOfLines, _______________
from app.objects.abstract_objects.abstract_buttons import BACK_BUTTON_LABEL,  Button

from app.logic.abstract_interface import abstractInterface
from app.logic.abstract_logic_api import button_error_and_back_to_initial_state_form
from app.logic.events.constants import *
from app.logic.events.events_in_state import get_event_from_state
from app.backend.data.field_mapping import get_field_mapping_for_event
from app.backend.wa_import.check_mapping import check_field_mapping
from app.backend.wa_import.map_wa_files import is_wa_file_mapping_setup_for_event
from app.objects.events import Event

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

    pre_existing_text = text_for_pre_existing_mapping(interface)
    check_mapping_lines = check_field_mapping(event)
    warning_text = warning_text_for_mapping(event)

    return Form(ListOfLines(
        [
            "Mapping already set up for %s" % str(event),
            _______________,
            warning_text,
            "Press %s to keep existing, or choose another option to change (see diagnostic information below)" % BACK_BUTTON_LABEL,
            mapping_buttons(),
               _______________,
            "Current field mapping:",
               pre_existing_text,
            _______________,
            check_mapping_lines

        ]

    )
    )

def warning_text_for_mapping(event: Event) -> str:
    wa_import_done = is_wa_file_mapping_setup_for_event(event=event)

    if wa_import_done:
        warning_text = "*WARNING* WA import has already been done for this event. Changing the mapping could break things. DO NOT CHANGE UNLESS YOU ARE SURE."
    else:
        warning_text = ""

    return warning_text


def display_form_event_field_mapping_no_existing_mapping(

) -> Union[Form, NewForm]:

    information = Line(
        "Mapping converts WA field names to our internal field names - we can't import_wa an event without it"
    )


    return Form(ListOfLines([information, _______________, mapping_buttons(), _______________]))

def does_event_already_have_mapping(interface: abstractInterface):
    event = get_event_from_state(interface)
    try:
        mapping = get_field_mapping_for_event(event)
        assert len(mapping)>0
        return True
    except:
        return False


def text_for_pre_existing_mapping(interface: abstractInterface) -> PandasDFTable:
    event = get_event_from_state(interface)
    try:
        mapping = get_field_mapping_for_event(event)
    except:
        return PandasDFTable()

    return PandasDFTable(mapping.to_df())


def mapping_buttons() -> Line:
    return Line(
        [
            Button(BACK_BUTTON_LABEL),
            Button(MAP_TO_TEMPLATE_BUTTON_LABEL),
            Button(CLONE_EVENT_MAPPING_BUTTON_LABEL),
            Button(UPLOAD_MAPPING_BUTTON_LABEL),
        ]
    )


def post_form_event_field_mapping(interface: abstractInterface) -> Union[Form, NewForm]:
    ## Called by post on view events form, so both stage and event name are set

    button_pressed = interface.last_button_pressed()
    if button_pressed == MAP_TO_TEMPLATE_BUTTON_LABEL:
        return NewForm(WA_SELECT_MAPPING_TEMPLATE_IN_VIEW_EVENT_STAGE)
    elif button_pressed == CLONE_EVENT_MAPPING_BUTTON_LABEL:
        return NewForm(WA_CLONE_EVENT_MAPPING_IN_VIEW_EVENT_STAGE)
    elif button_pressed == UPLOAD_MAPPING_BUTTON_LABEL:
        return NewForm(WA_UPLOAD_EVENT_MAPPING_IN_VIEW_EVENT_STAGE)
    elif button_pressed == BACK_BUTTON_LABEL:
        return NewForm(VIEW_EVENT_STAGE)
    else:
        button_error_and_back_to_initial_state_form(interface)