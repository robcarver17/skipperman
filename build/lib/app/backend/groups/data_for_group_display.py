from enum import Enum
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
from app.objects.exceptions import missing_data, arg_not_passed
from app.objects.groups import unallocated_group
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
            "%s (%s)" % (boat_name_or_none_if_empty(boat_name), day.name)
            for day, boat_name in all_boats_across_days.items()
        ]
    )


def boat_name_or_none_if_empty(boat_name: str):
    if len(boat_name) == 0:
        return "None"
    else:
        return boat_name


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

    return club_dinghy.name


def guess_if_club_boat_required_and_return_name(
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
        return NO_CLUB_DINGHY_NAME


NO_CLUB_DINGHY_NAME = no_club_dinghy.name


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
) -> Union[str, None]:
    all_boats_across_days = list(
        remove_na_from_dict(
            get_boat_class_names_across_days(
                dict_of_all_event_data=dict_of_all_event_data, cadet=cadet
            )
        ).values()
    )
    if len(all_boats_across_days) == 0:
        return no_boat_class.name
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
        return no_boat_class.name

    return name_from_data


def get_name_of_boat_class_on_day_from_data(
    dict_of_all_event_data: DictOfAllEventInfoForCadets, cadet: Cadet, day: Day
) -> str:
    boat_class = dict_of_all_event_data.event_data_for_cadet(
        cadet
    ).days_and_boat_class.boat_class_on_day(day=day, default=no_boat_class)
    if boat_class == no_boat_class:
        return missing_data

    return boat_class.name


INFORMATION_NOT_AVAILABLE = ""


def guess_name_of_boat_class_on_day_from_other_information(
    dict_of_all_event_data: DictOfAllEventInfoForCadets, cadet: Cadet, day: Day
) -> str:
    allocation_info = dict_of_all_event_data.event_data_for_cadet(
        cadet
    ).registration_data.data_in_row
    pref_group = allocation_info.get(CADET_GROUP_PREFERENCE, INFORMATION_NOT_AVAILABLE)
    boat_class = allocation_info.get(CADET_BOAT_CLASS, INFORMATION_NOT_AVAILABLE)
    pref_boat = allocation_info.get(DESIRED_BOAT, INFORMATION_NOT_AVAILABLE)

    allocated_group_name = (
        get_current_group_name_for_day_with_empty_string_if_unallocated(
            dict_of_all_event_data=dict_of_all_event_data, cadet=cadet, day=day
        )
    )
    allocated_club_boat = (
        get_current_club_boat_name_for_day_with_empty_string_if_unallocated(
            dict_of_all_event_data=dict_of_all_event_data, cadet=cadet, day=day
        )
    )

    list_of_dinghies = (
        dict_of_all_event_data.dict_of_cadets_and_boat_class_and_partners.list_of_boat_classes
    )
    best_guess = guess_best_boat_class_name_given_list_of_possibly_matching_fields(
        list_of_boats=list_of_dinghies,
        list_of_options=[
            boat_class,
            allocated_group_name,
            pref_boat,
            pref_group,
            allocated_club_boat,
        ],
    )

    return best_guess


def get_current_group_name_for_day_with_empty_string_if_unallocated(
    dict_of_all_event_data: DictOfAllEventInfoForCadets, cadet: Cadet, day: Day
):
    allocated_group_name = get_current_group_name_for_day(
        dict_of_all_event_data=dict_of_all_event_data, cadet=cadet, day=day
    )
    if allocated_group_name == unallocated_group.name:
        allocated_group_name = INFORMATION_NOT_AVAILABLE

    return allocated_group_name


def get_current_club_boat_name_for_day_with_empty_string_if_unallocated(
    dict_of_all_event_data: DictOfAllEventInfoForCadets, cadet: Cadet, day: Day
):
    club_boat = dict_of_all_event_data.dict_of_cadets_and_club_dinghies_at_event.club_dinghys_for_cadet(
        cadet=cadet
    ).dinghy_on_day(
        day=day, default=no_club_dinghy
    )

    if club_boat == no_club_dinghy:
        return INFORMATION_NOT_AVAILABLE

    return club_boat.name


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

    return partner.name


