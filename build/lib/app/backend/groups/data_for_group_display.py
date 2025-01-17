from typing import Dict, List, Tuple, Union

from app.backend.cadets_at_event.dict_of_all_cadet_at_event_data import (
    cadet_is_unavailable_on_day,
    cadet_is_available_on_day,
    cadet_availability_at_event,
)
from app.data_access.configuration.field_list import (
    CADET_BOAT_OWNERSHIP_STATUS,
    CADET_GROUP_PREFERENCE,
    CADET_BOAT_CLASS,
    DESIRED_BOAT,
    CADET_BOAT_SAIL_NUMBER,
)
from app.objects.boat_classes import ListOfBoatClasses, no_boat_class
from app.objects.cadets import Cadet
from app.objects.club_dinghies import ListOfClubDinghies, no_club_dinghy
from app.objects.composed.cadets_with_all_event_info import DictOfAllEventInfoForCadets
from app.objects.day_selectors import Day
from app.objects.exceptions import missing_data
from app.objects.utils import all_equal, similar


def get_current_group_name_across_days_or_none_if_different(
    dict_of_all_event_data: DictOfAllEventInfoForCadets, cadet: Cadet
):
    all_groups = list(
        remove_na_from_dict(
            get_group_names_across_days(
                dict_of_all_event_data=dict_of_all_event_data, cadet=cadet
            )
        ).values()
    )
    if len(all_groups) == 0:
        return ""
    if all_equal(all_groups):
        return all_groups[0]
    else:
        return None


def get_string_describing_different_group_names(
    dict_of_all_event_data: DictOfAllEventInfoForCadets, cadet: Cadet
):
    all_groups_across_days = get_group_names_across_days(
        dict_of_all_event_data=dict_of_all_event_data, cadet=cadet
    )
    return ", ".join(
        ["%s (%s)" % (group, day.name) for day, group in all_groups_across_days.items()]
    )


def get_group_names_across_days(
    dict_of_all_event_data: DictOfAllEventInfoForCadets, cadet: Cadet
) -> Dict[Day, str]:
    return dict(
        [
            (
                day,
                get_current_group_name_for_day(
                    dict_of_all_event_data=dict_of_all_event_data, cadet=cadet, day=day
                ),
            )
            for day in dict_of_all_event_data.event.days_in_event()
        ]
    )


def get_current_group_name_for_day(
    dict_of_all_event_data: DictOfAllEventInfoForCadets, cadet: Cadet, day: Day
) -> str:
    if cadet_is_unavailable_on_day(
        dict_of_all_event_data=dict_of_all_event_data, cadet=cadet, day=day
    ):
        return NOT_AVAILABLE
    group = dict_of_all_event_data.event_data_for_cadet(
        cadet
    ).days_and_groups.group_on_day(day)

    return group.name


def get_current_club_boat_name_across_days_or_none_if_different(
    dict_of_all_event_data: DictOfAllEventInfoForCadets, cadet: Cadet
):
    all_boats_across_days = list(
        remove_na_from_dict(
            get_club_boat_names_across_days(
                dict_of_all_event_data=dict_of_all_event_data, cadet=cadet
            )
        ).values()
    )
    if len(all_boats_across_days) == 0:
        return ""
    if all_equal(all_boats_across_days):
        return all_boats_across_days[0]
    else:
        return None


def get_string_describing_different_club_boats_across_days(
    dict_of_all_event_data: DictOfAllEventInfoForCadets, cadet: Cadet
):
    all_boats_across_days = get_club_boat_names_across_days(
        dict_of_all_event_data=dict_of_all_event_data, cadet=cadet
    )
    return ", ".join(
        [
            "%s (%s)" % (boat_name, day.name)
            for day, boat_name in all_boats_across_days.items()
        ]
    )


def get_club_boat_names_across_days(
    dict_of_all_event_data: DictOfAllEventInfoForCadets, cadet: Cadet
):
    return dict(
        [
            (
                day,
                get_current_club_boat_name_on_day(
                    dict_of_all_event_data=dict_of_all_event_data, cadet=cadet, day=day
                ),
            )
            for day in dict_of_all_event_data.event.days_in_event()
        ]
    )


def get_current_club_boat_name_on_day(
    dict_of_all_event_data: DictOfAllEventInfoForCadets, cadet: Cadet, day: Day
) -> str:
    if cadet_is_unavailable_on_day(
        dict_of_all_event_data=dict_of_all_event_data, cadet=cadet, day=day
    ):
        return NOT_AVAILABLE
    club_dinghy = dict_of_all_event_data.event_data_for_cadet(
        cadet
    ).days_and_club_dinghies.dinghy_on_day(day)
    if club_dinghy == no_club_dinghy:
        ## Guess
        return guess_if_club_boat_required(
            dict_of_all_event_data=dict_of_all_event_data, cadet=cadet, day=day
        )

    return club_dinghy


