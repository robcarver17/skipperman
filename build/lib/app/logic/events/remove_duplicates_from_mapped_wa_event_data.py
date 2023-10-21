from copy import copy

from app.logic.data import DataAndInterface
from app.logic.events.load_and_save_wa_mapped_events import (
    load_mapped_wa_event_data_without_duplicates,
    save_mapped_wa_event_data_without_duplicates,
)
from app.objects import (
    RowStatus,
    cancelled_status,
    active_status,
    deleted_status,
    RowInMappedWAEventWithIdAndStatus,
    MappedWAEventWithoutDuplicatesAndWithStatus,
    get_row_of_mapped_wa_event_data_with_status,
)
from app.objects import (
    RowInMappedWAEventWithId,
    MappedWAEventWithIDs,
)
from app.objects import DictOfDictDiffs
from app.objects import cadet_name_from_id
from app.objects import Event


def save_with_removed_duplicates_from_mapped_wa_event_data(
    data_and_interface: DataAndInterface,
    mapped_wa_event_data_with_cadet_ids: MappedWAEventWithIDs,
    event: Event,
):
    # will dynamically update this, then save when finished
    wa_event_data_without_duplicates = load_mapped_wa_event_data_without_duplicates(
        data_and_interface=data_and_interface, event=event
    )

    ## updates wa_event_data_without_duplicates in memory
    report_and_change_status_for_missing_cadets(
        data_and_interface=data_and_interface,
        wa_event_data_without_duplicates=wa_event_data_without_duplicates,
        mapped_wa_event_data_with_cadet_ids=mapped_wa_event_data_with_cadet_ids,
    )

    # for loop because wa_event_data_without_duplicates is recursively updated
    # we go from the bottom up, since cancellations are more likely to be underneath
    # actual entries
    for row_in_mapped_wa_event_with_id in reversed(mapped_wa_event_data_with_cadet_ids):
        ## updates wa_event_data_without_duplicates in memory
        add_or_update_row_of_mapped_wa_event_data_with_check_for_duplicate(
            row_in_mapped_wa_event_with_id=row_in_mapped_wa_event_with_id,
            data_and_interface=data_and_interface,
            wa_event_data_without_duplicates=wa_event_data_without_duplicates,
        )

    # Save updated version
    save_mapped_wa_event_data_without_duplicates(
        data_and_interface=data_and_interface,
        event=event,
        wa_event_data_without_duplicates=wa_event_data_without_duplicates,
    )


def report_and_change_status_for_missing_cadets(
    wa_event_data_without_duplicates: MappedWAEventWithoutDuplicatesAndWithStatus,
    data_and_interface: DataAndInterface,
    mapped_wa_event_data_with_cadet_ids: MappedWAEventWithIDs,
):

    missing_cadet_ids = (
        wa_event_data_without_duplicates.cadet_ids_missing_from_new_list(
            mapped_wa_event_data_with_cadet_ids.list_of_cadet_ids
        )
    )

    messenger = data_and_interface.interface.message

    for cadet_id in missing_cadet_ids:
        cadet_is_already_deleted = (
            wa_event_data_without_duplicates.is_cadet_status_deleted(cadet_id)
        )
        if cadet_is_already_deleted:
            continue
        else:
            messenger(
                "Cadet %s was in WA event data, now appears to be deleted"
                % cadet_name_from_id(cadet_id)
            )
            wa_event_data_without_duplicates.mark_cadet_as_deleted(cadet_id)

    # don't have to return as changed in place


def add_or_update_row_of_mapped_wa_event_data_with_check_for_duplicate(
    row_in_mapped_wa_event_with_id: RowInMappedWAEventWithId,
    wa_event_data_without_duplicates: MappedWAEventWithoutDuplicatesAndWithStatus,
    data_and_interface: DataAndInterface,
):

    cadet_id = row_in_mapped_wa_event_with_id.cadet_id
    cadet_already_present = wa_event_data_without_duplicates.is_cadet_id_in_event(
        cadet_id
    )

    if cadet_already_present:
        interactively_update_row_of_mapped_wa_event_data(
            row_in_mapped_wa_event_with_id=row_in_mapped_wa_event_with_id,
            data_and_interface=data_and_interface,
            wa_event_data_without_duplicates=wa_event_data_without_duplicates,
        )

    else:
        # new cadet
        add_new_unique_row_to_mapped_wa_event_data(
            row_in_mapped_wa_event_with_id=row_in_mapped_wa_event_with_id,
            wa_event_data_without_duplicates=wa_event_data_without_duplicates,
        )

    ## updates wa_event_data_without_duplicates in memory no return required


