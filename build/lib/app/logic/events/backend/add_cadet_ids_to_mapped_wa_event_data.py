import datetime
import pandas as pd

# from app.logic import_wa edit_provided_cadet_details
from app.logic.events.backend.load_and_save_wa_mapped_events import (
    load_mapped_wa_event_with_no_ids,
    save_mapped_wa_event_with_no_ids,
)
from app.objects.cadets import Cadet
from app.objects.field_list import CADET_SURNAME, CADET_DATE_OF_BIRTH, CADET_FIRST_NAME
from app.objects.constants import NoMoreData

from app.logic.events.backend.load_and_save_wa_mapped_events import (
    load_existing_mapped_wa_event_with_ids,
    save_mapped_wa_event_with_ids,
)
from app.objects.mapped_wa_event_with_ids import (
    MappedWAEventWithIDs,
    RowInMappedWAEventWithId,
    RowInMappedWAEventNoId,
)
from app.objects.events import Event


FIRST_ROW_INDEX = 0


def get_first_unmapped_row_for_event(event: Event):
    all_unmapped_rows = load_unmapped_rows_for_event(event)
    if len(all_unmapped_rows) == 0:
        raise NoMoreData()
    return all_unmapped_rows[FIRST_ROW_INDEX]


def load_unmapped_rows_for_event(event: Event):
    return load_mapped_wa_event_with_no_ids(event)


def get_cadet_data_from_row_of_mapped_data_no_checks(
    row_of_mapped_data: RowInMappedWAEventNoId,
) -> Cadet:
    first_name = row_of_mapped_data[CADET_FIRST_NAME]
    second_name = row_of_mapped_data[CADET_SURNAME]
    dob = row_of_mapped_data[CADET_DATE_OF_BIRTH]
    dob_as_date = _translate_df_timestamp_to_datetime(dob)

    return Cadet(first_name=first_name.strip(), surname=second_name.strip(), date_of_birth=dob_as_date)


def _translate_df_timestamp_to_datetime(df_timestamp) -> datetime.date:
    if type(df_timestamp) is datetime.date:
        return df_timestamp

    if type(df_timestamp) is pd._libs.tslibs.timestamps.Timestamp:
        return df_timestamp.date()

    if type(df_timestamp) is str:
        return datetime.datetime.strptime(df_timestamp, "")

    raise Exception(
        "Can't handle timestamp %s with type %s"
        % (str(df_timestamp), str(type(df_timestamp)))
    )


def add_row_data_with_id_included_and_delete_from_unmapped_data(
    event: Event, new_row: RowInMappedWAEventNoId, cadet_id: str
):
    new_row_with_cadet_id = RowInMappedWAEventWithId(
        cadet_id=cadet_id, data_in_row=new_row
    )
    existing_mapped_wa_event_with_ids = load_existing_mapped_wa_event_with_ids(
        event=event
    )

    new_row_as_list = MappedWAEventWithIDs([new_row_with_cadet_id])
    existing_mapped_wa_event_with_ids.add_new_rows(new_row_as_list)

    delete_first_unmapped_row_for_event(event)
    save_mapped_wa_event_with_ids(
        mapped_wa_event_data_with_ids=existing_mapped_wa_event_with_ids, event=event
    )


def delete_first_unmapped_row_for_event(event: Event):
    all_unmapped_rows = load_unmapped_rows_for_event(event)
    if len(all_unmapped_rows) == 0:
        raise NoMoreData()
    all_unmapped_rows.pop(FIRST_ROW_INDEX)
    save_mapped_wa_event_with_no_ids(
        event=event, mapped_wa_event_data_with_no_ids=all_unmapped_rows
    )


