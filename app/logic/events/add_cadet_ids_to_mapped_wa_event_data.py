import datetime
from copy import copy
import pandas as pd
from app.data_access.api.generic_api import GenericDataApi
from app.logic import edit_provided_cadet_details
from app.logic.cadets.add_cadet import add_new_verified_cadet
from app.logic.cadets.view_cadets import get_list_of_cadets

from app.objects.mapped_wa_event_no_ids import (
    MappedWAEventNoIDs,
    RowInMappedWAEventNoId,
)
from app.objects.mapped_wa_event_with_ids import MappedWAEventWithIDs
from app.objects.cadets import Cadet, is_cadet_age_surprising
from app.data_access.configuration.configuration import (
    SIMILARITY_LEVEL_TO_WARN_DATE,
    SIMILARITY_LEVEL_TO_WARN_NAME,
)


def add_cadet_ids_to_mapped_wa_event_data(
    data: GenericDataApi, mapped_wa_event_data: MappedWAEventNoIDs
) -> MappedWAEventWithIDs:

    list_of_cadet_ids = [
        get_cadet_id_resolving_possible_duplicates(
            data=data, row_of_mapped_data=row_of_mapped_data
        )
        for row_of_mapped_data in mapped_wa_event_data
    ]

    mapped_wa_event_data_with_cadet_ids = (
        MappedWAEventWithIDs.from_unmapped_event_and_id_list(
            list_of_cadet_ids=list_of_cadet_ids,
            mapped_event_no_ids=mapped_wa_event_data,
        )
    )

    return mapped_wa_event_data_with_cadet_ids


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