def interactively_update_row_of_mapped_wa_event_data(
    row_in_mapped_wa_event_with_id: RowInMappedWAEventWithId,
    wa_event_data_without_duplicates: MappedWAEventWithoutDuplicatesAndWithStatus,
    data_and_interface: DataAndInterface,
):

    new_row_in_mapped_wa_event_with_status = (
        get_row_of_mapped_wa_event_data_with_status(
            row_in_mapped_wa_event_with_id=row_in_mapped_wa_event_with_id
        )
    )
    existing_row_in_mapped_wa_event_with_status = (
        wa_event_data_without_duplicates.get_row_with_id(
            new_row_in_mapped_wa_event_with_status.cadet_id
        )
    )

    # identify diffs; first STATUS
    # if STATUS diff, then allow user to confirm if the status change happens
    new_row_in_mapped_wa_event_with_status = confirm_status_change_and_return_row(
        new_row_in_mapped_wa_event_with_status=new_row_in_mapped_wa_event_with_status,
        existing_row_in_mapped_wa_event_with_status=existing_row_in_mapped_wa_event_with_status,
        data_and_interface=data_and_interface,
    )

    # other diffs
    new_row_in_mapped_wa_event_with_status = confirm_diffs_and_return_row(
        new_row_in_mapped_wa_event_with_status=new_row_in_mapped_wa_event_with_status,
        existing_row_in_mapped_wa_event_with_status=existing_row_in_mapped_wa_event_with_status,
        data_and_interface=data_and_interface,
    )

    # update row with the new row, possibly modified
    wa_event_data_without_duplicates.update_row(
        row_of_mapped_wa_event_data_with_id_and_status=new_row_in_mapped_wa_event_with_status
    )

    return wa_event_data_without_duplicates


def confirm_status_change_and_return_row(
    new_row_in_mapped_wa_event_with_status: RowInMappedWAEventWithIdAndStatus,
    existing_row_in_mapped_wa_event_with_status: RowInMappedWAEventWithIdAndStatus,
    data_and_interface: DataAndInterface,
) -> RowInMappedWAEventWithIdAndStatus:

    old_status = existing_row_in_mapped_wa_event_with_status.status
    new_status = new_row_in_mapped_wa_event_with_status.status

    if old_status == new_status:
        return new_row_in_mapped_wa_event_with_status

    cadet_name = cadet_name_from_id(
        existing_row_in_mapped_wa_event_with_status.cadet_id
    )

    okay_to_update = status_change_warnings_and_return_true_if_confirmed(
        new_status=new_status,
        old_status=old_status,
        cadet_name=cadet_name,
        data_and_interface=data_and_interface,
    )

    if okay_to_update:
        # keep the status in the new version
        # Code actually doesn't do anything but makes things clearer
        new_row_in_mapped_wa_event_with_status.status = new_status
    else:
        # change the status to the old version
        new_row_in_mapped_wa_event_with_status.status = old_status

    return new_row_in_mapped_wa_event_with_status


def status_change_warnings_and_return_true_if_confirmed(
    new_status: RowStatus,
    old_status: RowStatus,
    cadet_name: str,
    data_and_interface: DataAndInterface,
) -> bool:

    interface = data_and_interface.interface

    old_status_name = old_status.name
    new_status_name = new_status.name

    ## Don't need all options as new_status can't be deleted
    if old_status == cancelled_status and new_status == active_status:
        interface.message(
            "Cadet %s was cancelled; now active so probably new registration"
            % cadet_name
        )

    elif old_status == deleted_status and new_status == active_status:
        interface.message(
            "Cadet %s was deleted (missing from event spreadsheet); now active so probably manual editing of WA file has occured"
            % cadet_name
        )

    elif old_status == deleted_status and new_status == cancelled_status:
        interface.message(
            "Cadet %s was deleted (missing from event spreadsheet); now cancelled so probably manual editing of WA file has occured"
            % cadet_name
        )

    elif old_status == active_status and new_status == cancelled_status:
        interface.message(
            "Cadet %s was active now cancelled, so probably cancelled in WA"
            % cadet_name
        )

    else:
        interface.message(
            "Cadet %s status change from %s to %s, shouldn't happen! Check very carefully"
            % (cadet_name, old_status_name, new_status_name)
        )

    okay_to_update = interface.return_true_if_answer_is_yes(
        "OK to update status for %s from %s to %s?"
        % (cadet_name, old_status_name, new_status_name)
    )

    return okay_to_update


