from typing import Union

from app.logic.abstract_form import Form, NewForm, Line, ListOfLines, Button, back_button, _______________, Table
from app.logic.abstract_interface import abstractInterface
from app.logic.abstract_logic_api import initial_state_form
from app.logic.events.constants import *
from app.logic.events.utilities import get_event_from_state
from app.logic.events.mapping.read_and_write_mapping_files import get_field_mapping_for_event

def display_form_event_field_mapping(
    interface: abstractInterface
) -> Union[Form, NewForm]:
    pre_existing = text_for_pre_existing_mapping(interface)
    if len(pre_existing)==0:
        pre_existing = Line("Mapping converts WA field names to our internal field names - we can't import_wa an event without it")
    else:
        pre_existing = ListOfLines([
            "Mapping already set up:",
            _______________,
            pre_existing,
            _______________,
            ".... press %s to keep existing, or continue to change" % back_button.label
        ])
    return Form(
        ListOfLines([
            pre_existing,
            _______________,
            mapping_buttons()
            ]
        )
    )

def text_for_pre_existing_mapping(interface: abstractInterface) -> Table:
    event = get_event_from_state(interface)
    try:
        mapping = get_field_mapping_for_event(event)
    except:
        return Table()

    return Table(mapping.to_df())


def mapping_buttons() -> Line:
    return Line([
        back_button,
        Button(MAP_TO_TEMPLATE),
        Button(CLONE_EVENT_BUTTON_LABEL),
        Button(UPLOAD_MAPPING)
    ])


def post_form_event_field_mapping(interface: abstractInterface) -> Union[Form, NewForm]:
    ## Called by post on view events form, so both stage and event name are set

    button_pressed = interface.last_button_pressed()
    if button_pressed==MAP_TO_TEMPLATE:
        return NewForm(WA_SELECT_MAPPING_TEMPLATE_IN_VIEW_EVENT_STAGE)
    elif button_pressed==CLONE_EVENT_BUTTON_LABEL:
        return NewForm(WA_CLONE_EVENT_MAPPING_IN_VIEW_EVENT_STAGE)
    elif button_pressed==UPLOAD_MAPPING:
        return NewForm(WA_UPLOAD_EVENT_MAPPING_IN_VIEW_EVENT_STAGE)
    else:
        interface.log_error("Button %s not recognised" % button_pressed)
        return initial_state_form


