from typing import Union

from app.logic.forms_and_interfaces.abstract_form import Form, NewForm
from app.logic.forms_and_interfaces.abstract_interface import abstractInterface
from app.logic.abstract_logic_api import initial_state_form
from app.logic.events.constants import WA_ADD_CADET_IDS_ITERATION_IN_VIEW_EVENT_STAGE
from app.logic.events.backend.load_wa_file import     delete_raw_event_upload_with_event_id,  get_staged_file_raw_event_filename
from app.logic.events.backend.map_wa_fields import map_wa_fields_in_df_for_event
from app.logic.events.backend.map_wa_files import verify_and_if_required_add_wa_mapping
from app.logic.events.backend.update_mapped_wa_event_data_with_cadet_ids import    update_and_save_mapped_wa_event_data_with_and_without_ids
from app.logic.events.utilities import get_event_from_state

def display_form_import_event_file(
    interface: abstractInterface
) -> Union[Form, NewForm]:
    try:
        ## deletes staged file if works ok
        return process_wa_staged_file_already_uploaded(interface)
    except Exception as e:
        # will have to upload again
        delete_staged_file_for_current_event(interface)
        interface.log_error("Problem with file import_wa %s try uploading again" % e)

        return initial_state_form


def post_form_import_event_file(interface: abstractInterface) -> Union[Form, NewForm]:
    ## Called by post on view events form, so both stage and event name are set
    interface.log_error("Shouldn't get to post on import_wa event file!")
    return initial_state_form


def process_wa_staged_file_already_uploaded(interface: abstractInterface) -> NewForm:
    ## First call, will do offline stuff and if required then change state for interactive
    ## no need for exceptions always in try catch
    event = get_event_from_state(interface)
    filename = get_staged_file_raw_event_filename(event.id)
    print("Working on %s "% filename)
    ## add WA mapping
    verify_and_if_required_add_wa_mapping(filename, event=event)

    ## do mapping
    mapped_wa_event_data = map_wa_fields_in_df_for_event(event=event, filename=filename)
    print("mapped data %s" % mapped_wa_event_data)
    update_and_save_mapped_wa_event_data_with_and_without_ids(
        event=event,
        mapped_wa_event_data=mapped_wa_event_data,
    )
    input("Press enter to continue")
    print("Deleting staging file no longer needed")
    delete_staged_file_for_current_event(interface)

    return NewForm(WA_ADD_CADET_IDS_ITERATION_IN_VIEW_EVENT_STAGE)


def delete_staged_file_for_current_event(interface: abstractInterface):
    event = get_event_from_state(interface)
    delete_raw_event_upload_with_event_id(event.id)
