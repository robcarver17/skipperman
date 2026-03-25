from copy import copy
from dataclasses import dataclass
from typing import List

import pandas as pd

from app.backend.boat_classes.list_of_boat_classes import get_list_of_boat_classes
from app.backend.club_boats.list_of_club_dinghies import get_list_of_club_dinghies
from app.backend.groups.list_of_groups import get_list_of_groups
from app.data_access.store.object_store import ObjectStore
from app.objects.cadets import ListOfCadets, Cadet, NO_CADET_ID
from app.objects.day_selectors import Day
from app.objects.utilities.exceptions import arg_not_passed
from app.objects.composed.cadets_with_all_event_info import DictOfAllEventInfoForCadets


CADET = "Cadet"
SORT_FIRST_NAME = "First name"
SORT_SECOND_NAME = "Second name"
SORT_GROUP = "Allocated group"
SORT_CLUBBOAT = "Club boat"
SORT_CLASS = "Class"
SORT_PARTNER = "Partner"
DEFAULT_SORT_ORDER_LIST = [
    SORT_GROUP,
    SORT_CLUBBOAT,
    SORT_CLASS,
    SORT_FIRST_NAME,
    SORT_SECOND_NAME,
]


@dataclass
class SortOrderGroups:
    sort_order_as_list: List[str]
    keep_pairs_together: bool

    def sort_order(self):
        if self.keep_pairs_together:
            new_list = copy(self.sort_order_as_list)
            new_list.insert(0, SORT_PARTNER)
            return new_list
        else:
            return self.sort_order_as_list


DEFAULT_SORT_ORDER = SortOrderGroups(DEFAULT_SORT_ORDER_LIST, keep_pairs_together=True)

dict_of_id_and_sort = {
    2: SORT_FIRST_NAME,
    3: SORT_SECOND_NAME,
    4: SORT_GROUP,
    5: SORT_CLUBBOAT,
    6: SORT_CLASS,
}
reverse_id_and_sort_dict = dict(
    [(value, key) for key, value in dict_of_id_and_sort.items()]
)


def from_id_to_sort_name(id: int):
    return dict_of_id_and_sort[id]


def from_sort_to_id(sort_name: str):
    return reverse_id_and_sort_dict[sort_name]


def from_sort_list_to_string(sort_order: SortOrderGroups):
    sort_list = sort_order.sort_order_as_list
    keep_pairs_together = sort_order.keep_pairs_together
    as_int = [str(from_sort_to_id(sort_name)) for sort_name in sort_list]
    as_int = [str(bool2int(keep_pairs_together))] + as_int
    return "".join(as_int)


from app.objects.utilities.transform_data import bool2int, int2bool


def from_string_to_sort_list(sort_list_as_str: str) -> SortOrderGroups:
    ids_as_list = list(sort_list_as_str)
    keep_pairs_together = int2bool(int(ids_as_list.pop(0)))
    sort_order_as_list = [from_id_to_sort_name(int(id)) for id in ids_as_list]

    return SortOrderGroups(
        sort_order_as_list=sort_order_as_list, keep_pairs_together=keep_pairs_together
    )


def sorted_active_cadets(
    object_store: ObjectStore,
    dict_of_all_event_data: DictOfAllEventInfoForCadets,
    day_or_none: Day = None,
    sort_order: SortOrderGroups = arg_not_passed,
) -> ListOfCadets:
    if sort_order is arg_not_passed:
        return dict_of_all_event_data.list_of_cadets

    active_cadets_as_data_frame = get_active_cadets_as_data_frame(
        dict_of_all_event_data=dict_of_all_event_data,
        object_store=object_store,
        day_or_none=day_or_none,
    )

    sorted_active_cadets_df = get_sorted_active_cadets_df(
        active_cadets_as_data_frame, sort_order=sort_order
    )
    list_of_active_cadets_from_sorted_df = get_list_of_active_cadets_from_sorted_df(
        sorted_active_cadets_df
    )

    return list_of_active_cadets_from_sorted_df


def get_active_cadets_as_data_frame(
    object_store: ObjectStore,
    dict_of_all_event_data: DictOfAllEventInfoForCadets,
    day_or_none: Day = None,
) -> pd.DataFrame:
    if day_or_none is None:
        return get_active_cadets_as_data_frame_on_non_specified_day(
            object_store=object_store, dict_of_all_event_data=dict_of_all_event_data
        )
    else:
        return get_active_cadets_as_data_frame_on_specific_day(
            object_store=object_store,
            dict_of_all_event_data=dict_of_all_event_data,
            day=day_or_none,
        )


def get_active_cadets_as_data_frame_on_non_specified_day(
    dict_of_all_event_data: DictOfAllEventInfoForCadets,
    object_store: ObjectStore,
) -> pd.DataFrame:
    active_cadets = dict_of_all_event_data.list_of_cadets
    first_names = [cadet.first_name for cadet in active_cadets]
    surnames = [cadet.surname for cadet in active_cadets]
    groups = [
        dict_of_all_event_data.get_most_common_group_name_across_days(cadet=cadet)
        for cadet in active_cadets
    ]
    club_boats = [
        dict_of_all_event_data.get_most_common_club_boat_name_across_days(cadet)
        for cadet in active_cadets
    ]
    boat_classes = [
        dict_of_all_event_data.get_most_common_boat_class_name_across_days(cadet)
        for cadet in active_cadets
    ]
    list_of_partner_ids = [
        dict_of_all_event_data.get_most_common_partner_id_across_days(
            cadet, default=NO_CADET_ID
        )
        for cadet in active_cadets
    ]
    partners = from_list_of_partners_to_list_of_nominal_codes(
        list_of_partner_ids=list_of_partner_ids,
        list_of_cadet_ids=active_cadets.list_of_ids,
    )

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

    active_cadets_as_data_frame = add_sort_order_to_data_frame(
        object_store=object_store,
        active_cadets_as_data_frame=active_cadets_as_data_frame,
    )

    return active_cadets_as_data_frame


