from typing import Dict, List, Tuple
from dataclasses import dataclass

from app.backend.group_allocations.group_allocation_info import get_group_allocation_info, \
    GroupAllocationInfo
from app.backend.events import get_sorted_list_of_events
from app.backend.group_allocations.cadet_event_allocations import get_list_of_active_cadets_at_event, \
    load_allocation_for_event
from app.backend.group_allocations.previous_allocations import allocation_for_cadet_in_previous_events, \
    get_dict_of_allocations_for_events_and_list_of_cadets
from app.data_access.configuration.configuration import UNALLOCATED_GROUP_NAME
from app.backend.data.cadets_at_event import load_cadets_at_event
from app.backend.data.cadets import get_list_of_all_cadets
from app.data_access.configuration.field_list import CADET_GROUP_PREFERENCE, DESIRED_BOAT, CADET_BOAT_CLASS, CADET_BOAT_SAIL_NUMBER
from app.backend.data.resources import load_list_of_club_dinghies, load_list_of_cadets_at_event_with_club_dinghies
from app.backend.data.resources import load_list_of_boat_classes
from app.backend.data.cadets_at_event import load_list_of_cadets_at_event_with_dinghies
from app.data_access.configuration.field_list_groups import GROUP_ALLOCATION_FIELDS_TO_IGNORE_WHEN_RACING_ONLY

from app.objects.cadets import ListOfCadets, Cadet
from app.objects.constants import missing_data
from app.objects.day_selectors import DaySelector
from app.objects.events import Event, list_of_events_excluding_one_event, SORT_BY_START_ASC
from app.objects.groups import ListOfCadetIdsWithGroups, Group
from app.objects.club_dinghies import ListOfCadetAtEventWithClubDinghies, ListOfClubDinghies, NO_BOAT
from app.objects.dinghies import ListOfDinghies, ListOfCadetAtEventWithDinghies, no_partnership, NO_PARTNER_REQUIRED
from app.objects.utils import similar

from app.objects.cadet_at_event import ListOfCadetsAtEvent


@dataclass
class AllocationData:
    event: Event
    current_allocation_for_event: ListOfCadetIdsWithGroups
    cadets_at_event_including_non_active: ListOfCadetsAtEvent
    list_of_cadets_in_event_active_only: ListOfCadets
    list_of_all_cadets: ListOfCadets
    previous_allocations_as_dict: Dict[Event, ListOfCadetIdsWithGroups]
    group_allocation_info: GroupAllocationInfo
    list_of_club_boats_allocated: ListOfCadetAtEventWithClubDinghies
    list_of_cadets_at_event_with_dinghies: ListOfCadetAtEventWithDinghies
    list_of_club_boats: ListOfClubDinghies
    list_of_dinghies: ListOfDinghies

    def get_two_handed_partner_name_for_cadet(self, cadet: Cadet) -> str:
        partner_id = self.get_two_handed_partner_id_for_cadet(cadet)

        if no_partnership(partner_id):
            return partner_id
        cadet = self.list_of_cadets_in_event_active_only.object_with_id(partner_id)
        if cadet is missing_data:
            raise Exception("Cadet partnet with ID %s not found" % partner_id)

        return cadet.name

    def get_two_handed_partner_id_for_cadet(self, cadet: Cadet) -> str:
        partner_id = self.list_of_cadets_at_event_with_dinghies.cadet_partner_id_for_cadet_id(cadet_id=cadet.id)
        if partner_id is missing_data:
            return NO_PARTNER_REQUIRED

        return partner_id

    def get_sail_number_for_boat(self, cadet: Cadet)-> str:
        sail_number_from_data = self.get_sail_number_for_boat_from_data(cadet)
        if sail_number_from_data is missing_data:
            sail_number_from_data = self.get_sail_number_for_boat_from_value_on_form(cadet)

        return sail_number_from_data

    def get_sail_number_for_boat_from_data(self, cadet: Cadet)-> str:
        return self.list_of_cadets_at_event_with_dinghies.sail_number_for_cadet_id(cadet.id)

    def get_sail_number_for_boat_from_value_on_form(self, cadet: Cadet)-> str:
        allocation_info = self.group_allocation_info.get_allocation_info_for_cadet(cadet)
        return allocation_info.get(CADET_BOAT_SAIL_NUMBER, '')

    def get_name_of_class_of_boat(self, cadet: Cadet)-> str:
        name_from_data = self.get_name_of_boat_class_from_data(cadet)
        if name_from_data is missing_data:
            name_from_data = self.guess_name_of_boat_class_from_other_information(cadet)

        return name_from_data

    def get_name_of_boat_class_from_data(self, cadet: Cadet)-> str:
        boat_class_id = self.list_of_cadets_at_event_with_dinghies.boat_class_id_for_cadet_id(cadet_id=cadet.id)
        return self.list_of_dinghies.name_given_id(boat_class_id)

    def guess_name_of_boat_class_from_other_information(self, cadet: Cadet)-> str:
        allocation_info = self.group_allocation_info.get_allocation_info_for_cadet(cadet)
        pref_group = allocation_info.get(CADET_GROUP_PREFERENCE, '')
        boat_class = allocation_info.get(CADET_BOAT_CLASS, '')
        pref_boat = allocation_info.get(DESIRED_BOAT, '')

        allocated_group = self.get_current_group_name(cadet)

        return guess_best_boat_class_name_given_list_of_possibly_matching_fields([
            boat_class,
            allocated_group,
            pref_boat,
            pref_group,
        ])

    def get_current_club_boat_name(self, cadet: Cadet)-> str:
        dinghy_id = self.list_of_club_boats_allocated.dinghy_for_cadet_id(cadet.id)
        if dinghy_id is missing_data:
            return NO_BOAT
        return self.list_of_club_boats.name_given_id(dinghy_id)

    def group_info_fields(self):
        visible_field_names =  self.group_allocation_info.visible_field_names
        if not self.event.contains_groups:
            try:
                for field in GROUP_ALLOCATION_FIELDS_TO_IGNORE_WHEN_RACING_ONLY:
                    visible_field_names.remove(field)
            except:
                pass

        return visible_field_names

    def group_info_dict_for_cadet_as_ordered_list(self, cadet: Cadet):
        info_dict = self.group_allocation_info.get_allocation_info_for_cadet(cadet)

        return [info_dict.get(field_name, "") for field_name in self.group_info_fields()]

    def previous_event_names(self) -> list:
        if not self.event.contains_groups:
            return []

        previous_events = self.previous_allocations_as_dict.keys()
        event_names = [str(event) for event in previous_events]

        return event_names

    def previous_groups_as_list_of_str(self, cadet: Cadet) -> list:
        if not self.event.contains_groups:
            return []
        previous_groups_as_list = self.previous_groups_as_list(cadet)
        return [x.as_str_replace_unallocated_with_empty() for x in previous_groups_as_list]


    def previous_groups_as_list(self, cadet: Cadet) -> List[Group]:
        return allocation_for_cadet_in_previous_events(cadet=cadet,previous_allocations_as_dict=self.previous_allocations_as_dict)

    def get_last_group_name(self, cadet: Cadet) -> str:
        previous_allocation = self.previous_groups_as_list(cadet)
        previous_allocation.reverse() ## last event first when considering
        for allocation in previous_allocation:
            if allocation == UNALLOCATED_GROUP_NAME:
                continue
            else:
                return allocation.group_name

        return UNALLOCATED_GROUP_NAME

    def get_current_group_name(self, cadet: Cadet)-> str:
        try:
            current_allocation = self.current_allocation_for_event.item_with_cadet_id(
                cadet_id=cadet.id
            ).group.group_name

        except:
            current_allocation = self.get_last_group_name(cadet)

        return current_allocation

    def cadet_availability_at_event(self, cadet: Cadet)-> DaySelector:
        cadet_at_event =  self.cadets_at_event_including_non_active.cadet_at_event(cadet_id=cadet.id)
        return cadet_at_event.availability

    def list_of_names_of_cadets_at_event_excluding_cadet(self, cadet: Cadet) -> List[str]:
        ids_at_event = self.list_of_cadets_in_event_active_only.list_of_ids
        ids_at_event_excluding_cadet = [id for id in ids_at_event if not id==cadet.id]
        names = [self.list_of_all_cadets.object_with_id(id).name for id in ids_at_event_excluding_cadet]
        names.sort()

        return names

