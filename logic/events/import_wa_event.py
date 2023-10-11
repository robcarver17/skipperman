from logic.data_and_interface import DataAndInterface
from logic.events.choose_event import choose_event
from logic.events.map_wa_fields import map_wa_fields_in_df_for_event
from logic.events.load_wa_file import (
    choose_and_load_raw_wa_file,
    NO_VALID_FILE,
)
from logic.events.map_wa_files import (
    verify_and_if_required_add_wa_mapping,
)
from logic.events.update_mapped_wa_event_data_with_cadet_ids import (
    update_and_save_mapped_wa_event_data_with_cadet_ids,
)
from logic.events.remove_duplicates_from_mapped_wa_event_data import (
    save_with_removed_duplicates_from_mapped_wa_event_data,
)


def import_wa_event_without_checking(
    data_and_interface: DataAndInterface, update_existing: bool
):

    # Step one: Select the event to do the import for (has to be an existing event)
    event = choose_event(
        data_and_interface=data_and_interface, message="Choose event to import from"
    )

    # Step two: Read in the WA file and get the WA id (config of global WA fields)
    wa_as_df = choose_and_load_raw_wa_file(data_and_interface)
    if wa_as_df is NO_VALID_FILE:
        return

    # Step three:
    # FOR NEW EVENTS: Check the WA id doesn't already exist in the list of existing event/WA mappings - if so then point user to update
    # FOR UPDATING: Check WA does exist and matches
    verified_okay = verify_and_if_required_add_wa_mapping(
        data_and_interface=data_and_interface,
        event=event,
        wa_as_df=wa_as_df,
        update_existing=update_existing,
    )
    if not verified_okay:
        return

    ## Step four: Field mapping; put WA data into consistent format
    mapped_wa_event_data = map_wa_fields_in_df_for_event(
        data_and_interface=data_and_interface, event=event, wa_as_df=wa_as_df
    )

    # Step five: Identify cadets, and if required create new cadets; write in cadet ID; save data
    mapped_wa_event_data_with_cadet_ids = (
        update_and_save_mapped_wa_event_data_with_cadet_ids(
            data_and_interface=data_and_interface,
            mapped_wa_event_data=mapped_wa_event_data,
            event=event,
        )
    )

    # Step six: deal with cancellations, duplicates; adding status
    # scanning through the existing event data
    # we always scan the whole WA mapped event, in case of status changes
    save_with_removed_duplicates_from_mapped_wa_event_data(
        data_and_interface=data_and_interface,
        mapped_wa_event_data_with_cadet_ids=mapped_wa_event_data_with_cadet_ids,
        event=event,
    )
