from app.logic.events.backend.load_and_save_wa_mapped_events import (
    load_master_event,
    save_master_event,
    load_existing_mapped_wa_event_with_ids
)

from app.objects.master_event import (
    get_row_of_master_event_from_mapped_row_with_idx_and_status, RowInMasterEvent,
)
from app.objects.mapped_wa_event_with_ids import (
    RowInMappedWAEventWithId,
    cancelled_status, active_status, deleted_status, )
from app.logic.cadets.view_cadets import cadet_name_from_id
from app.objects.events import Event
from app.objects.constants import NoMoreData



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

    cadet = cadet_name_from_id(existing_row_in_master_event.cadet_id)

    ## Don't need all options as new_status can't be deleted
    if old_status == cancelled_status and new_status == active_status:
        status_message=\
            "Cadet %s was cancelled; now active so probably new registration" % str(cadet)

    elif old_status == deleted_status and new_status == active_status:
        status_message =\
            "Existing cadet %s data was deleted (missing from event spreadsheet); now active so probably manual editing of WA file has occured" % str(cadet)

    elif old_status == deleted_status and new_status == cancelled_status:
        status_message=\
            "Cadet %s was deleted (missing from event spreadsheet); now cancelled so probably manual editing of WA file has occured" % str(cadet)

    elif old_status == active_status and new_status == cancelled_status:
        status_message=\
            "Cadet %s was active now cancelled, so probably cancelled on WA website" % str(cadet)
    else:
        status_message =\
            "Cadet %s status change from %s to %s, shouldn't happen! Check very carefully" % \
            (str(cadet), old_status_name, new_status_name)

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