def confirm_diffs_and_return_row(
    new_row_in_mapped_wa_event_with_status: RowInMappedWAEventWithIdAndStatus,
    existing_row_in_mapped_wa_event_with_status: RowInMappedWAEventWithIdAndStatus,
    data_and_interface: DataAndInterface,
) -> RowInMappedWAEventWithIdAndStatus:
    ## IMPORTANT NOTE: at this stage all field names should match, or will throw an exception
    # accept all, keep old one, or edit one by one
    #   edit one by one, choose old, new or type value
    dict_of_dict_diffs = (
        existing_row_in_mapped_wa_event_with_status.dict_of_row_diffs_in_rowdata(
            new_row_in_mapped_wa_event_with_status
        )
    )
    if len(dict_of_dict_diffs) == 0:
        # no change
        return new_row_in_mapped_wa_event_with_status

    new_row_in_mapped_wa_event_with_status = confirm_diffs_and_return_row_when_diffs_exist(
        new_row_in_mapped_wa_event_with_status=new_row_in_mapped_wa_event_with_status,
        existing_row_in_mapped_wa_event_with_status=existing_row_in_mapped_wa_event_with_status,
        dict_of_dict_diffs=dict_of_dict_diffs,
        data_and_interface=data_and_interface,
    )

    return new_row_in_mapped_wa_event_with_status


def confirm_diffs_and_return_row_when_diffs_exist(
    new_row_in_mapped_wa_event_with_status: RowInMappedWAEventWithIdAndStatus,
    existing_row_in_mapped_wa_event_with_status: RowInMappedWAEventWithIdAndStatus,
    dict_of_dict_diffs: DictOfDictDiffs,
    data_and_interface: DataAndInterface,
) -> RowInMappedWAEventWithIdAndStatus:

    interface = data_and_interface.interface
    interface.message(
        "Found differences between existing and new data: %s" % str(dict_of_dict_diffs)
    )
    interface.message("What do you want to do?")

    ## first is default
    options = USE_NEW, KEEP_OLD, CHOOSE = [
        "Use all new",
        "Keep existing data",
        "Choose for each data field",
    ]
    option = interface.get_choice_from_adhoc_menu(options)

    if option == KEEP_OLD:
        new_row_in_mapped_wa_event_with_status = copy(
            existing_row_in_mapped_wa_event_with_status
        )
    elif option == USE_NEW:
        ## new is unchanged
        pass
    elif option == CHOOSE:
        new_row_in_mapped_wa_event_with_status = confirm_diffs_by_choice(
            new_row_in_mapped_wa_event_with_status=new_row_in_mapped_wa_event_with_status,
            dict_of_dict_diffs=dict_of_dict_diffs,
            data_and_interface=data_and_interface,
        )

    return new_row_in_mapped_wa_event_with_status


def confirm_diffs_by_choice(
    new_row_in_mapped_wa_event_with_status: RowInMappedWAEventWithIdAndStatus,
    dict_of_dict_diffs: DictOfDictDiffs,
    data_and_interface: DataAndInterface,
) -> RowInMappedWAEventWithIdAndStatus:
    for key, diff in dict_of_dict_diffs.items():
        interface = data_and_interface.interface
        keep_old = interface.return_true_if_answer_is_yes(
            "For %s keep old %s [YES] or use new %s [NO]"
            % (key, diff.old_value, diff.new_value)
        )
        if keep_old:
            new_row_in_mapped_wa_event_with_status.update_data_in_row(
                key, diff.old_value
            )
        else:
            ## no change needed
            pass

    return new_row_in_mapped_wa_event_with_status


def add_new_unique_row_to_mapped_wa_event_data(
    row_in_mapped_wa_event_with_id: RowInMappedWAEventWithId,
    wa_event_data_without_duplicates: MappedWAEventWithoutDuplicatesAndWithStatus,
):

    row_of_mapped_wa_event_data_with_status = (
        get_row_of_mapped_wa_event_data_with_status(
            row_in_mapped_wa_event_with_id=row_in_mapped_wa_event_with_id
        )
    )
    wa_event_data_without_duplicates.add_row(row_of_mapped_wa_event_data_with_status)

    ## updates wa_event_data_without_duplicates in memory no return required