def get_two_handed_partner_as_str_for_dropdown_cadet_on_day(
    dict_of_all_event_data: DictOfAllEventInfoForCadets, cadet: Cadet, day: Day
) -> str:

    partner = get_two_handed_partner_for_cadet_on_day(
        dict_of_all_event_data=dict_of_all_event_data, cadet=cadet, day=day
    )

    partner_name = get_cadet_name_or_none_given_schedule_status(
        dict_of_all_event_data=dict_of_all_event_data,
        cadet=cadet,
        other_cadet=partner,
        specific_day=day,
    )
    if partner_name is None:
        raise Exception("Partner name should not resolve to none for matched partner")

    return partner_name


def get_two_handed_partner_as_str_for_dropdown_cadet_across_days(
    dict_of_all_event_data: DictOfAllEventInfoForCadets, cadet: Cadet
) -> str:

    current_partner_name = (
        get_two_handed_partner_name_for_cadet_across_days_or_none_if_different(
            dict_of_all_event_data=dict_of_all_event_data, cadet=cadet
        )
    )
    if current_partner_name is None:
        return None

    partner = dict_of_all_event_data.dict_of_cadets_and_boat_class_and_partners.boat_classes_and_partner_for_cadet(
        cadet
    ).most_common_partner()

    partner_name = get_cadet_name_or_none_given_schedule_status(
        dict_of_all_event_data=dict_of_all_event_data, cadet=cadet, other_cadet=partner
    )
    if partner_name is None:
        raise Exception("Partner name should not resolve to none for matched partner")

    return partner_name


def get_two_handed_partner_for_cadet_on_day(
    dict_of_all_event_data: DictOfAllEventInfoForCadets, cadet: Cadet, day: Day
) -> Union[Cadet, object]:

    partner = dict_of_all_event_data.event_data_for_cadet(
        cadet
    ).days_and_boat_class.partner_on_day(day)

    return partner


Schedule = Enum(
    "Schedule", ["match", "no_match", "partial_match", "unavailable", "same_cadet"]
)
matched_schedule = Schedule.match
no_matched_schedule = Schedule.no_match
partial_matched_schedule = Schedule.partial_match
same_cadet = Schedule.same_cadet
unavailable = Schedule.unavailable


def get_list_of_cadet_names_including_asterix_marks_at_event_with_matching_schedules_excluding_this_cadet(
    dict_of_all_event_data: DictOfAllEventInfoForCadets,
    cadet: Cadet,
    available_on_specific_day: Day = arg_not_passed,
) -> List[str]:

    cadets_at_event = (
        dict_of_all_event_data.dict_of_cadets_with_registration_data.list_of_active_cadets()
    )
    raw_list_of_cadet_names__with_matching_schedules = []
    for other_cadet in cadets_at_event:
        cadet_name_or_none = get_cadet_name_or_none_given_schedule_status(
            dict_of_all_event_data=dict_of_all_event_data,
            cadet=cadet,
            other_cadet=other_cadet,
            specific_day=available_on_specific_day,
        )
        if cadet_name_or_none is None:
            continue

        raw_list_of_cadet_names__with_matching_schedules.append(cadet_name_or_none)

    raw_list_of_cadet_names__with_matching_schedules.sort()

    return raw_list_of_cadet_names__with_matching_schedules


from app.objects.partners import (
    no_partnership_given_partner_cadet,
    from_partner_cadet_to_id_or_string,
)


def get_cadet_name_or_none_given_schedule_status(
    dict_of_all_event_data: DictOfAllEventInfoForCadets,
    cadet: Cadet,
    other_cadet: Cadet,
    specific_day: Day = arg_not_passed,
):

    if no_partnership_given_partner_cadet(other_cadet):
        return from_partner_cadet_to_id_or_string(other_cadet)

    schedule = get_schedule_status_for_two_cadets(
        dict_of_all_event_data=dict_of_all_event_data,
        cadet=cadet,
        other_cadet=other_cadet,
        specific_day=specific_day,
    )

    if schedule is same_cadet:
        return None
    elif schedule is unavailable:
        return None
    elif schedule is no_matched_schedule:
        return None
    elif schedule is matched_schedule:
        return other_cadet.name
    elif schedule is partial_matched_schedule:
        return other_cadet.name + "*"  ## NO SPACES
    else:
        raise Exception("Don't know this schedule")


