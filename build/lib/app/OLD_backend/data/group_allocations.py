from typing import List

from app.objects.cadet_with_id_at_event import CadetWithIdAtEvent

from app.objects.exceptions import missing_data, arg_not_passed

from app.objects.day_selectors import Day, DictOfDaySelectors, DaySelector

from app.objects.cadets import ListOfCadets, Cadet

from app.objects.utils import in_both_x_and_y

from app.objects.events import Event

from app.objects.composed.cadets_at_event_with_groups import ListOfCadetsWithGroupOnDay
from app.objects.groups import Group, unallocated_group
from app.objects.cadet_with_id_with_group_at_event import ListOfCadetIdsWithGroups
from app.OLD_backend.data.cadets_at_event_id_level import CadetsAtEventIdLevelData
from app.data_access.store.data_access import DataLayer


class GroupAllocationsData:
    def __init__(self, data_api: DataLayer):
        self.data_api = data_api

    def groups_given_cadet_id(self, event: Event, cadet_id: str) -> List[Group]:
        list_of_cadets_with_groups = self.list_of_active_cadets_with_groups(event)
        list_of_cadet_with_group_this_cadet = (
            list_of_cadets_with_groups.items_with_cadet_id(cadet_id)
        )
        list_of_groups_this_cadet = [
            cadet_with_group.group
            for cadet_with_group in list_of_cadet_with_group_this_cadet
        ]

        if len(list_of_groups_this_cadet) == 0:
            return [unallocated_group]
        else:
            return list(set(list_of_groups_this_cadet))

    def get_joint_attendance_matrix_for_cadet_ids_in_group_at_event(
        self, event: Event, group: Group, list_of_cadet_ids: List[str] = arg_not_passed
    ):
        if list_of_cadet_ids is arg_not_passed:
            list_of_cadet_ids = (
                self.list_of_cadet_ids_in_a_specific_group_if_cadet_active_at_event(
                    event=event, group=group
                )
            )
        attendance_data = self.cadets_at_event_data.get_attendance_matrix_for_list_of_cadet_ids_at_event(
            event=event, list_of_cadet_ids=list_of_cadet_ids
        )
        attendance_in_group = self.get_attendance_matrix_for_group(
            event=event, list_of_cadet_ids=list_of_cadet_ids, group=group
        )

        joint_attendance = attendance_data.intersect(attendance_in_group)
        joint_attendance = joint_attendance.align_with_list_of_days(
            event.weekdays_in_event()
        )

        return joint_attendance

    def get_attendance_matrix_for_group(
        self, event: Event, group: Group, list_of_cadet_ids: List[str]
    ) -> DictOfDaySelectors:
        list_of_selectors = [
            self.day_selector_for_cadet_id_and_group_at_event(
                event=event, group=group, cadet_id=cadet_id
            )
            for cadet_id in list_of_cadet_ids
        ]

        return DictOfDaySelectors(list_of_selectors)

    def day_selector_for_cadet_id_and_group_at_event(
        self, event: Event, group: Group, cadet_id: str
    ) -> DaySelector:
        list_of_cadet_ids_with_groups = self.CONSIDER_USING_ACTIVE_FILTER_get_list_of_cadet_ids_with_groups_at_event(
            event
        )

        return DaySelector(
            dict(
                [
                    (
                        day,
                        list_of_cadet_ids_with_groups.group_for_cadet_id_on_day(
                            day=day, cadet_id=cadet_id
                        )
                        == group,
                    )
                    for day in event.weekdays_in_event()
                ]
            )
        )

    def remove_cadet_from_data(self, event: Event, cadet_id: str):
        for day in event.weekdays_in_event():
            self.remove_cadet_from_data_on_day(event=event, cadet_id=cadet_id, day=day)

    def remove_cadet_from_data_on_day(self, event: Event, cadet_id: str, day: Day):
        list_of_cadet_ids_with_groups = self.CONSIDER_USING_ACTIVE_FILTER_get_list_of_cadet_ids_with_groups_at_event(
            event
        )
        list_of_cadet_ids_with_groups.remove_group_allocation_for_cadet_on_day(
            cadet_id=cadet_id, day=day
        )
        self.save_list_of_cadet_ids_with_groups_at_event(
            event=event, list_of_cadet_ids_with_groups=list_of_cadet_ids_with_groups
        )

    def add_or_upate_group_for_cadet_on_day_if_cadet_available_on_day(
        self, event: Event, cadet: Cadet, group: Group, day: Day
    ):
        cadet_at_event = self.cadet_at_event_or_missing_data(event, cadet_id=cadet.id)
        if cadet_at_event is missing_data:
            return
        if not cadet_at_event.availability.available_on_day(day):
            return
        if not cadet_at_event.is_active():
            return

        list_of_cadet_ids_with_groups = self.CONSIDER_USING_ACTIVE_FILTER_get_list_of_cadet_ids_with_groups_at_event(
            event
        )
        list_of_cadet_ids_with_groups.update_group_for_cadet_on_day(
            cadet_id=cadet.id, day=day, chosen_group=group
        )
        self.save_list_of_cadet_ids_with_groups_at_event(
            event=event, list_of_cadet_ids_with_groups=list_of_cadet_ids_with_groups
        )

    def get_list_of_groups_at_event(
        self,
        event: Event,
    ) -> List[Group]:
        list_of_cadet_ids_with_groups = self.active_cadet_ids_at_event_with_allocations_including_unallocated_cadets(
            event
        )
        groups = [
            list_of_cadet_ids_with_groups.item_with_cadet_id(cadet_id).group
            for cadet_id in list_of_cadet_ids_with_groups.list_of_ids
        ]
        groups = list(set(groups))
        raise Exception("Can't order groups")
        # return order_list_of_groups(groups)

    def get_list_of_groups_at_event_given_list_of_cadets(
        self, event: Event, list_of_cadets: ListOfCadets
    ) -> List[Group]:
        list_of_cadet_ids_with_groups = self.active_cadet_ids_at_event_with_allocations_including_unallocated_cadets(
            event
        )
        groups = [
            list_of_cadet_ids_with_groups.item_with_cadet_id(cadet_id).group
            for cadet_id in list_of_cadets.list_of_ids
        ]
        groups = list(set(groups))

        raise Exception("Can't order groups")

        # return order_list_of_groups(groups)

    def get_list_of_cadets_with_group_by_day(
        self, event: Event, day: Day, include_unallocated_cadets: bool = True
    ) -> ListOfCadetsWithGroupOnDay:
        if include_unallocated_cadets:
            list_of_cadet_ids_with_groups = self.active_cadet_ids_at_event_with_allocations_including_unallocated_cadets_on_day(
                event=event, day=day
            )
        else:
            list_of_cadet_ids_with_groups = (
                self.active_cadet_ids_at_event_with_allocations_on_day(
                    event=event, day=day
                )
            )

        return (
            self.get_list_of_cadets_with_group_given_list_of_cadets_with_ids_and_groups(
                list_of_cadet_ids_with_groups
            )
        )

    def get_list_of_cadets_with_group_given_list_of_cadets_with_ids_and_groups(
        self,
        list_of_cadet_ids_with_groups: ListOfCadetIdsWithGroups,
    ) -> ListOfCadetsWithGroupOnDay:
        list_of_cadets = self.data_api.get_list_of_cadets()

        try:
            list_of_cadet_with_groups = (
                ListOfCadetsWithGroupOnDay.from_list_of_cadets_and_list_of_allocations(
                    list_of_cadets=list_of_cadets,
                    list_of_allocations=list_of_cadet_ids_with_groups,
                )
            )
        except:
            raise Exception(
                "Cadets in OLD_backend missing from master list of group_allocations"
            )

        return list_of_cadet_with_groups

    def active_cadet_ids_at_event_with_allocations_including_unallocated_cadets(
        self, event: Event
    ) -> ListOfCadetIdsWithGroups:
        list_of_cadet_ids_with_groups = self.active_cadet_ids_at_event_with_allocations(
            event
        )
        return self.active_cadet_ids_at_event_for_unallocated_cadets(
            event=event, list_of_cadet_ids_with_groups=list_of_cadet_ids_with_groups
        )

    def active_cadet_ids_at_event_for_unallocated_cadets(
        self,
        event: Event,
        list_of_cadet_ids_with_groups: ListOfCadetIdsWithGroups = arg_not_passed,
    ) -> ListOfCadetIdsWithGroups:
        if list_of_cadet_ids_with_groups is arg_not_passed:
            list_of_cadet_ids_with_groups = ListOfCadetIdsWithGroups([])
        unallocated_cadets = self.unallocated_cadets_at_event(event)
        for day in event.weekdays_in_event():
            list_of_cadet_ids_with_groups.add_list_of_unallocated_cadets_on_day(
                unallocated_cadets, day=day
            )

        return list_of_cadet_ids_with_groups

    def active_cadet_ids_at_event_with_allocations_including_unallocated_cadets_on_day(
        self, event: Event, day: Day
    ) -> ListOfCadetIdsWithGroups:
        list_of_cadet_ids_with_groups = (
            self.active_cadet_ids_at_event_with_allocations_on_day(event=event, day=day)
        )
        unallocated_cadets = self.unallocated_cadets_at_event_available_on_day(
            event=event, day=day
        )
        list_of_cadet_ids_with_groups.add_list_of_unallocated_cadets_on_day(
            unallocated_cadets, day=day
        )

        return list_of_cadet_ids_with_groups

    def active_cadet_ids_with_groups_for_group_at_event(
        self, event: Event, group: Group
    ) -> ListOfCadetIdsWithGroups:
        cadet_ids = self.list_of_cadet_ids_in_a_specific_group_if_cadet_active_at_event(
            event=event, group=group
        )
        list_of_cadets_with_groups = self.CONSIDER_USING_ACTIVE_FILTER_get_list_of_cadet_ids_with_groups_at_event(
            event
        )
        list_of_allocated_cadets_with_groups_in_group = [
            cadet_with_group
            for cadet_with_group in list_of_cadets_with_groups
            if cadet_with_group.cadet_id in cadet_ids
            and cadet_with_group.group == group
        ]

        return ListOfCadetIdsWithGroups(list_of_allocated_cadets_with_groups_in_group)

    def active_cadet_ids_at_event_with_allocations(
        self, event: Event
    ) -> ListOfCadetIdsWithGroups:
        list_of_cadets_with_groups = self.CONSIDER_USING_ACTIVE_FILTER_get_list_of_cadet_ids_with_groups_at_event(
            event
        )
        list_of_active_cadet_ids_at_event = (
            self.cadets_at_event_data.list_of_active_cadet_ids_at_event(event)
        )

        list_of_allocated_cadets_with_groups = [
            cadet_with_group
            for cadet_with_group in list_of_cadets_with_groups
            if cadet_with_group.cadet_id in list_of_active_cadet_ids_at_event
        ]

        return ListOfCadetIdsWithGroups(list_of_allocated_cadets_with_groups)

    def active_cadet_ids_at_event_with_allocations_on_day(
        self, event: Event, day: Day
    ) -> ListOfCadetIdsWithGroups:
        list_of_cadets_with_groups = (
            self.get_list_of_cadet_ids_with_groups_at_event_on_day(event=event, day=day)
        )
        list_of_active_cadet_ids_at_event = (
            self.cadets_at_event_data.list_of_active_cadets_at_event_available_on_day(
                day=day, event=event
            ).list_of_cadet_ids()
        )

        list_of_allocated_cadets_with_groups = [
            cadet_with_group
            for cadet_with_group in list_of_cadets_with_groups
            if cadet_with_group.cadet_id in list_of_active_cadet_ids_at_event
        ]

        return ListOfCadetIdsWithGroups(list_of_allocated_cadets_with_groups)

    def unallocated_cadets_at_event_available_on_day(
        self, event: Event, day: Day
    ) -> ListOfCadets:
        list_of_cadets_in_groups_at_event_on_day = (
            self.get_list_of_cadet_ids_with_groups_at_event_on_day(event=event, day=day)
        )
        list_of_active_cadets_at_event_on_day = (
            self.list_of_active_cadets_at_event_on_day(event=event, day=day)
        )

        unallocated_cadet_ids = list_of_cadets_in_groups_at_event_on_day.cadets_in_passed_list_not_allocated_to_any_group(
            list_of_cadets=list_of_active_cadets_at_event_on_day
        )
        return unallocated_cadet_ids

    def unallocated_cadets_at_event(self, event: Event) -> ListOfCadets:
        list_of_cadets_in_groups_at_event = self.CONSIDER_USING_ACTIVE_FILTER_get_list_of_cadet_ids_with_groups_at_event(
            event
        )
        list_of_active_cadets_at_event = self.list_of_active_cadets_at_event(event)

        unallocated_cadet_ids = list_of_cadets_in_groups_at_event.cadets_in_passed_list_not_allocated_to_any_group(
            list_of_cadets=list_of_active_cadets_at_event
        )
        return unallocated_cadet_ids

    def list_of_cadet_ids_in_a_specific_group_if_cadet_active_at_event(
        self, event: Event, group: Group
    ) -> List[str]:
        list_of_cadets_with_groups = self.CONSIDER_USING_ACTIVE_FILTER_get_list_of_cadet_ids_with_groups_at_event(
            event
        )
        list_of_cadet_ids_in_group = (
            list_of_cadets_with_groups.unique_list_of_cadet_ids(group)
        )
        list_of_active_cadet_ids_at_event = (
            self.cadets_at_event_data.list_of_active_cadet_ids_at_event(event)
        )

        return in_both_x_and_y(
            list_of_active_cadet_ids_at_event, list_of_cadet_ids_in_group
        )

    def list_of_active_cadets_with_groups(
        self, event: Event
    ) -> ListOfCadetsWithGroupOnDay:
        list_of_cadet_ids_with_groups = self.CONSIDER_USING_ACTIVE_FILTER_get_list_of_cadet_ids_with_groups_at_event(
            event
        )
        list_of_active_cadet_ids_at_event = (
            self.cadets_at_event_data.list_of_active_cadet_ids_at_event(event)
        )

        list_of_cadet_ids_with_groups = ListOfCadetIdsWithGroups(
            [
                cadet_with_group
                for cadet_with_group in list_of_cadet_ids_with_groups
                if cadet_with_group.cadet_id in list_of_active_cadet_ids_at_event
            ]
        )

        return (
            self.get_list_of_cadets_with_group_given_list_of_cadets_with_ids_and_groups(
                list_of_cadet_ids_with_groups=list_of_cadet_ids_with_groups
            )
        )

    def get_list_of_cadet_ids_with_groups_at_event_on_day(
        self, event: Event, day: Day
    ) -> ListOfCadetIdsWithGroups:
        list_of_cadet_id_with_group = self.CONSIDER_USING_ACTIVE_FILTER_get_list_of_cadet_ids_with_groups_at_event(
            event=event
        )

        return list_of_cadet_id_with_group.subset_for_day(day)

    def cadet_at_event_or_missing_data(
        self, event: Event, cadet_id: str
    ) -> CadetWithIdAtEvent:
        return self.cadets_at_event_data.cadet_at_event_or_missing_data(
            event=event, cadet_id=cadet_id
        )

    def list_of_active_cadets_at_event(self, event: Event) -> ListOfCadets:
        return self.cadets_at_event_data.list_of_active_cadets_at_event(event)

    def list_of_active_cadets_at_event_on_day(
        self, event: Event, day: Day
    ) -> ListOfCadets:
        return self.cadets_at_event_data.list_of_active_cadets_available_on_day(
            event=event, day=day
        )

    def CONSIDER_USING_ACTIVE_FILTER_get_list_of_cadet_ids_with_groups_at_event(
        self, event: Event
    ) -> ListOfCadetIdsWithGroups:
        return self.data_api.get_list_of_cadets_with_groups_at_event(event)

    def save_list_of_cadet_ids_with_groups_at_event(
        self, event: Event, list_of_cadet_ids_with_groups: ListOfCadetIdsWithGroups
    ):
        self.data_api.save_list_of_cadets_with_groups_at_event(
            list_of_cadets_with_groups_at_event=list_of_cadet_ids_with_groups,
            event=event,
        )

    @property
    def cadets_at_event_data(self) -> CadetsAtEventIdLevelData:
        return CadetsAtEventIdLevelData(data_api=self.data_api)
