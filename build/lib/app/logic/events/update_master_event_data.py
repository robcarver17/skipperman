from app.web.flask.flash import flash_log
from app.backend.load_and_save_wa_mapped_events import (
    load_master_event,
    save_master_event,
    load_existing_mapped_wa_event_with_ids,
    save_mapped_wa_event_with_ids
)
from app.objects.master_event import (
    MasterEvent, get_row_of_master_event_from_mapped_row_with_idx_and_status, RowInMasterEvent,
)
from app.objects.mapped_wa_event_with_ids import (
    RowInMappedWAEventWithId,
    MappedWAEventWithIDs, cancelled_status, active_status, deleted_status, )
from app.backend.cadets import cadet_name_from_id
from app.objects.events import Event
from app.objects.constants import NoMoreData

def remove_duplicated_row_from_mapped_wa_event_data(event: Event, idx: int):
    mapped_wa_event_data_with_cadet_ids = load_existing_mapped_wa_event_with_ids(event)
    mapped_wa_event_data_with_cadet_ids.pop(idx)
    save_mapped_wa_event_with_ids(mapped_wa_event_data_with_ids=mapped_wa_event_data_with_cadet_ids,
                                  event=event)



def report_on_missing_data_from_mapped_wa_event_data_and_save_to_master_event(
    event: Event,
):
    # load up event with IDs and possible duplicates
    mapped_wa_event_data_with_cadet_ids = load_existing_mapped_wa_event_with_ids(event)

    # will dynamically update this, then save when finished
    master_event = load_master_event(
        event=event
    )

    ## updates wa_event_data_without_duplicates in memory
    report_and_change_status_for_missing_cadets(master_event=master_event,
                                                mapped_wa_event_data_with_cadet_ids=mapped_wa_event_data_with_cadet_ids)

    # Save updated version
    save_master_event(event=event, master_event=master_event)


def report_and_change_status_for_missing_cadets(master_event: MasterEvent,
                                                mapped_wa_event_data_with_cadet_ids: MappedWAEventWithIDs):

    missing_cadet_ids = (
        master_event.cadet_ids_missing_from_new_list(
            mapped_wa_event_data_with_cadet_ids.list_of_cadet_ids
        )
    )

    for cadet_id in missing_cadet_ids:
        cadet_is_already_deleted = (
            master_event.is_cadet_status_deleted(cadet_id)
        )
        if cadet_is_already_deleted:
            continue
        else:
            flash_log(
                "Cadet %s was in WA event data, now appears to be missing from latest file - marked as deleted"
                % cadet_name_from_id(cadet_id)
            )
            master_event.mark_cadet_as_deleted(cadet_id)

    # don't have to return as changed in place

def get_row_from_event_file_with_ids(event: Event, row_idx: int) -> RowInMappedWAEventWithId:
    mapped_wa_event_data_with_cadet_ids = load_existing_mapped_wa_event_with_ids(event)
    try:
        return mapped_wa_event_data_with_cadet_ids[row_idx]
    except IndexError:
        raise NoMoreData



def add_new_row_to_master_event_data(
    event: Event, row_in_mapped_wa_event_with_id: RowInMappedWAEventWithId
):

    row_of_master_event = (
        get_row_of_master_event_from_mapped_row_with_idx_and_status(
            row_in_mapped_wa_event_with_id=row_in_mapped_wa_event_with_id
        )
    )
    print("Adding row %s to master event" % str(row_of_master_event))
    master_event = load_master_event(
        event
    )

    master_event.add_row(row_of_master_event)

    save_master_event(
        event=event, master_event=master_event
    )


NO_STATUS_CHANGE = object()

def new_status_and_status_message(existing_row_in_master_event: RowInMasterEvent,
                                  new_row_in_mapped_wa_event_with_status: RowInMasterEvent)-> tuple:
    old_status = existing_row_in_master_event.status
    new_status = new_row_in_mapped_wa_event_with_status.status

    if old_status==new_status:
        return new_status, NO_STATUS_CHANGE

    old_status_name = old_status.name
    new_status_name = new_status.name

    ## Don't need all options as new_status can't be deleted
    if old_status == cancelled_status and new_status == active_status:
        status_message=\
            "Cadet was cancelled; now active so probably new registration"

    elif old_status == deleted_status and new_status == active_status:
        status_message =\
            "Existing cadet data was deleted (missing from event spreadsheet); now active so probably manual editing of WA file has occured"

    elif old_status == deleted_status and new_status == cancelled_status:
        status_message=\
            "Cadet was deleted (missing from event spreadsheet); now cancelled so probably manual editing of WA file has occured"

    elif old_status == active_status and new_status == cancelled_status:
        status_message=\
            "Cadet %s was active now cancelled, so probably cancelled on WA website"
    else:
        status_message =\
            "Cadet status change from %s to %s, shouldn't happen! Check very carefully" % \
            (old_status_name, new_status_name)

    return new_status,status_message


def update_row_in_master_event_data(
    event: Event, new_row_in_mapped_wa_event_with_status: RowInMasterEvent
):

    master_event = load_master_event(
        event
    )
    print("Updating event %s with existing row new values %s" % (str(event), str(new_row_in_mapped_wa_event_with_status)))

    master_event.update_row(row_of_mapped_wa_event_data_with_id_and_status=new_row_in_mapped_wa_event_with_status)

    save_master_event(
        event=event, master_event=master_event
    )

