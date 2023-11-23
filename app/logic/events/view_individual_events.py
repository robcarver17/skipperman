from typing import Union

from app.data_access.data import data

from app.logic.abstract_form import Form, NewForm, Line, ListOfLines, Button, back_button
from app.logic.abstract_interface import abstractInterface
from app.logic.abstract_logic_api import initial_state_form

from app.logic.events.constants import EVENT
from app.logic.events.constants import WA_IMPORT_BUTTON_LABEL, WA_UPLOAD_BUTTON_LABEL, WA_FIELD_MAPPING_BUTTON_LABEL, WA_UPDATE_BUTTON_LABEL, ALLOCATE_CADETS_BUTTON_LABEL, WA_UPLOAD_SUBSTAGE_IN_VIEW_EVENT_STAGE, WA_IMPORT_SUBSTAGE_IN_VIEW_EVENT_STAGE, WA_UPDATE_SUBSTAGE_IN_VIEW_EVENT_STAGE
from app.logic.events.backend.load_wa_file import does_raw_event_file_exist
from app.logic.events.utilities import get_event_from_state, get_list_of_events
from app.objects.events import Event

def display_form_view_individual_event(
    interface: abstractInterface
) -> Union[Form, NewForm]:
    event_name_selected = interface.last_button_pressed()

    try:
        confirm_event_exists(event_name_selected)
    except:
        interface.log_error("Event %s no longer in list- someone else has deleted or file corruption?"
            % event_name_selected)
        return initial_state_form

    ## so whilst we are in this stage, we know which event we are talking about
    update_state_for_specific_event(
        interface=interface, event_selected=event_name_selected)

    return get_selected_event_form(interface)

def get_selected_event_form(    interface: abstractInterface
) -> Union[Form, NewForm]:

    event = get_event_from_state(interface)
    form = get_event_form_for_event(event, interface=interface)

    return form


def get_event_form_for_event(event: Event, interface: abstractInterface) -> Union[Form, NewForm]:

    event_description = event.verbose_repr
    buttons = get_event_buttons(event, interface=interface)

    lines_in_form = ListOfLines([event_description, buttons])

    return Form(lines_in_form)


def get_event_buttons(event: Event,
                      interface: abstractInterface)-> Line:
    wa_initial_upload = Button(
        WA_UPLOAD_BUTTON_LABEL
    )  ## uploads and creates staging file
    wa_field_mapping = Button(
        WA_FIELD_MAPPING_BUTTON_LABEL
    )  ## does field mapping from staged file
    wa_import = Button(WA_IMPORT_BUTTON_LABEL)  ## does import given a staged file
    wa_update = Button(
        WA_UPDATE_BUTTON_LABEL
    )  ## does upload and import, assuming no staged file

    cadet_allocation = Button(ALLOCATE_CADETS_BUTTON_LABEL)

    wa_import_done = is_wa_mapping_setup_for_event(event=event)
    field_mapping_done = is_wa_field_mapping_setup_for_event(event=event)
    raw_event_file_exists = does_raw_event_file_exist(event.id)

    if not wa_import_done and not field_mapping_done and not raw_event_file_exists:
        return Line([back_button, wa_initial_upload])

    if wa_import_done and not field_mapping_done and not raw_event_file_exists:
        ## something went wrong getting the raw event file, try again
        return Line([back_button, wa_initial_upload])

    if not wa_import_done and field_mapping_done and not raw_event_file_exists:
        ## probably done mapping manually, need to do initial upload
        return Line([back_button, wa_initial_upload])

    if wa_import_done and not field_mapping_done and raw_event_file_exists:
        return Line([back_button, wa_field_mapping])

    if wa_import_done and field_mapping_done and raw_event_file_exists:
        return Line([back_button, wa_import])

    ## both done, we can update the WA file and do cadet allocation
    if wa_import_done and field_mapping_done and not raw_event_file_exists:
        return Line([back_button, wa_update, cadet_allocation])

    interface.log_error(
        "Something went wrong; contact support [wa_import_done=%s, field_mapping_done=%s, raw_event_file_exists=%s]"
        % (str(wa_import_done), str(field_mapping_done), str(raw_event_file_exists))
    )
    return Line([back_button])


def post_form_view_individual_event(interface: abstractInterface) -> Union[Form, NewForm]:
    ## Called by post on view events form, so both stage and event name are set

    last_button_pressed = interface.last_button_pressed()
    if last_button_pressed == WA_UPLOAD_BUTTON_LABEL:
        return NewForm(WA_UPLOAD_SUBSTAGE_IN_VIEW_EVENT_STAGE)

    elif last_button_pressed == WA_FIELD_MAPPING_BUTTON_LABEL:
        interface.log_error("not implemented, have to manually hack .csv")
        return initial_state_form

    elif last_button_pressed == WA_IMPORT_BUTTON_LABEL:
        return NewForm(WA_IMPORT_SUBSTAGE_IN_VIEW_EVENT_STAGE)

    elif last_button_pressed == WA_UPDATE_BUTTON_LABEL:
        return NewForm(WA_UPDATE_SUBSTAGE_IN_VIEW_EVENT_STAGE)

    elif last_button_pressed == ALLOCATE_CADETS_BUTTON_LABEL:
        interface.log_error("not implemented")
        return initial_state_form

    else:
        interface.log_error("Don't recognise button %s" % last_button_pressed)
        return initial_state_form

def confirm_event_exists(event_selected):
    list_of_events = get_list_of_events()
    list_of_events_as_str = [str(event) for event in list_of_events]
    assert event_selected in list_of_events_as_str


def update_state_for_specific_event(
    interface: abstractInterface, event_selected: str
):
    interface.set_persistent_value(EVENT, event_selected)


def row_of_form_for_event_with_buttons(event) -> Line:
    return Line(Button(str(event)))

def is_wa_mapping_setup_for_event(event: Event) -> bool:
    event_id = event.id
    wa_event_mapping = data.data_wa_event_mapping.read()

    event_is_already_in_mapping_list = wa_event_mapping.is_event_in_mapping_list(
        event_id
    )

    return event_is_already_in_mapping_list


def is_wa_field_mapping_setup_for_event(event: Event) -> bool:
    wa_mapping_dict = data.data_wa_field_mapping.read(event.id)
    if len(wa_mapping_dict) == 0:
        return False
    else:
        return True