def guess_if_club_boat_required(
    dict_of_all_event_data: DictOfAllEventInfoForCadets, cadet: Cadet, day: Day
) -> str:
    ## Guess
    boat_status = dict_of_all_event_data.event_data_for_cadet(
        cadet
    ).registration_data.data_in_row.get(CADET_BOAT_OWNERSHIP_STATUS, "")
    if "club boat" in boat_status.lower():
        return guess_current_club_boat_name_on_day(
            dict_of_all_event_data=dict_of_all_event_data, cadet=cadet, day=day
        )
    else:
        return no_club_dinghy


def guess_current_club_boat_name_on_day(
    dict_of_all_event_data: DictOfAllEventInfoForCadets, cadet: Cadet, day: Day
) -> str:
    ## Guess
    allocation_info = dict_of_all_event_data.event_data_for_cadet(
        cadet
    ).registration_data.data_in_row

    pref_group = allocation_info.get(CADET_GROUP_PREFERENCE, "")
    boat_class = allocation_info.get(CADET_BOAT_CLASS, "")
    pref_boat = allocation_info.get(DESIRED_BOAT, "")

    allocated_group = get_current_group_name_for_day(
        dict_of_all_event_data=dict_of_all_event_data, cadet=cadet, day=day
    )

    list_of_club_boats = (
        dict_of_all_event_data.dict_of_cadets_and_club_dinghies_at_event.list_of_club_dinghies
    )

    return guess_best_club_boat_name_given_list_of_possibly_matching_fields(
        list_of_boats=list_of_club_boats,
        list_of_options=[
            boat_class,
            allocated_group,
            pref_boat,
            pref_group,
        ],
    )


def get_current_boat_class_across_days_or_none_if_different(
    dict_of_all_event_data: DictOfAllEventInfoForCadets, cadet: Cadet
):
    all_boats_across_days = list(
        remove_na_from_dict(
            get_boat_class_names_across_days(
                dict_of_all_event_data=dict_of_all_event_data, cadet=cadet
            )
        ).values()
    )
    if len(all_boats_across_days) == 0:
        return ""
    if all_equal(all_boats_across_days):
        return all_boats_across_days[0]
    else:
        return None


def get_string_describing_different_boat_class_across_days(
    dict_of_all_event_data: DictOfAllEventInfoForCadets, cadet: Cadet
):
    all_boats_across_days = get_boat_class_names_across_days(
        cadet=cadet, dict_of_all_event_data=dict_of_all_event_data
    )
    return ", ".join(
        [
            "%s (%s)" % (boat_name, day.name)
            for day, boat_name in all_boats_across_days.items()
        ]
    )


def get_boat_class_names_across_days(
    dict_of_all_event_data: DictOfAllEventInfoForCadets, cadet: Cadet
):
    return dict(
        [
            (
                day,
                get_name_of_class_of_boat_on_day(
                    cadet=cadet, day=day, dict_of_all_event_data=dict_of_all_event_data
                ),
            )
            for day in dict_of_all_event_data.event.days_in_event()
        ]
    )


def get_name_of_class_of_boat_on_day(
    dict_of_all_event_data: DictOfAllEventInfoForCadets, cadet: Cadet, day: Day
) -> str:
    if cadet_is_unavailable_on_day(
        dict_of_all_event_data=dict_of_all_event_data, cadet=cadet, day=day
    ):
        return NOT_AVAILABLE
    name_from_data = get_name_of_boat_class_on_day_from_data(
        dict_of_all_event_data=dict_of_all_event_data, cadet=cadet, day=day
    )
    if name_from_data is missing_data:
        name_from_data = guess_name_of_boat_class_on_day_from_other_information(
            dict_of_all_event_data=dict_of_all_event_data, cadet=cadet, day=day
        )

    return name_from_data


def get_name_of_boat_class_on_day_from_data(
    dict_of_all_event_data: DictOfAllEventInfoForCadets, cadet: Cadet, day: Day
) -> str:
    boat_class = dict_of_all_event_data.event_data_for_cadet(
        cadet
    ).days_and_boat_class.boat_class_on_day(day=day)
    if boat_class == no_boat_class:
        return missing_data

    return boat_class.name


