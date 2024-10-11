from typing import List, Union

from app.objects_OLD.volunteers_at_event import DEPRECATE_VolunteerAtEvent
from app.objects_OLD.primtive_with_id.volunteer_at_event import VolunteerAtEventWithId

from app.objects.volunteers import Volunteer, ListOfVolunteers

from app.OLD_backend.data.volunteer_allocation import VolunteerAllocationData
from app.OLD_backend.data.volunteers import VolunteerData
from app.objects_OLD.volunteers_in_roles import (
    DEPRECATE_VolunteerWithRoleAtEvent, DEPRECATE_ListOfVolunteersWithRoleAtEvent
)
from app.objects_OLD.primtive_with_id.volunteer_role_targets import ListOfTargetForRoleAtEvent
from app.objects_OLD.primtive_with_id.volunteer_roles_and_groups import VolunteerWithIdInRoleAtEvent, \
    ListOfVolunteersWithIdInRoleAtEvent, RoleAndGroup

from app.data_access.store.data_layer import DataLayer

from app.objects.exceptions import missing_data
from app.objects.day_selectors import Day
from app.objects.events import Event
from app.objects.groups import Group


class VolunteerRotaData:
    def __init__(self, data_api: DataLayer):
        self.data_api = data_api

    def volunteer_is_on_lake(self, event: Event, volunteer_id: str) -> bool:
        list_of_volunteers = self.get_list_of_volunteers_in_roles_at_event(event)
        subset_for_volunteer = list_of_volunteers.list_if_volunteer_id_in_list_of_ids(
            [volunteer_id]
        )

        return any(
            [volunteer_in_role.on_lake() for volunteer_in_role in subset_for_volunteer]
        )

    def save_new_volunteer_target(self, event: Event, role: str, target: int):
        list_of_targets_for_role_at_event = self.get_list_of_targets_for_role_at_event(
            event=event
        )
        list_of_targets_for_role_at_event.set_target_for_role(role=role, target=target)
        self.save_list_of_targets_for_role_at_event(
            event=event,
            list_of_targets_for_role_at_event=list_of_targets_for_role_at_event,
        )

    def is_senior_instructor(self, event: Event, volunteer_id: str) -> bool:
        all_roles = [
            self.get_volunteer_with_id_in_role_at_event_on_day_from_id(
                event=event, day=day, volunteer_id=volunteer_id
            )
            for day in event.weekdays_in_event()
        ]
        is_si = [role.senior_instructor() for role in all_roles]
        return any(is_si)

    def get_list_of_groups_volunteer_is_instructor_for(
        self, event: Event, volunteer_id: str
    ) -> List[Group]:
        all_roles = [
            self.get_volunteer_with_id_in_role_at_event_on_day_from_id(
                event=event, day=day, volunteer_id=volunteer_id
            )
            for day in event.weekdays_in_event()
        ]
        all_valid_groups = [
            role.group for role in all_roles if role.in_instructor_team()
        ]
        all_valid_groups = list(set(all_valid_groups))
        raise Exception("Can't order groups")

        #return order_list_of_groups(all_valid_groups)

    def delete_role_at_event_for_volunteer_on_all_days(
        self, volunteer_id: str, event: Event
    ):
        for day in event.weekdays_in_event():
            self.delete_role_at_event_for_volunteer_with_id_on_day(
                event=event, day=day, volunteer_id=volunteer_id
            )


    def delete_role_at_event_for_volunteer_on_day(
        self, volunteer: Volunteer, day: Day, event: Event
    ):
        self.delete_role_at_event_for_volunteer_with_id_on_day(event=event,
                                                               volunteer_id=volunteer.id,
                                                               day=day)

    def delete_role_at_event_for_volunteer_with_id_on_day(
        self, volunteer_id: str, day: Day, event: Event
    ):
        volunteer_in_role_at_event_on_day = VolunteerWithIdInRoleAtEvent(
            volunteer_id=volunteer_id, day=day
        )

        list_of_volunteers_in_roles_at_event = (
            self.get_list_of_volunteers_in_roles_at_event(event)
        )
        list_of_volunteers_in_roles_at_event.delete_volunteer_in_role_at_event_on_day(
            volunteer_in_role_at_event=volunteer_in_role_at_event_on_day
        )
        self.save_list_of_volunteers_in_roles_at_event(
            list_of_volunteers_in_role_at_event=list_of_volunteers_in_roles_at_event,
            event=event,
        )

    def update_role_and_group_at_event_for_volunteer_on_all_days_when_available(
        self, volunteer_at_event: DEPRECATE_VolunteerAtEvent, new_role_and_group: RoleAndGroup
    ):
        event = volunteer_at_event.event
        list_of_volunteers_in_roles_at_event = (
            self.get_list_of_volunteers_in_roles_at_event(event)
        )

        for day in self.days_at_event_when_volunteer_available(
            event=event, volunteer_id=volunteer_at_event.volunteer_id
        ):
            volunteer_in_role_at_event = list_of_volunteers_in_roles_at_event.member_matching_volunteer_id_and_day(
                volunteer_id=volunteer_at_event.volunteer_id, day=day
            )
            list_of_volunteers_in_roles_at_event.update_volunteer_in_role_on_day(
                volunteer_in_role_at_event=volunteer_in_role_at_event,
                new_role=new_role_and_group.role,
            )
            list_of_volunteers_in_roles_at_event.update_volunteer_in_group_on_day(
                volunteer_in_role_at_event=volunteer_in_role_at_event,
                new_group=new_role_and_group.group,
            )

        self.save_list_of_volunteers_in_roles_at_event(
            list_of_volunteers_in_role_at_event=list_of_volunteers_in_roles_at_event,
            event=event,
        )

    def swap_roles_and_groups_for_volunteers_in_allocation(
        self,
        event: Event,
        original_day: Day,
        original_volunteer_id: str,
        day_to_swap_with: Day,
        volunteer_id_to_swap_with: str,
    ):
        volunteers_in_role_at_event = self.get_list_of_volunteers_in_roles_at_event(
            event
        )
        volunteers_in_role_at_event.swap_roles_and_groups_for_volunteers_in_allocation(
            original_volunteer_id=original_volunteer_id,
            original_day=original_day,
            day_to_swap_with=day_to_swap_with,
            volunteer_id_to_swap_with=volunteer_id_to_swap_with,
        )
        self.save_list_of_volunteers_in_roles_at_event(
            list_of_volunteers_in_role_at_event=volunteers_in_role_at_event, event=event
        )

    def swap_roles_for_volunteers_in_allocation(
        self,
        event: Event,
        original_volunteer_id: str,
        original_day: Day,
        day_to_swap_with: Day,
        volunteer_id_to_swap_with: str,
    ):
        volunteers_in_role_at_event = self.get_list_of_volunteers_in_roles_at_event(
            event
        )
        volunteers_in_role_at_event.swap_roles_for_volunteers_in_allocation(
            original_volunteer_id=original_volunteer_id,
            original_day=original_day,
            day_to_swap_with=day_to_swap_with,
            volunteer_id_to_swap_with=volunteer_id_to_swap_with,
        )
        self.save_list_of_volunteers_in_roles_at_event(
            list_of_volunteers_in_role_at_event=volunteers_in_role_at_event, event=event
        )

    def copy_across_duties_for_volunteer_at_event_from_one_day_to_all_other_days(
        self, volunteer_at_event: DEPRECATE_VolunteerAtEvent, day: Day, allow_replacement: bool = True
    ):
        list_of_volunteers_in_roles_at_event = (
            self.get_list_of_volunteers_in_roles_at_event(volunteer_at_event.event)
        )
        list_of_volunteers_in_roles_at_event.copy_across_duties_for_volunteer_at_event_from_one_day_to_all_other_days(
            volunteer_id=volunteer_at_event.volunteer_id,
            day=day,
            list_of_all_days=self.days_at_event_when_volunteer_available(
                event=volunteer_at_event.event,
                volunteer_id=volunteer_at_event.volunteer_id,
            ),
            allow_replacement=allow_replacement,
        )
        self.save_list_of_volunteers_in_roles_at_event(
            list_of_volunteers_in_role_at_event=list_of_volunteers_in_roles_at_event,
            event=volunteer_at_event.event,
        )

    def days_at_event_when_volunteer_available(
        self, event: Event, volunteer_id: str
    ) -> List[Day]:
        volunteer_at_event = self.volunteer_allocation_data.get_volunteer_at_this_event(
            event=event, volunteer_id=volunteer_id
        )
        all_days = [
            day
            for day in event.weekdays_in_event()
            if volunteer_at_event.availablity.available_on_day(day)
        ]

        return all_days

    def update_group_at_event_for_volunteer_on_day(
        self,
        volunteer_in_role_at_event_on_day: VolunteerWithIdInRoleAtEvent,
        new_group: Group,
        event: Event,
    ):
        list_of_volunteers_in_roles_at_event = (
            self.get_list_of_volunteers_in_roles_at_event(event)
        )
        list_of_volunteers_in_roles_at_event.update_volunteer_in_group_on_day(
            volunteer_in_role_at_event=volunteer_in_role_at_event_on_day,
            new_group=new_group,
        )
        self.save_list_of_volunteers_in_roles_at_event(
            list_of_volunteers_in_role_at_event=list_of_volunteers_in_roles_at_event,
            event=event,
        )

    def update_role_at_event_for_volunteer_on_day_at_event(
        self,
        event: Event,
        volunteer_in_role_at_event_on_day: VolunteerWithIdInRoleAtEvent,
        new_role: str,
    ):
        list_of_volunteers_in_roles_at_event = (
            self.get_list_of_volunteers_in_roles_at_event(event)
        )
        list_of_volunteers_in_roles_at_event.update_volunteer_in_role_on_day(
            volunteer_in_role_at_event=volunteer_in_role_at_event_on_day,
            new_role=new_role,
        )
        self.save_list_of_volunteers_in_roles_at_event(
            list_of_volunteers_in_role_at_event=list_of_volunteers_in_roles_at_event,
            event=event,
        )

    def get_volunteer_ids_in_boat_related_roles_on_day_of_event(
        self, event: Event, day: Day
    ) -> List[str]:
        volunteers_in_role_at_event = (
            self.get_volunteers_with_id_in_role_at_event_who_are_also_allocated_to_event(event)
        )
        volunteer_ids_in_boat_related_roles_on_day_of_event = volunteers_in_role_at_event.list_of_volunteer_ids_in_boat_related_role_on_day(
            day
        )

        return volunteer_ids_in_boat_related_roles_on_day_of_event

    def get_volunteer_ids_in_boat_related_roles_on_any_day_of_event(
        self, event: Event
    ) -> List[str]:
        volunteers_in_role_at_event = (
            self.get_volunteers_with_id_in_role_at_event_who_are_also_allocated_to_event(event)
        )
        volunteer_ids_in_boat_related_roles_on_any_day_of_event = (
            volunteers_in_role_at_event.list_of_volunteer_ids_in_boat_related_role_on_any_day()
        )

        return volunteer_ids_in_boat_related_roles_on_any_day_of_event


    def get_volunteer_role_and_group_event_on_day_for_volunteer_at_event(
        self, event: Event, volunteer_at_event: Union[VolunteerAtEventWithId, DEPRECATE_VolunteerAtEvent], day: Day
    ) -> RoleAndGroup:
        volunteer_with_role = self.get_volunteer_with_role_at_event_on_day_for_volunteer_at_event(
            event=event,
            volunteer_at_event=volunteer_at_event,
            day=day
        )

        return volunteer_with_role.role_and_group


    def get_volunteer_with_role_at_event_on_day_for_volunteer_at_event(
        self, event: Event, volunteer_at_event: Union[VolunteerAtEventWithId, DEPRECATE_VolunteerAtEvent], day: Day
    ) -> VolunteerWithIdInRoleAtEvent:
        return self.get_volunteer_with_id_in_role_at_event_on_day_from_id(
            event=event, volunteer_id=volunteer_at_event.volunteer_id, day=day
        )


    def get_volunteer_role_at_event_on_day_for_volunteer_id(
        self, event: Event, volunteer_id: str, day: Day, default=missing_data
    ) -> str:
        volunteer_in_role = self.get_volunteer_with_id_in_role_at_event_on_day_from_id(
            event=event, day=day, volunteer_id=volunteer_id
        )
        if volunteer_in_role is missing_data:
            return default

        return volunteer_in_role.role

    def get_volunteer_group_name_at_event_on_day(
        self,
        event: Event,
        volunteer_id: str,
        day: Day,
        default_if_missing="",
        default_if_unallocated="",
    ) -> str:
        volunteer_in_role = self.get_volunteer_with_id_in_role_at_event_on_day_from_id(
            event=event, day=day, volunteer_id=volunteer_id
        )
        if volunteer_in_role is missing_data:
            return default_if_missing

        group = volunteer_in_role.group
        if group.is_unallocated:
            return default_if_unallocated

        return group.name

    def volunteer_has_at_least_one_allocated_role_which_matches_others(
        self, event: Event, volunteer_id: str
    ) -> bool:
        list_of_volunteers_in_roles = (
            self.get_list_of_volunteers_in_roles_at_event_for_volunteer(
                event=event, volunteer_id=volunteer_id
            )
        )
        if len(list_of_volunteers_in_roles) == 0:
            return False
        return list_of_volunteers_in_roles.count(list_of_volunteers_in_roles[0]) == len(
            list_of_volunteers_in_roles
        )

    def volunteer_has_at_least_one_allocated_role_and_empty_spaces_to_fill(
        self, event: Event, volunteer_id: str
    ) -> bool:
        list_of_volunteers_in_roles = (
            self.get_list_of_volunteers_in_roles_at_event_for_volunteer(
                event=event, volunteer_id=volunteer_id
            )
        )
        available_days = self.days_at_event_when_volunteer_available(
            event=event, volunteer_id=volunteer_id
        )
        empty_spaces = len(available_days) - len(list_of_volunteers_in_roles)
        at_least_one_allocated = len(list_of_volunteers_in_roles) > 0
        has_empty_spaces = empty_spaces > 0

        return at_least_one_allocated and has_empty_spaces

    def get_list_of_volunteers_in_roles_at_event_for_volunteer(
        self, event: Event, volunteer_id: str
    ) -> List[VolunteerWithIdInRoleAtEvent]:
        list_of_volunteers_in_roles = [
            self.get_volunteer_with_id_in_role_at_event_on_day_from_id(
                event=event, day=day, volunteer_id=volunteer_id
            )
            for day in event.weekdays_in_event()
        ]
        list_of_volunteers_in_roles = [
            volunteer_in_role
            for volunteer_in_role in list_of_volunteers_in_roles
            if not volunteer_in_role.no_role_set
        ]

        return list_of_volunteers_in_roles

    def get_volunteer_with_role_at_event_on_day_from_volunteer(
        self, event: Event, volunteer: Volunteer, day: Day
    ) -> VolunteerWithIdInRoleAtEvent:
        return self.get_volunteer_with_id_in_role_at_event_on_day_from_id(event=event,
                                                                          volunteer_id=volunteer.id,
                                                                          day=day
                                                                          )

    def get_volunteer_with_id_in_role_at_event_on_day_from_id(
        self, event: Event, volunteer_id: str, day: Day
    ) -> VolunteerWithIdInRoleAtEvent:
        volunteers_in_roles_at_event = (
            self.get_volunteers_with_id_in_role_at_event_who_are_also_allocated_to_event(event)
        )
        volunteer_in_role = (
            volunteers_in_roles_at_event.member_matching_volunteer_id_and_day(
                volunteer_id=volunteer_id, day=day
            )
        )

        return volunteer_in_role

    def get_volunteers_with_in_role_at_event_who_are_also_allocated_to_event(
        self, event: Event
    ) -> DEPRECATE_ListOfVolunteersWithRoleAtEvent:

        volunteers_with_ids_in_roles_and_at_event= self.get_volunteers_with_id_in_role_at_event_who_are_also_allocated_to_event(
            event=event
        )
        list_of_volunteers = self.get_list_of_all_volunteers()

        return DEPRECATE_ListOfVolunteersWithRoleAtEvent(
            [
                DEPRECATE_VolunteerWithRoleAtEvent.from_volunteer_with_id_in_role_at_event(
                    volunteer_with_id_in_role_at_event=volunteer_with_id_in_role_at_event,
                    volunteer=list_of_volunteers.volunteer_with_id(volunteer_with_id_in_role_at_event.volunteer_id)
                )

                for volunteer_with_id_in_role_at_event in volunteers_with_ids_in_roles_and_at_event
            ]
        )

    def get_volunteers_with_id_in_role_at_event_who_are_also_allocated_to_event(
        self, event: Event
    ) -> ListOfVolunteersWithIdInRoleAtEvent:
        list_of_volunteers_at_event = (
            self.volunteer_allocation_data.load_list_of_volunteers_with_ids_at_event(
                event
            )
        )
        list_of_volunteer_ids_at_event = (
            list_of_volunteers_at_event.list_of_volunteer_ids
        )
        list_of_volunteers_in_role_at_event = (
            self.get_list_of_volunteers_in_roles_at_event(event)
        )
        volunteers_in_roles_and_at_event = (
            list_of_volunteers_in_role_at_event.list_if_volunteer_id_in_list_of_ids(
                list_of_volunteer_ids_at_event
            )
        )

        return volunteers_in_roles_and_at_event

    def get_list_of_volunteers_in_roles_at_event(
        self, event: Event
    ) -> ListOfVolunteersWithIdInRoleAtEvent:
        return self.data_api.get_list_of_volunteers_in_roles_at_event(event=event)

    def save_list_of_volunteers_in_roles_at_event(
        self,
        event: Event,
        list_of_volunteers_in_role_at_event: ListOfVolunteersWithIdInRoleAtEvent,
    ):
        self.data_api.save_list_of_volunteers_in_roles_at_event(
            event=event,
            list_of_volunteers_in_role_at_event=list_of_volunteers_in_role_at_event,
        )

    def get_list_of_targets_for_role_at_event(
        self, event: Event
    ) -> ListOfTargetForRoleAtEvent:
        return self.data_api.get_list_of_targets_for_role_at_event(event)

    def save_list_of_targets_for_role_at_event(
        self,
        list_of_targets_for_role_at_event: ListOfTargetForRoleAtEvent,
        event: Event,
    ):
        self.data_api.save_list_of_targets_for_role_at_event(
            list_of_targets_for_role_at_event=list_of_targets_for_role_at_event,
            event=event,
        )

    def get_list_of_all_volunteers(self) -> ListOfVolunteers:
        return self.volunteer_data.get_list_of_volunteers()

    @property
    def volunteer_allocation_data(self) -> VolunteerAllocationData:
        return VolunteerAllocationData(self.data_api)


    @property
    def volunteer_data(self) -> VolunteerData:
        return VolunteerData(self.data_api)