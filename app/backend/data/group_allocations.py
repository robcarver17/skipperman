from typing import List

import pandas as pd
from app.objects.cadets import ListOfCadets

from app.objects.utils import in_both_x_and_y

from app.objects.events import Event

from app.objects.groups import ListOfCadetIdsWithGroups, Group, ListOfCadetsWithGroup
from app.backend.data.cadets_at_event import CadetsAtEventData
from app.backend.data.cadets import CadetData
from app.data_access.storage_layer.api import DataLayer

class GroupAllocationsData():
    def __init__(self, data_api: DataLayer):
        self.data_api = data_api

    def get_list_of_groups_at_event(self,
                                                         event: Event,
                                                         ) -> List[Group]:

        list_of_cadet_ids_with_groups = self.active_cadet_ids_at_event_with_allocations_including_unallocated_cadets(event)
        groups = [list_of_cadet_ids_with_groups.item_with_cadet_id(cadet_id).group for cadet_id in list_of_cadet_ids_with_groups.list_of_ids]
        return list(set(groups))

    def get_list_of_groups_at_event_given_list_of_cadets(self,
                                                         event: Event,
                                                         list_of_cadets: ListOfCadets) -> List[Group]:

        list_of_cadet_ids_with_groups = self.active_cadet_ids_at_event_with_allocations_including_unallocated_cadets(event)
        groups = [list_of_cadet_ids_with_groups.item_with_cadet_id(cadet_id).group for cadet_id in list_of_cadets.list_of_ids]
        return list(set(groups))

    def get_list_of_cadets_with_group_at_event(self, event: Event, include_unallocated_cadets: bool = True)-> ListOfCadetsWithGroup:
        if include_unallocated_cadets:
            list_of_cadet_ids_with_groups = self.active_cadet_ids_at_event_with_allocations_including_unallocated_cadets(event)
        else:
            list_of_cadet_ids_with_groups = self.active_cadet_ids_at_event_with_allocations(event)

        return self.get_list_of_cadets_with_group_given_list_of_cadets_with_ids_and_groups(list_of_cadet_ids_with_groups)

    def get_list_of_cadets_with_group_given_list_of_cadets_with_ids_and_groups(self,
                                                                               list_of_cadet_ids_with_groups: ListOfCadetIdsWithGroups,
                                                                               ) -> ListOfCadetsWithGroup:
        list_of_cadets = self.data_api.get_list_of_cadets()

        try:
            list_of_cadet_with_groups = (
                ListOfCadetsWithGroup.from_list_of_cadets_and_list_of_allocations(
                    list_of_cadets=list_of_cadets,
                    list_of_allocations=list_of_cadet_ids_with_groups,
                )
            )
        except:
            raise Exception("Cadets in backend missing from master list of group_allocations")

        return list_of_cadet_with_groups

    def active_cadet_ids_at_event_with_allocations_including_unallocated_cadets(self, event: Event) -> ListOfCadetIdsWithGroups:
        list_of_cadet_ids_with_groups = self.active_cadet_ids_at_event_with_allocations(event)
        unallocated_cadets = self.unallocated_cadets_at_event(event)
        list_of_cadet_ids_with_groups.add_list_of_unallocated_cadets(unallocated_cadets)

        return list_of_cadet_ids_with_groups

    def active_cadet_ids_at_event_with_allocations(self, event: Event) -> ListOfCadetIdsWithGroups:

        list_of_cadets_with_groups = self.list_of_cadets_with_groups_at_event(event)
        list_of_active_cadet_ids_at_event = self.cadets_at_event_data.list_of_active_cadet_ids_at_event(event)

        list_of_allocated_cadets_with_groups = [cadet_with_group for cadet_with_group in list_of_cadets_with_groups
                                                if cadet_with_group.cadet_id in list_of_active_cadet_ids_at_event]

        return ListOfCadetIdsWithGroups(list_of_allocated_cadets_with_groups)

    def unallocated_cadets_at_event(self, event: Event) -> ListOfCadets:
        list_of_cadets_in_groups_at_event = self.list_of_cadets_with_groups_at_event(event)
        list_of_active_cadets_at_event = self.list_of_active_cadets_at_event(event)

        unallocated_cadet_ids = (
            list_of_cadets_in_groups_at_event.cadets_in_passed_list_not_allocated_to_any_group(
                list_of_cadets=list_of_active_cadets_at_event
            )
        )
        return unallocated_cadet_ids

    def list_of_cadet_ids_in_a_specific_group_if_cadet_active_at_event(self, event: Event, group: Group):
        list_of_cadets_with_groups = self.list_of_cadets_with_groups_at_event(event)
        list_of_cadet_ids_in_group= list_of_cadets_with_groups.list_of_cadet_ids_in_group(group)
        list_of_active_cadet_ids_at_event = self.cadets_at_event_data.list_of_active_cadet_ids_at_event(event)

        return in_both_x_and_y(list_of_active_cadet_ids_at_event, list_of_cadet_ids_in_group)

    def list_of_active_cadets_at_event(self, event: Event) -> ListOfCadets:
        return self.cadets_at_event_data.list_of_active_cadets_at_event(event)

    def list_of_cadets_with_groups_at_event(self, event: Event) -> ListOfCadetIdsWithGroups:
        return self.data_api.get_list_of_cadets_with_groups_at_event(event)

    @property
    def cadets_at_event_data(self) ->CadetsAtEventData:
        return CadetsAtEventData(data_api=self.data_api)

