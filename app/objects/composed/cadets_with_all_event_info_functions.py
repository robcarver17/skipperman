from copy import copy
from dataclasses import dataclass
from typing import Union, Dict

from app.objects.cadets import ListOfCadets, Cadet
from app.objects.composed.cadets_at_event_with_boat_classes_and_partners import (
    DictOfCadetsAndBoatClassAndPartners,
)
from app.objects.composed.cadets_at_event_with_boat_classes_groups_club_dnghies_and_partners import (
    CadetBoatClassClubDinghyGroupAndPartnerAtEventOnDay,
    are_partners_equal,
)
from app.objects.composed.people_at_event_with_club_dinghies import (
    DictOfPeopleAndClubDinghiesAtEvent,
)
from app.objects.composed.cadets_at_event_with_groups import (
    DictOfCadetsWithDaysAndGroupsAtEvent,
)
from app.objects.composed.cadets_at_event_with_registration_data import (
    DictOfCadetsWithRegistrationData,
)
from app.objects.day_selectors import Day, DaySelector
from app.objects.groups import unallocated_group
from app.objects.partners import valid_partnership_given_partner_cadet, NoCadetPartner


def cadets_not_allocated_to_group_but_attending_on_day(
    dict_of_cadets_with_registration_data: DictOfCadetsWithRegistrationData,
    dict_of_cadets_with_days_and_groups: DictOfCadetsWithDaysAndGroupsAtEvent,
    day: Day,
) -> ListOfCadets:
    list_of_cadets = []
    for cadet in dict_of_cadets_with_registration_data.list_of_cadets():
        inactive = (
            not dict_of_cadets_with_registration_data.registration_data_for_cadet(
                cadet
            ).status.is_active
        )
        if inactive:
            continue

        attending = dict_of_cadets_with_registration_data.registration_data_for_cadet(
            cadet
        ).availability.available_on_day(day)
        if not attending:
            continue

        group = dict_of_cadets_with_days_and_groups.get_days_and_groups_for_cadet(
            cadet
        ).group_on_day(day, default=unallocated_group)
        if group is unallocated_group:
            list_of_cadets.append(cadet)

    return ListOfCadets(list_of_cadets)


def cadets_not_allocated_to_group_on_at_least_one_day_attending(
    dict_of_cadets_with_registration_data: DictOfCadetsWithRegistrationData,
    dict_of_cadets_with_days_and_groups: DictOfCadetsWithDaysAndGroupsAtEvent,
) -> ListOfCadets:
    list_of_cadets = []
    for cadet in dict_of_cadets_with_registration_data.list_of_cadets():
        inactive = (
            not dict_of_cadets_with_registration_data.registration_data_for_cadet(
                cadet
            ).status.is_active
        )
        if inactive:
            continue

        if cadet_is_not_allocated_to_group_on_at_least_one_day_attending(
            cadet=cadet,
            dict_of_cadets_with_registration_data=dict_of_cadets_with_registration_data,
            dict_of_cadets_with_days_and_groups=dict_of_cadets_with_days_and_groups,
        ):
            list_of_cadets.append(cadet)

    return ListOfCadets(list_of_cadets)


def cadet_is_not_allocated_to_group_on_at_least_one_day_attending(
    cadet: Cadet,
    dict_of_cadets_with_registration_data: DictOfCadetsWithRegistrationData,
    dict_of_cadets_with_days_and_groups: DictOfCadetsWithDaysAndGroupsAtEvent,
) -> bool:
    availability = dict_of_cadets_with_registration_data.registration_data_for_cadet(
        cadet
    ).availability
    days_when_cadet_is_available = availability.days_available()
    for day in days_when_cadet_is_available:
        days_and_groups = (
            dict_of_cadets_with_days_and_groups.get_days_and_groups_for_cadet(cadet)
        )
        group_on_day = days_and_groups.group_on_day(day)
        if group_on_day is unallocated_group:
            return True

    return False