def guess_name_of_boat_class_on_day_from_other_information(
    dict_of_all_event_data: DictOfAllEventInfoForCadets, cadet: Cadet, day: Day
) -> str:
    allocation_info = dict_of_all_event_data.event_data_for_cadet(
        cadet
    ).registration_data.data_in_row
    pref_group = allocation_info.get(CADET_GROUP_PREFERENCE, "")
    boat_class = allocation_info.get(CADET_BOAT_CLASS, "")
    pref_boat = allocation_info.get(DESIRED_BOAT, "")

    allocated_group = get_current_group_name_for_day(
        dict_of_all_event_data=dict_of_all_event_data, cadet=cadet, day=day
    )

    list_of_dinghies = (
        dict_of_all_event_data.dict_of_cadets_and_boat_class_and_partners.list_of_boat_classes
    )

    return guess_best_boat_class_name_given_list_of_possibly_matching_fields(
        list_of_boats=list_of_dinghies,
        list_of_options=[
            boat_class,
            allocated_group,
            pref_boat,
            pref_group,
        ],
    )


def get_current_sail_number_across_days_or_none_if_different(
    dict_of_all_event_data: DictOfAllEventInfoForCadets, cadet: Cadet
):
    all_numbers_across_days = list(
        remove_na_from_dict(
            get_sail_numbers_across_days(
                dict_of_all_event_data=dict_of_all_event_data, cadet=cadet
            )
        ).values()
    )
    if len(all_numbers_across_days) == 0:
        return ""
    if all_equal(all_numbers_across_days):
        return all_numbers_across_days[0]
    else:
        return None


def get_string_describing_different_sail_numbers_across_days(
    dict_of_all_event_data: DictOfAllEventInfoForCadets, cadet: Cadet
):

    all_numbers = get_sail_numbers_across_days(
        dict_of_all_event_data=dict_of_all_event_data, cadet=cadet
    )
    return ", ".join(
        [
            "%s (%s)" % (sail_number, day.name)
            for day, sail_number in all_numbers.items()
        ]
    )


def get_sail_numbers_across_days(
    dict_of_all_event_data: DictOfAllEventInfoForCadets, cadet: Cadet
):
    return dict(
        [
            (
                day,
                get_sail_number_for_boat_on_day(
                    cadet=cadet, day=day, dict_of_all_event_data=dict_of_all_event_data
                ),
            )
            for day in dict_of_all_event_data.event.days_in_event()
        ]
    )


def get_sail_number_for_boat_on_day(
    dict_of_all_event_data: DictOfAllEventInfoForCadets, cadet: Cadet, day: Day
) -> str:
    if cadet_is_unavailable_on_day(
        dict_of_all_event_data=dict_of_all_event_data, cadet=cadet, day=day
    ):
        return NOT_AVAILABLE
    sail_number_from_data = get_sail_number_for_boat_from_data(
        dict_of_all_event_data=dict_of_all_event_data, cadet=cadet, day=day
    )
    if sail_number_from_data is missing_data:
        sail_number_from_data = get_sail_number_for_boat_from_value_on_form(
            dict_of_all_event_data=dict_of_all_event_data, cadet=cadet
        )

    return sail_number_from_data


def get_sail_number_for_boat_from_data(
    dict_of_all_event_data: DictOfAllEventInfoForCadets, cadet: Cadet, day: Day
) -> str:
    return dict_of_all_event_data.event_data_for_cadet(
        cadet
    ).days_and_boat_class.sail_number_on_day(day=day)


def get_sail_number_for_boat_from_value_on_form(
    dict_of_all_event_data: DictOfAllEventInfoForCadets, cadet: Cadet
) -> str:
    allocation_info = dict_of_all_event_data.event_data_for_cadet(
        cadet
    ).registration_data.data_in_row
    return allocation_info.get(CADET_BOAT_SAIL_NUMBER, "")


def get_two_handed_partner_name_for_cadet_across_days_or_none_if_different(
    dict_of_all_event_data: DictOfAllEventInfoForCadets, cadet: Cadet
):
    all_names_across_days = list(
        remove_na_from_dict(
            get_two_handed_partners_across_days(
                dict_of_all_event_data=dict_of_all_event_data, cadet=cadet
            )
        ).values()
    )
    if len(all_names_across_days) == 0:
        return ""
    if all_equal(all_names_across_days):
        return all_names_across_days[0]
    else:
        return None


def get_string_describing_two_handed_partner_name_across_days(
    dict_of_all_event_data: DictOfAllEventInfoForCadets, cadet: Cadet
):
    all_names = get_two_handed_partners_across_days(
        dict_of_all_event_data=dict_of_all_event_data, cadet=cadet
    )
    return ", ".join(["%s (%s)" % (name, day.name) for day, name in all_names.items()])


