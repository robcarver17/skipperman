import pandas as pd
from app.objects.day_selectors import Day

from app.OLD_backend.group_allocations.group_allocations_data import AllocationData
from app.objects.cadets import ListOfCadets
from app.objects.exceptions import arg_not_passed
from app.data_access.configuration.groups import all_groups_names

## following double up as column headers in df
CADET = "Cadet"
SORT_FIRST_NAME = "First name"
SORT_SECOND_NAME = "Second name"
SORT_GROUP = "Allocated group"
SORT_CLUBBOAT = "Club boat"
SORT_CLASS = "Class"
SORT_PARTNER = "Partner"
DEFAULT_SORT_ORDER = [
    SORT_GROUP,
    SORT_CLUBBOAT,
    SORT_CLASS,
    SORT_PARTNER,
    SORT_FIRST_NAME,
    SORT_SECOND_NAME,
]


def sorted_active_cadets(
    allocation_data: AllocationData,
    day_or_none: Day = None,
    sort_order: list = arg_not_passed,
) -> ListOfCadets:
    if sort_order is arg_not_passed:
        return allocation_data.list_of_cadets_in_event_active_only

    active_cadets_as_data_frame = get_active_cadets_as_data_frame(
        allocation_data=allocation_data, day_or_none=day_or_none
    )

    sorted_active_cadets_df = get_sorted_active_cadets_df(
        active_cadets_as_data_frame, sort_order
    )
    list_of_active_cadets_from_sorted_df = get_list_of_active_cadets_from_sorted_df(
        sorted_active_cadets_df
    )

    return list_of_active_cadets_from_sorted_df


def get_active_cadets_as_data_frame(
    allocation_data: AllocationData, day_or_none: Day = None
) -> pd.DataFrame:
    if day_or_none is None:
        return get_active_cadets_as_data_frame_on_non_specified_day(
            allocation_data=allocation_data
        )
    else:
        return get_active_cadets_as_data_frame_on_specific_day(
            allocation_data=allocation_data, day=day_or_none
        )


def get_active_cadets_as_data_frame_on_non_specified_day(
    allocation_data: AllocationData,
) -> pd.DataFrame:
    active_cadets = allocation_data.list_of_cadets_in_event_active_only
    first_names = [cadet.first_name for cadet in active_cadets]
    surnames = [cadet.surname for cadet in active_cadets]
    groups = [
        allocation_data.get_most_common_group_name_across_days(cadet=cadet)
        for cadet in active_cadets
    ]
    club_boats = [
        allocation_data.get_most_common_club_boat_name_across_days(cadet)
        for cadet in active_cadets
    ]
    boat_classes = [
        allocation_data.get_most_common_boat_class_name_across_days(cadet)
        for cadet in active_cadets
    ]
    partners = [
        allocation_data.get_most_common_partner_name_across_days(cadet)
        for cadet in active_cadets
    ]
    df_as_dict = {
        CADET: active_cadets,
        SORT_FIRST_NAME: first_names,
        SORT_SECOND_NAME: surnames,
        SORT_GROUP: groups,
        SORT_CLUBBOAT: club_boats,
        SORT_CLASS: boat_classes,
        SORT_PARTNER: partners,
    }

    active_cadets_as_data_frame = pd.DataFrame(df_as_dict)
    active_cadets_as_data_frame[SORT_GROUP] = pd.Categorical(
        active_cadets_as_data_frame[SORT_GROUP], all_groups_names
    )

    return active_cadets_as_data_frame


def get_active_cadets_as_data_frame_on_specific_day(
    allocation_data: AllocationData, day: Day
) -> pd.DataFrame:
    active_cadets = allocation_data.list_of_cadets_in_event_active_only
    first_names = [cadet.first_name for cadet in active_cadets]
    surnames = [cadet.surname for cadet in active_cadets]
    groups = [
        allocation_data.get_current_group_name_for_day(cadet=cadet, day=day)
        for cadet in active_cadets
    ]
    club_boats = [
        allocation_data.get_current_club_boat_name_on_day(cadet, day=day)
        for cadet in active_cadets
    ]
    boat_classes = [
        allocation_data.get_name_of_class_of_boat_on_day(cadet, day=day)
        for cadet in active_cadets
    ]
    partners = [
        allocation_data.get_two_handed_partner_as_str_for_cadet_on_day(cadet, day=day)
        for cadet in active_cadets
    ]
    df_as_dict = {
        CADET: active_cadets,
        SORT_FIRST_NAME: first_names,
        SORT_SECOND_NAME: surnames,
        SORT_GROUP: groups,
        SORT_CLUBBOAT: club_boats,
        SORT_CLASS: boat_classes,
        SORT_PARTNER: partners,
    }

    active_cadets_as_data_frame = pd.DataFrame(df_as_dict)
    active_cadets_as_data_frame[SORT_GROUP] = pd.Categorical(
        active_cadets_as_data_frame[SORT_GROUP], all_groups_names
    )

    return active_cadets_as_data_frame


def get_sorted_active_cadets_df(
    active_cadets_as_data_frame: pd.DataFrame, sort_order: list
) -> pd.DataFrame:
    return active_cadets_as_data_frame.sort_values(sort_order)


def get_list_of_active_cadets_from_sorted_df(
    sorted_active_cadets_df: pd.DataFrame,
) -> ListOfCadets:
    return ListOfCadets(sorted_active_cadets_df[CADET].to_list())
