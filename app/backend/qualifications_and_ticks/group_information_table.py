from collections.abc import Callable
from typing import List, Dict

import pandas as pd

from app.backend.groups.previous_groups import get_group_allocations_for_event_active_cadets_only
from app.backend.qualifications_and_ticks.qualifications_for_cadet import highest_qualification_for_cadet, \
    name_of_highest_qualification_for_cadet
from app.data_access.store.object_store import ObjectStore
from app.objects.cadets import Cadet, ListOfCadets
from app.objects.club_dinghies import no_club_dinghy
from app.objects.day_selectors import Day
from app.objects.events import Event
from app.objects.groups import Group
from app.backend.cadets_at_event.dict_of_all_cadet_at_event_data import get_dict_of_all_event_info_for_cadets

from app.objects.composed.cadets_with_all_event_info import DictOfAllEventInfoForCadets
from app.objects.partners import no_partnership_given_partner_cadet


def get_group_info_table(object_store: ObjectStore, event: Event, group: Group) -> pd.DataFrame:
    all_group_allocations_at_event = get_group_allocations_for_event_active_cadets_only(
        object_store=object_store, event=event
    )
    cadets_in_group = all_group_allocations_at_event.cadets_in_group_during_event(group)
    cadets_in_group = cadets_in_group.sort_by_firstname()

    all_event_info_for_cadets = get_dict_of_all_event_info_for_cadets(object_store=object_store, event=event)

    club_boats = get_boat_ownership_column_for_list_of_cadets(all_event_info_for_cadets=all_event_info_for_cadets,
                                                         list_of_cadets=cadets_in_group,
                                                         group=group)

    boat_class = get_boat_class_and_sail_number_column_for_list_of_cadets(all_event_info_for_cadets=all_event_info_for_cadets,
                                                         list_of_cadets=cadets_in_group,
                                                         group=group)

    partners = get_partner_column_for_list_of_cadets(all_event_info_for_cadets=all_event_info_for_cadets,
                                                         list_of_cadets=cadets_in_group,
                                                         group=group)

    qualis = get_qualification_column_for_list_of_cadets(object_store=object_store, list_of_cadets=cadets_in_group)

    health = get_health_column_for_list_of_cadets(all_event_info_for_cadets=all_event_info_for_cadets,
                                                         list_of_cadets=cadets_in_group,
                                                         group=group)

    days_column = get_days_attending_column_for_list_of_cadets(all_event_info_for_cadets=all_event_info_for_cadets,
                                                         list_of_cadets=cadets_in_group,
                                                         group=group)

    cadets_as_str = ["%s (%d)" % (cadet.name, cadet.approx_age_years()) for cadet in cadets_in_group]
    df = pd.DataFrame({
        'Boat': boat_class,
        'Ownership': club_boats,
        'Partner': partners,
        'Highest qualification': qualis,
        'Health':health,
        'Days': days_column
    }, index=cadets_as_str)

    return df

def get_days_attending_and_in_group_for_cadet(all_event_info_for_cadets: DictOfAllEventInfoForCadets, group: Group, cadet: Cadet):
    days_attending = all_event_info_for_cadets.event_data_for_cadet(cadet).registration_data.availability.days_available()
    in_group = [day for day in days_attending if all_event_info_for_cadets.event_data_for_cadet(cadet).days_and_groups.group_on_day(day=day)==group]

    return in_group



def get_boat_ownership_column_for_list_of_cadets(all_event_info_for_cadets: DictOfAllEventInfoForCadets, group: Group, list_of_cadets: ListOfCadets):
    return get_generic_column_for_list_of_cadets(
        all_event_info_for_cadets=all_event_info_for_cadets,
        group=group,
        function_to_extract_str=get_boat_ownership_column_for_cadet_on_day,
        list_of_cadets=list_of_cadets)

def get_generic_column_for_list_of_cadets(all_event_info_for_cadets: DictOfAllEventInfoForCadets, group: Group, list_of_cadets: ListOfCadets,function_to_extract_str: Callable):
    return [get_generic_column_for_cadet(
        all_event_info_for_cadets=all_event_info_for_cadets,
        cadet=cadet,
        group=group,
        function_to_extract_str=function_to_extract_str
    ) for cadet in list_of_cadets]


def get_generic_column_for_cadet(all_event_info_for_cadets: DictOfAllEventInfoForCadets, group: Group, cadet: Cadet,function_to_extract_str: Callable):
    days_in_group = get_days_attending_and_in_group_for_cadet(all_event_info_for_cadets=all_event_info_for_cadets, cadet=cadet, group=group)
    as_dict = get_generic_column_for_cadet_as_dict(all_event_info_for_cadets=all_event_info_for_cadets, cadet=cadet, days_in_group=days_in_group,
                                                   function_to_extract_str=function_to_extract_str)

    return annotate_item(as_dict)

def get_generic_column_for_cadet_as_dict(all_event_info_for_cadets: DictOfAllEventInfoForCadets, cadet: Cadet, days_in_group: List[Day],
                                         function_to_extract_str: Callable):
    return dict([(day, function_to_extract_str(all_event_info_for_cadets=all_event_info_for_cadets, cadet=cadet, day=day))
                 for day in days_in_group])

