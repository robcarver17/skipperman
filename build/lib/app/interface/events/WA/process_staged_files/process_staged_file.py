### this is called by WA import_wa or update
from app.web.events.WA.process_staged_files.wa_iteratively_add_cadet_ids import (
    process_rows_of_unmapped_data_and_proceed_to_process_file_with_ids,
)
from app.web.events.WA.utils import (
    delete_staged_file_for_current_event,
    get_event_from_state,
)

from app.web.flask.state_for_action import StateDataForAction

from app.backend.wa_import.load_wa_file import get_staged_file_raw_event_filename
from app.backend.wa_import.map_wa_fields import map_wa_fields_in_df_for_event
from app.backend.wa_import.update_mapped_wa_event_data_with_cadet_ids import (
    update_and_save_mapped_wa_event_data_with_and_without_ids,
)


def process_wa_staged_file_already_uploaded(state_data: StateDataForAction):
    ## First call, will do offline stuff and if required then change state for interactive
    ## no need for exceptions always in try catch
    event = get_event_from_state(state_data)
    filename = get_staged_file_raw_event_filename(event.id)
    print("Working on %s "% filename)
    mapped_wa_event_data = map_wa_fields_in_df_for_event(event=event, filename=filename)
    print("mapped data %s" % mapped_wa_event_data)
    update_and_save_mapped_wa_event_data_with_and_without_ids(
        event=event,
        mapped_wa_event_data=mapped_wa_event_data,
    )
    input("Press enter to continue")
    print("Deleting staging file no longer needed")
    delete_staged_file_for_current_event(state_data)

    return process_rows_of_unmapped_data_and_proceed_to_process_file_with_ids(state_data)