def guess_best_boat_class_name_given_list_of_possibly_matching_fields(list_of_options: List[str])-> str:
    list_of_boats = load_list_of_boat_classes()
    list_of_names = list_of_boats.list_of_names()

    return best_option_against_boat_names(list_of_names=list_of_names, list_of_options=list_of_options)

def best_option_against_boat_names(list_of_names: List[str], list_of_options: List[str]) -> str:
    scores_and_names = [
        similarity_score_and_best_option_against_boat_names_for_one_name(option, list_of_names=list_of_names)
        for option in list_of_options
    ]
    scores = [s[0] for s in scores_and_names]
    names = [s[1] for s in scores_and_names]

    max_score = max(scores)
    max_score_index = scores.index(max_score)
    best_name = names[max_score_index]

    return best_name

def similarity_score_and_best_option_against_boat_names_for_one_name(option: str, list_of_names: List[str]) -> Tuple[float, str]:
    score = [similar(option, boat_name) for boat_name in list_of_names]
    high_score = max(score)
    high_score_index = score.index(high_score)

    return high_score, list_of_names[high_score_index]




def get_allocation_data(event: Event) -> AllocationData:
    current_allocation_for_event = load_allocation_for_event(event)
    cadets_at_event_including_non_active = load_cadets_at_event(event)
    list_of_cadets_in_event_active_only = get_list_of_active_cadets_at_event(event)
    list_of_events = get_sorted_list_of_events()
    list_of_previous_events = list_of_events_excluding_one_event(list_of_events=list_of_events,event_to_exclude=event, only_past=True, sort_by=SORT_BY_START_ASC)
    previous_allocations_as_dict = get_dict_of_allocations_for_events_and_list_of_cadets(list_of_events=list_of_previous_events)
    list_of_all_cadets = get_list_of_all_cadets()

    group_allocation_info = get_group_allocation_info(cadets_at_event_including_non_active)

    list_of_dinghies = load_list_of_boat_classes()
    list_of_club_boats = load_list_of_club_dinghies()
    list_of_club_boats_allocated = load_list_of_cadets_at_event_with_club_dinghies(event)
    list_of_cadets_at_event_with_dinghies = load_list_of_cadets_at_event_with_dinghies(event)

    return AllocationData(
        event=event,
        current_allocation_for_event=current_allocation_for_event,
        cadets_at_event_including_non_active=cadets_at_event_including_non_active,
        list_of_cadets_in_event_active_only=list_of_cadets_in_event_active_only,
        previous_allocations_as_dict=previous_allocations_as_dict,
        group_allocation_info=group_allocation_info,
        list_of_dinghies=list_of_dinghies,
        list_of_club_boats=list_of_club_boats,
        list_of_club_boats_allocated=list_of_club_boats_allocated,
        list_of_cadets_at_event_with_dinghies=list_of_cadets_at_event_with_dinghies,
        list_of_all_cadets=list_of_all_cadets
    )



## only return if not all empty values


