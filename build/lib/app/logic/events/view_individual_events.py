from typing import Union

from app.backend.volunteers.volunteer_rota_summary import get_summary_list_of_roles_and_groups_for_events
from app.data_access.data import data
from app.backend.wa_import.map_wa_files import is_wa_file_mapping_setup_for_event
from app.backend.group_allocations.summarise_allocations_data import summarise_allocations_for_event
from app.objects.abstract_objects.abstract_form import (
    Form,
    NewForm
)
from app.objects.abstract_objects.abstract_lines import Line, ListOfLines, _______________
from app.objects.abstract_objects.abstract_buttons import BACK_BUTTON_LABEL, Button
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.logic.abstract_logic_api import initial_state_form, button_error_and_back_to_initial_state_form

from app.logic.events.constants import *
from app.backend.wa_import.load_wa_file import does_raw_event_file_exist
from app.logic.events.events_in_state import get_event_from_state
from app.objects.events import Event


def display_form_view_individual_event(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    event = get_event_from_state(interface)
    form = get_event_form_for_event(event, interface=interface)

    return form


def get_event_form_for_event(
    event: Event, interface: abstractInterface
) -> Union[Form, NewForm]:
    event_description = event.details_as_list_of_str()

    if event.contains_groups:
        allocations = summarise_allocations_for_event(event)
        allocations_lines = ListOfLines([        "Group allocations:",
                    _______________,
                    allocations])

    else:
        allocations_lines = ""

    if event.contains_volunteers:
        rota = get_summary_list_of_roles_and_groups_for_events(event)
        rota_lines =   ListOfLines([
                    "Volunteer rota:",
                      _______________,
                      rota])
    else:
        rota_lines = ""

    if event.contains_cadets:
        ## FIXME SUMMARISE CADET NUMBERS
        pass

    if event.contains_food:
        ## FIXME SUMMARISE FOOD NUMBERS
        pass

    if event.contains_clothing:
        ## FIXME SUMMARISE CLOTHING NUMBERS
        pass

    buttons = get_event_buttons(event, interface=interface)

    lines_in_form = (ListOfLines(
                    [
                        ListOfLines(event_description),
                        _______________,
                        buttons,
                        _______________,
                        allocations_lines,
                        rota_lines
]))

    return Form(lines_in_form)



def get_event_buttons(event: Event, interface: abstractInterface) -> Line:
    wa_initial_upload = Button(
        WA_UPLOAD_BUTTON_LABEL
    )  ## uploads and creates staging file
    wa_create_field_mapping = Button(
        WA_FIELD_MAPPING_BUTTON_LABEL
    )  ## does field mapping from staged file
    wa_check_field_mapping = Button(WA_CHECK_FIELD_MAPPING_BUTTON_LABEL)
    wa_modify_field_mapping = Button(WA_MODIFY_FIELD_MAPPING_BUTTON_LABEL)

    wa_import = Button(WA_IMPORT_BUTTON_LABEL)  ## does import_wa given a staged file
    wa_update = Button(
        WA_UPDATE_BUTTON_LABEL
    )  ## does upload and import_wa, assuming no staged file
    back_button = Button(BACK_BUTTON_LABEL)

    wa_import_done = is_wa_file_mapping_setup_for_event(event=event) ## have we done an import already (sets up event mapping)
    field_mapping_done = is_wa_field_mapping_setup_for_event(event=event) ## have set up field mapping
    raw_event_file_exists = does_raw_event_file_exist(event.id) ## is there a staging file waiting to be uploaded


    print(
        "[wa_import_done=%s, field_mapping_done=%s, raw_event_file_exists=%s]"
        % (str(wa_import_done), str(field_mapping_done), str(raw_event_file_exists))
    )

    if not wa_import_done and not field_mapping_done and not raw_event_file_exists:
        return Line([back_button, wa_initial_upload])

    if not wa_import_done and field_mapping_done and not raw_event_file_exists:
        ## probably done mapping manually, need to do initial upload
        return Line([back_button, wa_initial_upload])

    if not wa_import_done and not field_mapping_done and raw_event_file_exists:
        return Line([back_button, wa_create_field_mapping])

    if not wa_import_done and field_mapping_done and raw_event_file_exists:
        return Line([back_button, wa_import, wa_check_field_mapping])

    ## both done, we can update the WA file and do cadet backend / other editing
    if wa_import_done and field_mapping_done and not raw_event_file_exists:
        event_specific_buttons = get_event_specific_buttons(event)
        return Line([back_button, wa_update, wa_modify_field_mapping]+event_specific_buttons )

    interface.log_error(
        "Something went wrong; contact support [wa_import_done=%s, field_mapping_done=%s, raw_event_file_exists=%s]"
        % (str(wa_import_done), str(field_mapping_done), str(raw_event_file_exists))
    )
    return Line([back_button])

def get_event_specific_buttons(event: Event) -> list:
    group_allocation = Button(ALLOCATE_CADETS_BUTTON_LABEL)
    edit_registration = Button(EDIT_CADET_REGISTRATION_DATA_IN_EVENT_BUTTON)
    volunteer_rota = Button(EDIT_VOLUNTEER_ROLES_BUTTON_LABEL)
    event_specific_buttons = []
    if event.contains_cadets:
        event_specific_buttons.append(edit_registration)
    if event.contains_groups:
        event_specific_buttons.append(group_allocation)
    if event.contains_volunteers:
        event_specific_buttons.append(volunteer_rota)
    return event_specific_buttons



def post_form_view_individual_event(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    ## Called by post on view events form, so both stage and event name are set

    last_button_pressed = interface.last_button_pressed()
    if last_button_pressed == WA_UPLOAD_BUTTON_LABEL:
        return NewForm(WA_UPLOAD_SUBSTAGE_IN_VIEW_EVENT_STAGE)

    elif last_button_pressed in [WA_FIELD_MAPPING_BUTTON_LABEL, WA_MODIFY_FIELD_MAPPING_BUTTON_LABEL, WA_CHECK_FIELD_MAPPING_BUTTON_LABEL]:
        ## same form, but contents will be different
        return NewForm(WA_FIELD_MAPPING_IN_VIEW_EVENT_STAGE)

    elif last_button_pressed == WA_IMPORT_BUTTON_LABEL:
        return NewForm(WA_IMPORT_SUBSTAGE_IN_VIEW_EVENT_STAGE)

    elif last_button_pressed == WA_UPDATE_BUTTON_LABEL:
        return NewForm(WA_UPDATE_SUBSTAGE_IN_VIEW_EVENT_STAGE)

    elif last_button_pressed == ALLOCATE_CADETS_BUTTON_LABEL:
        return NewForm(ALLOCATE_CADETS_IN_VIEW_EVENT_STAGE)

    elif last_button_pressed==EDIT_CADET_REGISTRATION_DATA_IN_EVENT_BUTTON:
        return NewForm(EDIT_CADET_REGISTRATION_DATA_IN_VIEW_EVENT_STAGE)
    elif last_button_pressed==EDIT_VOLUNTEER_ROLES_BUTTON_LABEL:
        return NewForm(EDIT_VOLUNTEER_ROTA_EVENT_STAGE)

    elif last_button_pressed == BACK_BUTTON_LABEL:
        return initial_state_form
    else:
        button_error_and_back_to_initial_state_form(interface)


def row_of_form_for_event_with_buttons(event) -> Line:
    return Line(Button(str(event)))


def is_wa_field_mapping_setup_for_event(event: Event) -> bool:
    try:
        wa_mapping_dict = data.data_wa_field_mapping.read(event.id)

        if len(wa_mapping_dict) == 0:
            return False
        else:
            return True
    except:
        return False
