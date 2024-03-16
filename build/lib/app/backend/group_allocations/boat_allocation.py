import pandas as pd
from dataclasses import dataclass
from typing import List, Dict

from app.backend.data.resources import load_list_of_cadets_at_event_with_club_dinghies, load_list_of_club_dinghies, save_list_of_cadets_at_event_with_club_dinghies, load_list_of_boat_classes
from app.backend.data.cadets import get_list_of_all_cadets
from app.backend.forms.summarys import summarise_generic_counts_for_event
from app.objects.abstract_objects.abstract_tables import PandasDFTable
from app.objects.cadets import Cadet
from app.objects.day_selectors import DaySelector, Day
from app.objects.events import Event
from app.objects.club_dinghies import NO_BOAT
from app.backend.data.cadets_at_event import load_list_of_cadets_at_event_with_dinghies, \
    save_list_of_cadets_at_event_with_dinghies, load_cadets_at_event
from app.objects.dinghies import no_partnership, CadetAtEventWithDinghy, ListOfCadetAtEventWithDinghies, \
    compare_list_of_cadets_with_dinghies_and_return_list_with_changed_values
from app.objects.club_dinghies import ListOfCadetAtEventWithClubDinghies

def update_club_boat_allocation_for_cadet_at_event(boat_name: str, cadet_id: str, event: Event):
    cadets_with_club_dinghies_at_event = load_list_of_cadets_at_event_with_club_dinghies(event)
    if boat_name==NO_BOAT:
        cadets_with_club_dinghies_at_event.delete_allocation_for_cadet(cadet_id)
    else:
        club_dinghies = load_list_of_club_dinghies()
        boat_id = club_dinghies.id_given_name(boat_name)
        cadets_with_club_dinghies_at_event.update_allocation_for_cadet(cadet_id=cadet_id, club_dinghy_id=boat_id)

    save_list_of_cadets_at_event_with_club_dinghies(event=event, cadets_with_club_dinghies_at_event=cadets_with_club_dinghies_at_event)




@dataclass
class CadetWithDinghyInputs:
    cadet_id: str
    sail_number: str
    boat_class_name: str
    two_handed_partner_name: str



def update_boat_info_for_cadets_at_event(event: Event,
                                         list_of_updates: List[CadetWithDinghyInputs]):

    list_of_existing_cadets_at_event_with_dinghies=load_list_of_cadets_at_event_with_dinghies(event)

    list_of_potentially_updated_cadets_at_event = convert_list_of_inputs_to_list_of_cadet_at_event_objects(
        list_of_updates
    )

    list_of_updated_cadets = compare_list_of_cadets_with_dinghies_and_return_list_with_changed_values(
        new_list=list_of_potentially_updated_cadets_at_event,
        existing_list=list_of_existing_cadets_at_event_with_dinghies
    )

    update_boat_info_for_updated_cadets_at_event(event=event, list_of_updated_cadets=list_of_updated_cadets)



def update_boat_info_for_updated_cadets_at_event(event: Event,
                                        list_of_updated_cadets: ListOfCadetAtEventWithDinghies):

    list_of_cadets_at_event_with_dinghies=load_list_of_cadets_at_event_with_dinghies(event)
    for cadet_at_event_with_dinghy in list_of_updated_cadets:
        list_of_cadets_at_event_with_dinghies.update_boat_info_for_cadet_and_partner_at_event(
            cadet_at_event_with_dinghy
        )

    save_list_of_cadets_at_event_with_dinghies(event=event, cadets_with_dinghies_at_event=list_of_cadets_at_event_with_dinghies)



def convert_list_of_inputs_to_list_of_cadet_at_event_objects(list_of_updates: List[CadetWithDinghyInputs])-> ListOfCadetAtEventWithDinghies:
    return ListOfCadetAtEventWithDinghies(
        [convert_single_input_to_cadet_at_event(update) for update in list_of_updates]
    )

