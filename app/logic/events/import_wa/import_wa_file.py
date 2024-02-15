from typing import Union

from app.objects.abstract_objects.abstract_form import Form, NewForm
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.logic.abstract_logic_api import initial_state_form
from app.logic.events.constants import WA_UPDATE_CONTROLLER_IN_VIEW_EVENT_STAGE
from app.backend.wa_import.load_wa_file import (
    delete_raw_event_upload_with_event_id,
    get_staged_file_raw_event_filename,
)
from app.backend.data.mapped_events import save_mapped_wa_event
from app.backend.wa_import.map_wa_fields import map_wa_fields_in_df_for_event
from app.backend.wa_import.map_wa_files import verify_and_if_required_add_wa_mapping
from app.backend.wa_import.delta_and_mapped_events import (
    create_deltas_of_mapped_event_data, messaging_for_delta_rows,
)
from app.logic.events.events_in_state import get_event_from_state


def display_form_import_event_file(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    return process_wa_staged_file_already_uploaded(interface)
    ## FIX ME
    try:
        ## deletes staged file if works ok
        return process_wa_staged_file_already_uploaded(interface)
    except Exception as e:
        # will have to upload again
        delete_staged_file_for_current_event(interface)
        interface.log_error("Problem with file import_wa %s try uploading again" % e)

        return initial_state_form


def post_form_import_event_file(interface: abstractInterface) -> Union[Form, NewForm]:
    interface.log_error("Shouldn't get to post on import_wa event file!")
    return initial_state_form


def process_wa_staged_file_already_uploaded(interface: abstractInterface) -> NewForm:
    ## First call, will do offline stuff and if required then change state for interactive
    ## no need for exceptions always in try catch
    event = get_event_from_state(interface)
    filename = get_staged_file_raw_event_filename(event.id)
    print("Working on %s " % filename)
    ## add WA mapping
    verify_and_if_required_add_wa_mapping(filename=filename, event=event)

    ## do field mapping
    mapped_wa_event_data = map_wa_fields_in_df_for_event(event=event, filename=filename)
    print("mapped data %s" % mapped_wa_event_data)

    save_mapped_wa_event(mapped_wa_event_data=mapped_wa_event_data, event=event)

    print("Deleting staging file no longer needed")
    delete_staged_file_for_current_event(interface)

    return NewForm(WA_UPDATE_CONTROLLER_IN_VIEW_EVENT_STAGE)



def send_logs_to_interface(list_of_messages: list, interface: abstractInterface):
    for message in list_of_messages:
        interface.log_message(message)

def delete_staged_file_for_current_event(interface: abstractInterface):
    event = get_event_from_state(interface)
    delete_raw_event_upload_with_event_id(event.id)