"""

def get_cadet_id_resolving_possible_duplicates(
    data_and_interface: DataAndInterface, row_of_mapped_data: RowInMappedWAEventNoId
) -> str:
    cadet_from_mapped_data = get_cadet_data_from_row_of_mapped_data_with_age_checks(
        row_of_mapped_data=row_of_mapped_data, data_and_interface=data_and_interface
    )

    cadet_to_use = check_for_possible_duplicate_cadet_or_add_if_required(
        data_and_interface=data_and_interface,
        cadet_from_mapped_data=cadet_from_mapped_data,
    )

    return cadet_to_use.id


def get_cadet_data_from_row_of_mapped_data_with_age_checks(
    data_and_interface: DataAndInterface, row_of_mapped_data: RowInMappedWAEventNoId
) -> Cadet:
    cadet = get_cadet_data_from_row_of_mapped_data_no_checks(row_of_mapped_data)
    surprising_age = is_cadet_age_surprising(cadet)
    if surprising_age:
        data_and_interface.interface.message(
            "Cadet %s is surprisingly old or young, are you sure their DOB is correct?"
            % str(cadet)
        )
        cadet = edit_provided_cadet_details(
            cadet=cadet,
            data_and_interface=data_and_interface,
            edit_dob=True,
            edit_surname=False,
            edit_firstname=False,
        )
        # note this won't change the WA dataframe of cadet DOB but once ID mapped this isn't used

    return cadet


def get_cadet_data_from_row_of_mapped_data_no_checks(
    row_of_mapped_data: RowInMappedWAEventNoId,
) -> Cadet:
    first_name = row_of_mapped_data[CADET_FIRST_NAME]
    second_name = row_of_mapped_data[CADET_SURNAME]
    dob = row_of_mapped_data[CADET_DATE_OF_BIRTH]
    dob_as_date = _translate_df_timestamp_to_datetime(dob)

    return Cadet(first_name=first_name, surname=second_name, date_of_birth=dob_as_date)


def _translate_df_timestamp_to_datetime(df_timestamp) -> datetime.date:
    if type(df_timestamp) is datetime.date:
        return df_timestamp

    if type(df_timestamp) is pd._libs.tslibs.timestamps.Timestamp:
        return df_timestamp.date()

    if type(df_timestamp) is str:
        return datetime.datetime.strptime(df_timestamp, "")

    raise Exception(
        "Can't handle timestamp %s with type %s"
        % (str(df_timestamp), str(type(df_timestamp)))
    )


def check_for_possible_duplicate_cadet_or_add_if_required(
    data_and_interface: DataAndInterface, cadet_from_mapped_data: Cadet
) -> Cadet:

    interface = data_and_interface.interface
    similarity_threshold_to_warn_age = copy(SIMILARITY_LEVEL_TO_WARN_AGE)
    similarity_threshold_to_warn_name = copy(SIMILARITY_LEVEL_TO_WARN_NAME)

    existing_cadets = load_master_list_of_cadets(data_and_interface=data_and_interface)
    if cadet_from_mapped_data in existing_cadets:
        ## Already in, and perfect match
        return cadet_from_mapped_data

    unmatched = True
    while unmatched:
        similar_cadets = existing_cadets.similar_cadets(
            cadet_from_mapped_data,
            name_threshold=similarity_threshold_to_warn_name,
            dob_threshold=similarity_threshold_to_warn_age,
        )

        if len(similar_cadets) > 0:
            ## Some similar cadets, let's see if it's a match
            interface.message(
                "Looks like cadet %s is very similar to some existing cadets. \n Select an existing cadet [options 1... upwards], or choose the cadet from the WA file [0] if this cadet is not in the list shown and is really new."
                % cadet_from_mapped_data
            )
            similar_cadets.insert(0, cadet_from_mapped_data)
            chosen_cadet = interface.get_choice_from_adhoc_menu(similar_cadets)
            chosen_an_existing_cadet = not chosen_cadet == cadet_from_mapped_data

            if chosen_an_existing_cadet:
                return chosen_cadet
        else:
            interface.message("Cadet %s appears to be new" % cadet_from_mapped_data)

        ## Must be new
        add_cadet = interface.return_true_if_answer_is_yes(
            "Add %s to the master list as a new cadet? Say no to see more potential duplicates."
            % cadet_from_mapped_data
        )
        if add_cadet:
            ## Really new let's add it
            # can always edit master list later (menu option)
            add_new_cadet_to_master_list(
                data_and_interface=data_and_interface, cadet=cadet_from_mapped_data
            )
            return cadet_from_mapped_data
        else:
            interface.message(
                "You have chosen not to add cadet %s, checking again to see if an existing cadet looks similar"
                % cadet_from_mapped_data
            )
            ## lower threshold to bring more into the mix
            similarity_threshold_to_warn_age = similarity_threshold_to_warn_age * 0.9
            similarity_threshold_to_warn_name = similarity_threshold_to_warn_name * 0.9
            continue
"""