NO_PARTNER = 0
STARTING_CODE = 1


def from_list_of_partners_to_list_of_nominal_codes(
    list_of_cadet_ids: List[str], list_of_partner_ids: List[str]
) -> List[int]:
    list_of_codes = [NO_PARTNER] * len(list_of_partner_ids)
    boat_number = STARTING_CODE
    for idx, partner_id in enumerate(list_of_partner_ids):
        if partner_id == NO_CADET_ID:
            continue

        partner_idx_in_cadets = list_of_cadet_ids.index(partner_id)
        boat_code = list_of_codes[partner_idx_in_cadets]
        if boat_code == NO_PARTNER:
            boat_code_to_use = copy(boat_number)
            boat_number += 1
            list_of_codes[partner_idx_in_cadets] = boat_code_to_use
            list_of_codes[idx] = boat_code_to_use
        else:
            list_of_codes[idx] = boat_code

    return list_of_codes


def get_active_cadets_as_data_frame_on_specific_day(
    object_store: ObjectStore,
    dict_of_all_event_data: DictOfAllEventInfoForCadets,
    day: Day,
) -> pd.DataFrame:
    active_cadets = dict_of_all_event_data.list_of_cadets
    first_names = [cadet.first_name for cadet in active_cadets]
    surnames = [cadet.surname for cadet in active_cadets]
    groups = [
        dict_of_all_event_data.event_data_for_cadet(cadet)
        .days_and_groups.group_on_day(day)
        .name
        for cadet in active_cadets
    ]
    club_boats = [
        dict_of_all_event_data.event_data_for_cadet(cadet)
        .days_and_club_dinghies.dinghy_on_day(day)
        .name
        for cadet in active_cadets
    ]
    boat_classes = [
        dict_of_all_event_data.event_data_for_cadet(cadet)
        .days_and_boat_class.boat_class_on_day(day)
        .name
        for cadet in active_cadets
    ]
    list_of_partner_ids = [
        dict_of_all_event_data.event_data_for_cadet(
            cadet
        ).days_and_boat_class.partner_id_on_day(day, default=NO_CADET_ID)
        for cadet in active_cadets
    ]
    partners = from_list_of_partners_to_list_of_nominal_codes(
        list_of_cadet_ids=active_cadets.list_of_ids,
        list_of_partner_ids=list_of_partner_ids,
    )

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

    active_cadets_as_data_frame = add_sort_order_to_data_frame(
        object_store=object_store,
        active_cadets_as_data_frame=active_cadets_as_data_frame,
    )

    return active_cadets_as_data_frame


def add_sort_order_to_data_frame(
    object_store: ObjectStore, active_cadets_as_data_frame: pd.DataFrame
):
    if len(active_cadets_as_data_frame) == 0:
        return active_cadets_as_data_frame

    ## this ensures the groups, boat classes and club boats are sorted in order
    list_of_groups = get_list_of_groups(object_store).list_of_names()
    list_of_groups = remove_empty_values(list_of_groups)

    active_cadets_as_data_frame[SORT_GROUP] = pd.Categorical(
        active_cadets_as_data_frame[SORT_GROUP],
        list_of_groups,
    )

    list_of_club_dinghies = get_list_of_club_dinghies(object_store).list_of_names()
    list_of_club_dinghies = remove_empty_values(
        list_of_club_dinghies
    )  ## there is a weird bug but this ensures it won't affect us

    active_cadets_as_data_frame[SORT_CLUBBOAT] = pd.Categorical(
        active_cadets_as_data_frame[SORT_CLUBBOAT],
        list_of_club_dinghies,
    )

    list_of_classes = get_list_of_boat_classes(object_store).list_of_names()
    list_of_classes = remove_empty_values(list_of_classes)

    active_cadets_as_data_frame[SORT_CLASS] = pd.Categorical(
        active_cadets_as_data_frame[SORT_CLASS],
        list_of_classes,
    )

    return active_cadets_as_data_frame


def remove_empty_values(some_list: List) -> list:
    return [x for x in some_list if len(x) > 0]


def get_sorted_active_cadets_df(
    active_cadets_as_data_frame: pd.DataFrame, sort_order: SortOrderGroups
) -> pd.DataFrame:
    if len(active_cadets_as_data_frame) == 0:
        return active_cadets_as_data_frame

    active_cadets_as_data_frame = active_cadets_as_data_frame.sort_values(
        sort_order.sort_order()
    )

    return active_cadets_as_data_frame


def get_list_of_active_cadets_from_sorted_df(
    sorted_active_cadets_df: pd.DataFrame,
) -> ListOfCadets:
    if len(sorted_active_cadets_df) == 0:
        return ListOfCadets([])
    return ListOfCadets(sorted_active_cadets_df[CADET].to_list())