def get_schedule_status_for_two_cadets(
    dict_of_all_event_data: DictOfAllEventInfoForCadets,
    cadet: Cadet,
    other_cadet: Cadet,
    specific_day: Day = arg_not_passed,
) -> Schedule:

    if cadet == other_cadet:
        return same_cadet
    this_cadet_availability = cadet_availability_at_event(
        dict_of_all_event_data=dict_of_all_event_data, cadet=cadet
    )
    other_cadet_availability = cadet_availability_at_event(
        dict_of_all_event_data=dict_of_all_event_data, cadet=other_cadet
    )

    if specific_day is not arg_not_passed:
        if not other_cadet_availability.available_on_day(specific_day):
            return unavailable

    if this_cadet_availability == other_cadet_availability:
        return matched_schedule

    if (
        len(this_cadet_availability.days_that_intersect_with(other_cadet_availability))
        > 0
    ):
        return partial_matched_schedule

    return no_matched_schedule


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
    list_of_options = remove_empty(list_of_options)
    if len(list_of_options) == 0:
        return ""

    list_of_names = remove_empty(list_of_boats.list_of_names())
    best_option = best_option_against_boat_names(
        list_of_names=list_of_names, list_of_options=list_of_options
    )
    return best_option


def remove_empty(list_of_options: List[str]) -> List[str]:
    return [x for x in list_of_options if not x == INFORMATION_NOT_AVAILABLE]


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
    if max_score < 0.3:
        ## no idea
        return ""

    max_score_index = scores.index(max_score)
    best_name = names[max_score_index]

    return best_name


def similarity_score_and_best_option_against_boat_names_for_one_name(
    option: str, list_of_names: List[str]
) -> Tuple[float, str]:
    score = [
        contains_or_similar(name_with_boat_or_similar=option, boat_name=boat_name)
        for boat_name in list_of_names
    ]
    high_score = max(score)
    high_score_index = score.index(high_score)

    return high_score, list_of_names[high_score_index]


def contains_or_similar(name_with_boat_or_similar: str, boat_name: str):
    boat_contains = boat_name in name_with_boat_or_similar
    option_contains = name_with_boat_or_similar in boat_name
    if boat_contains or option_contains:
        return 1.0
    else:
        return similar(name_with_boat_or_similar, boat_name)


def get_potential_partner_to_be_added_or_missing_data(
    cadet: Cadet, dict_of_all_event_data: DictOfAllEventInfoForCadets
) -> Union[str, object]:
    registration_data = dict_of_all_event_data.dict_of_cadets_with_registration_data.registration_data_for_cadet(
        cadet
    )
    potential_partner = registration_data.two_handed_partner(default=missing_data)

    print("%s: (%s)" % (cadet, potential_partner))
    if looks_like_cadet_already_has_allocated_partner(
        dict_of_all_event_data=dict_of_all_event_data, cadet=cadet
    ):
        return missing_data

    if potential_partner is missing_data:
        return missing_data

    if len(potential_partner) == 0:
        return missing_data

    if looks_like_partner_is_already_at_event(
        dict_of_all_event_data=dict_of_all_event_data,
        potential_partner=potential_partner,
    ):
        return missing_data

    return potential_partner


def looks_like_cadet_already_has_allocated_partner(
    dict_of_all_event_data: DictOfAllEventInfoForCadets, cadet: Cadet
):
    boat_classes_and_partner_for_cadet = dict_of_all_event_data.dict_of_cadets_and_boat_class_and_partners.boat_classes_and_partner_for_cadet(
        cadet
    )
    most_common_partner = boat_classes_and_partner_for_cadet.most_common_partner()
    most_common_partner_is_not_a_partner = no_partnership_given_partner_cadet(
        most_common_partner
    )

    return not most_common_partner_is_not_a_partner


def looks_like_partner_is_already_at_event(
    dict_of_all_event_data: DictOfAllEventInfoForCadets, potential_partner: str
):
    active_cadets_at_event = (
        dict_of_all_event_data.dict_of_cadets_with_registration_data.list_of_active_cadets()
    )
    matching_cadet = active_cadets_at_event.matching_cadet_with_name(
        potential_partner, default=missing_data
    )
    cadet_at_event = not matching_cadet is missing_data

    return cadet_at_event