def convert_single_input_to_cadet_at_event(update: CadetWithDinghyInputs) -> CadetAtEventWithDinghy:
    boat_class_id = get_boat_class_id_from_name(update.boat_class_name)
    two_handed_partner_id = get_two_handed_partner_id_from_name(update.two_handed_partner_name)

    return CadetAtEventWithDinghy(
        cadet_id=update.cadet_id,
        boat_class_id=boat_class_id,
        partner_cadet_id=two_handed_partner_id,
        sail_number=update.sail_number
    )

def get_two_handed_partner_id_from_name(two_handed_partner_name: str):
    list_of_cadets =get_list_of_all_cadets()
    if no_partnership(two_handed_partner_name):
        two_handed_partner_id = two_handed_partner_name
    else:
        two_handed_partner_id = list_of_cadets.id_given_name(two_handed_partner_name)

    return two_handed_partner_id

def get_boat_class_id_from_name(boat_class_name:str):

    list_of_boats = load_list_of_boat_classes()
    boat_class_id = list_of_boats.id_given_name(boat_class_name)

    return boat_class_id


def summarise_club_boat_allocations_for_event(event: Event) -> PandasDFTable:
    cadets_with_club_dinghies_at_event = load_list_of_cadets_at_event_with_club_dinghies(event)
    all_club_dinghies = load_list_of_club_dinghies()
    list_of_dinghy_ids = cadets_with_club_dinghies_at_event.unique_sorted_list_of_dinghy_ids(all_club_dinghies)
    row_names = [all_club_dinghies.name_given_id(id) for id in list_of_dinghy_ids]
    cadets_at_event = load_cadets_at_event(event)
    availability_dict = dict([(cadet.cadet_id, cadet.availability)
                              for cadet in cadets_at_event.list_of_active_cadets_at_event()])

    table = summarise_generic_counts_for_event(
        get_id_function=get_relevant_cadet_ids_for_dinghy_id,
        event=event,
        groups=list_of_dinghy_ids,
        group_labels=row_names,
        availability_dict=availability_dict,
        list_of_ids_with_groups=cadets_with_club_dinghies_at_event
    )

    return table



def get_relevant_cadet_ids_for_dinghy_id(group: str,
                                     event: Event,
                                     list_of_ids_with_groups: ListOfCadetAtEventWithClubDinghies):

    ## map from generic to specific var names. Event is not used
    dinghy_id = group
    cadets_with_club_dinghies_at_event = list_of_ids_with_groups

    return [cadet_id
            for cadet_id in cadets_with_club_dinghies_at_event.list_of_cadet_ids()
            if cadets_with_club_dinghies_at_event.dinghy_for_cadet_id(cadet_id)==dinghy_id]


def summarise_class_attendance_for_event(event: Event) -> PandasDFTable:
    cadets_with_dinghies_at_event = load_list_of_cadets_at_event_with_dinghies(event)
    all_boat_classes = load_list_of_boat_classes()
    list_of_boat_class_ids = cadets_with_dinghies_at_event.unique_sorted_list_of_boat_class_ids(all_boat_classes)
    row_names = [all_boat_classes.name_given_id(id) for id in list_of_boat_class_ids]
    cadets_at_event = load_cadets_at_event(event)
    availability_dict = dict([(cadet.cadet_id, cadet.availability)
                              for cadet in cadets_at_event.list_of_active_cadets_at_event()])

    table = summarise_generic_counts_for_event(
        get_id_function=get_relevant_cadet_ids_for_boat_class_id,
        event=event,
        groups=list_of_boat_class_ids,
        group_labels=row_names,
        availability_dict=availability_dict,
        list_of_ids_with_groups=cadets_with_dinghies_at_event
    )

    return table

def get_relevant_cadet_ids_for_boat_class_id(group: str,
                                     event: Event,
                                     list_of_ids_with_groups: ListOfCadetAtEventWithDinghies):

    ## map from generic to specific var names. Event is not used
    boat_class_id = group
    cadets_with_dinghies_at_event = list_of_ids_with_groups

    return [cadet_id
            for cadet_id in cadets_with_dinghies_at_event.list_of_cadet_ids()
            if cadets_with_dinghies_at_event.boat_class_id_for_cadet_id(cadet_id)==boat_class_id]