def get_boat_ownership_column_for_cadet_on_day(all_event_info_for_cadets: DictOfAllEventInfoForCadets, cadet: Cadet, day: Day):
    dinghy_on_day = all_event_info_for_cadets.event_data_for_cadet(cadet).days_and_club_dinghies.dinghy_on_day(day)
    if dinghy_on_day==no_club_dinghy:
        return "Own boat"
    else:
        return "Club: %s" % dinghy_on_day.name


def get_boat_class_and_sail_number_column_for_list_of_cadets(all_event_info_for_cadets: DictOfAllEventInfoForCadets, group: Group, list_of_cadets: ListOfCadets):
    return get_generic_column_for_list_of_cadets(
        all_event_info_for_cadets=all_event_info_for_cadets,
        group=group,
        function_to_extract_str=get_boat_class_column_for_cadet_on_day,
        list_of_cadets=list_of_cadets)

def get_boat_class_column_for_cadet_on_day(all_event_info_for_cadets: DictOfAllEventInfoForCadets, cadet: Cadet, day: Day):
    boat_class = str(all_event_info_for_cadets.event_data_for_cadet(cadet).days_and_boat_class.boat_class_on_day(day))
    sail_number =all_event_info_for_cadets.event_data_for_cadet(cadet).days_and_boat_class.sail_number_on_day(day)
    if len(sail_number)==0:
        return boat_class
    return "%s (%s)" % (boat_class, sail_number)


def get_partner_column_for_list_of_cadets(all_event_info_for_cadets: DictOfAllEventInfoForCadets, group: Group, list_of_cadets: ListOfCadets):
    return get_generic_column_for_list_of_cadets(
        all_event_info_for_cadets=all_event_info_for_cadets,
        group=group,
        function_to_extract_str=get_partner_column_for_cadet_on_day,
        list_of_cadets=list_of_cadets)

def get_partner_column_for_cadet_on_day(all_event_info_for_cadets: DictOfAllEventInfoForCadets, cadet: Cadet, day: Day):
    partner = all_event_info_for_cadets.event_data_for_cadet(cadet).days_and_boat_class.partner_on_day(day)
    if no_partnership_given_partner_cadet(partner):
        return ""
    else:
        return partner.name

def get_qualification_column_for_list_of_cadets(object_store: ObjectStore, list_of_cadets: ListOfCadets):
    return [
        name_of_highest_qualification_for_cadet(
            object_store=object_store,
            cadet=cadet)
        for cadet in list_of_cadets
    ]

def get_health_column_for_list_of_cadets(all_event_info_for_cadets: DictOfAllEventInfoForCadets, group: Group, list_of_cadets: ListOfCadets):
    return get_generic_column_for_list_of_cadets(
        all_event_info_for_cadets=all_event_info_for_cadets,
        group=group,
        function_to_extract_str=get_health_column_for_cadet_on_day,
        list_of_cadets=list_of_cadets)

def get_health_column_for_cadet_on_day(all_event_info_for_cadets: DictOfAllEventInfoForCadets, cadet: Cadet, day: Day): ## day not used
    return all_event_info_for_cadets.event_data_for_cadet(cadet).registration_data.health

def get_days_attending_column_for_list_of_cadets(all_event_info_for_cadets: DictOfAllEventInfoForCadets, group: Group, list_of_cadets: ListOfCadets):
    return [
        get_days_attending_column_for_single_cadets(all_event_info_for_cadets=all_event_info_for_cadets,
                                                    group=group,
                                                    cadet=cadet)
        for cadet in list_of_cadets
    ]

def get_days_attending_column_for_single_cadets(all_event_info_for_cadets: DictOfAllEventInfoForCadets,
                                                     group: Group, cadet: Cadet):

    all_days_for_cadet = get_days_attending_and_in_group_for_cadet(cadet=cadet, group=group, all_event_info_for_cadets=all_event_info_for_cadets)
    event_days = all_event_info_for_cadets.event.days_in_event()
    print("days for cadet %s %s" % (cadet, all_days_for_cadet))
    print("even days %s" % event_days)
    cadet_at_all_days_for_event = len(set(event_days).difference(set(all_days_for_cadet)))==0
    print("tru? %s" % cadet_at_all_days_for_event)
    if cadet_at_all_days_for_event:
        return "All"
    else:
        return ", ".join([day.name[:3] for day in all_days_for_cadet])

def annotate_item(dict_of_items_by_day: Dict[Day, str]) -> str:
    if len(dict_of_items_by_day)==0:
        return ""
    elif values_all_the_same(dict_of_items_by_day):
        list_of_values = list(dict_of_items_by_day.values())
        return list_of_values[0]
    else:
        return day_annotation(dict_of_items_by_day)

def values_all_the_same(dict_of_values: Dict[Day, str]) -> bool:
    return len(set(list(dict_of_values.values())))<=1

def day_annotation(dict_of_values: Dict[Day, str]):
    values_over_days = ["%s (%s)" % (str_value, day.name[:3]) for day, str_value in dict_of_values.items()]

    return ", ".join(values_over_days)