def get_two_handed_partners_across_days(
    dict_of_all_event_data: DictOfAllEventInfoForCadets, cadet: Cadet
):
    return dict(
        [
            (
                day,
                get_two_handed_partner_as_str_for_cadet_on_day(
                    dict_of_all_event_data=dict_of_all_event_data, cadet=cadet, day=day
                ),
            )
            for day in dict_of_all_event_data.event.days_in_event()
        ]
    )


def get_two_handed_partner_as_str_for_cadet_on_day(
    dict_of_all_event_data: DictOfAllEventInfoForCadets, cadet: Cadet, day: Day
) -> str:
    if cadet_is_unavailable_on_day(
        dict_of_all_event_data=dict_of_all_event_data, cadet=cadet, day=day
    ):
        return NOT_AVAILABLE
    partner = get_two_handed_partner_for_cadet_on_day(
        dict_of_all_event_data=dict_of_all_event_data, cadet=cadet, day=day
    )

    return str(partner)


def get_two_handed_partner_for_cadet_on_day(
    dict_of_all_event_data: DictOfAllEventInfoForCadets, cadet: Cadet, day: Day
) -> Union[Cadet, object]:

    partner = dict_of_all_event_data.event_data_for_cadet(
        cadet
    ).days_and_boat_class.partner_on_day(day)

    return partner


def get_list_of_cadets_as_str_at_event_with_matching_schedules_excluding_this_cadet(
    dict_of_all_event_data: DictOfAllEventInfoForCadets, cadet: Cadet
) -> List[str]:

    this_cadet_availability = cadet_availability_at_event(
        dict_of_all_event_data=dict_of_all_event_data, cadet=cadet
    )

    cadets_at_event = (
        dict_of_all_event_data.dict_of_cadets_with_registration_data.list_of_active_cadets()
    )
    raw_list_of_cadets_with_matching_schedules = []
    for other_cadet in cadets_at_event:
        if other_cadet == cadet:
            continue
        other_cadet_availability = cadet_availability_at_event(
            dict_of_all_event_data=dict_of_all_event_data, cadet=other_cadet
        )
        if this_cadet_availability == other_cadet_availability:
            raw_list_of_cadets_with_matching_schedules.append(other_cadet)

    cadets_as_str = [str(cadet) for cadet in raw_list_of_cadets_with_matching_schedules]
    cadets_as_str.sort()

    return cadets_as_str


def list_of_cadets_as_str_at_event_excluding_cadet_available_on_day(
    dict_of_all_event_data: DictOfAllEventInfoForCadets, cadet: Cadet, day: Day
):
    list_of_cadets_at_event_available = (
        dict_of_all_event_data.dict_of_cadets_with_registration_data.list_of_active_cadets()
    )
    list_of_cadets_at_event_available.remove(cadet)

    return [
        str(other_cadet)
        for other_cadet in list_of_cadets_at_event_available
        if cadet_is_available_on_day(
            dict_of_all_event_data=dict_of_all_event_data, cadet=cadet, day=day
        )
    ]


NOT_AVAILABLE = "Not available"


def remove_na_from_dict(some_dict: dict) -> dict:
    return dict(
        [(key, value) for key, value in some_dict.items() if not value == NOT_AVAILABLE]
    )


def guess_best_club_boat_name_given_list_of_possibly_matching_fields(
    list_of_boats: ListOfClubDinghies, list_of_options: List[str]
) -> str:
    list_of_names = list_of_boats.list_of_names()

    return best_option_against_boat_names(
        list_of_names=list_of_names, list_of_options=list_of_options
    )


def guess_best_boat_class_name_given_list_of_possibly_matching_fields(
    list_of_boats: ListOfBoatClasses, list_of_options: List[str]
) -> str:
    list_of_names = list_of_boats.list_of_names()

    return best_option_against_boat_names(
        list_of_names=list_of_names, list_of_options=list_of_options
    )


def best_option_against_boat_names(
    list_of_names: List[str], list_of_options: List[str]
) -> str:
    scores_and_names = [
        similarity_score_and_best_option_against_boat_names_for_one_name(
            option, list_of_names=list_of_names
        )
        for option in list_of_options
    ]
    scores = [s[0] for s in scores_and_names]
    names = [s[1] for s in scores_and_names]

    max_score = max(scores)
    max_score_index = scores.index(max_score)
    best_name = names[max_score_index]

    return best_name


def similarity_score_and_best_option_against_boat_names_for_one_name(
    option: str, list_of_names: List[str]
) -> Tuple[float, str]:
    score = [similar(option, boat_name) for boat_name in list_of_names]
    high_score = max(score)
    high_score_index = score.index(high_score)

    return high_score, list_of_names[high_score_index]
