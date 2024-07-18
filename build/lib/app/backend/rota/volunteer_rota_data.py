from dataclasses import dataclass
from typing import Dict, List

import pandas as pd

from app.OLD_backend.rota.sorting_and_filtering import filtered_list_of_volunteers_at_event, filter_volunteer, \
    RotaSortsAndFilters
from app.data_access.data_layer.ad_hoc_cache import AdHocCache

from app.OLD_backend.rota.volunteer_history import DEPRECATE_get_dict_of_volunteers_with_last_roles, \
    get_dict_of_volunteers_with_last_roles
from app.data_access.data_layer.data_layer import DataLayer

from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.OLD_backend.group_allocations.cadet_event_allocations import (
    DEPRECATE_load_list_of_cadets_ids_with_group_allocations_active_cadets_only,
    DEPRECATE_get_list_of_cadets_unallocated_to_group_at_event,
    load_list_of_cadets_ids_with_group_allocations_active_cadets_only,
    get_list_of_cadets_unallocated_to_group_at_event,
)
from app.OLD_backend.volunteers.volunteers import (
    load_list_of_volunteer_skills,
    get_list_of_all_volunteers,
)
from app.OLD_backend.rota.volunteer_rota import (
    DEPRECATE_load_list_of_volunteers_at_event,
    DEPRECATE_get_volunteers_in_role_at_event_with_active_allocations,
    get_volunteers_in_role_at_event_with_active_allocations,
    load_list_of_volunteers_at_event,
    load_list_of_volunteers_with_ids_at_event,
    sort_volunteer_data_for_event_by_name_sort_order,
)

from app.objects.cadets import ListOfCadets
from app.objects.exceptions import missing_data, arg_not_passed
from app.objects.day_selectors import Day
from app.objects.events import (
    Event,
)
from app.objects.primtive_with_id.groups import sorted_locations, Group, GROUP_UNALLOCATED, ListOfCadetIdsWithGroups
from app.objects.primtive_with_id.volunteers import Volunteer, ListOfVolunteers
from app.objects.primtive_with_id.volunteer_skills import ListOfVolunteerSkills, SkillsDict
from app.objects.volunteers_at_event import (
    ListOfVolunteersAtEvent, )
from app.objects.primtive_with_id.volunteer_at_event import VolunteerAtEventWithId, ListOfVolunteersAtEventWithId
from app.objects.primtive_with_id.volunteer_roles_and_groups import VolunteerWithIdInRoleAtEvent, \
    ListOfVolunteersWithIdInRoleAtEvent, RoleAndGroup


@dataclass
class DEPRECATE_DataToBeStoredWhilstConstructingVolunteerRotaPage:
    event: Event
    list_of_cadet_ids_with_groups: ListOfCadetIdsWithGroups
    unallocated_cadets_at_event: ListOfCadets
    volunteer_skills: ListOfVolunteerSkills
    volunteers_in_roles_at_event: ListOfVolunteersWithIdInRoleAtEvent
    list_of_volunteers_with_id_at_event: ListOfVolunteersAtEventWithId
    dict_of_volunteers_with_last_roles: Dict[str, RoleAndGroup]
    all_volunteers: ListOfVolunteers

    def filtered_list_of_volunteers_at_event(
        self, sorts_and_filters: RotaSortsAndFilters
    ) -> ListOfVolunteersAtEventWithId:
        skills_filter = sorts_and_filters.skills_filter
        original_list = self.list_of_volunteers_with_id_at_event
        volunteer_skills = self.volunteer_skills
        availability_filter_dict = sorts_and_filters.availability_filter
        list_of_volunteers_in_roles_at_event = self.volunteers_in_roles_at_event

        new_list = ListOfVolunteersAtEventWithId(
            [
                volunteer
                for volunteer in original_list
                if filter_volunteer(
                    volunteer,
                    list_of_volunteers_in_roles_at_event=list_of_volunteers_in_roles_at_event,
                    skills_filter=skills_filter,
                    volunteer_skills=volunteer_skills,
                    availability_filter_dict=availability_filter_dict,
                )
            ]
        )

        return new_list

    def group_given_cadet_id(self, cadet_id):
        try:
            cadet_with_group = self.list_of_cadet_ids_with_groups.item_with_cadet_id(
                cadet_id
            )
            return cadet_with_group.group
        except:
            try:
                __unallocated_cadet_unused = (
                    self.unallocated_cadets_at_event.object_with_id(cadet_id)
                )
                return GROUP_UNALLOCATED
            except:
                return missing_data

    def dict_of_skills_given_volunteer_id(self, volunteer_id: str) -> SkillsDict:
        return self.volunteer_skills.dict_of_skills_for_volunteer_id(volunteer_id)

    def volunteer_in_role_at_event_on_day(
        self, volunteer_id: str, day: Day
    ) -> VolunteerWithIdInRoleAtEvent:
        return self.volunteers_in_roles_at_event.member_matching_volunteer_id_and_day(
            volunteer_id=volunteer_id, day=day
        )

    def previous_role_and_group_for_volunteer(
        self, volunteer_at_event: VolunteerAtEventWithId
    ) -> RoleAndGroup:
        return self.dict_of_volunteers_with_last_roles.get(
            volunteer_at_event.volunteer_id, RoleAndGroup()
        )

    def all_roles_match_across_event(self, volunteer_id: str) -> bool:
        availability = (
            self.list_of_volunteers_with_id_at_event.volunteer_at_event_with_id(
                volunteer_id=volunteer_id
            ).availablity
        )
        all_volunteers_in_roles_at_event_including_no_role_set = [
            self.volunteer_in_role_at_event_on_day(volunteer_id=volunteer_id, day=day)
            for day in availability.days_available()
        ]

        if len(all_volunteers_in_roles_at_event_including_no_role_set) == 0:
            return False

        all_roles = [
            volunteer_in_role_at_event_on_day.role
            for volunteer_in_role_at_event_on_day in all_volunteers_in_roles_at_event_including_no_role_set
        ]
        all_groups = [
            volunteer_in_role_at_event_on_day.group
            for volunteer_in_role_at_event_on_day in all_volunteers_in_roles_at_event_including_no_role_set
        ]

        all_groups_match = len(set(all_groups)) <= 1
        all_roles_match = len(set(all_roles)) <= 1

        return all_roles_match and all_groups_match

    def volunteer_has_empty_available_days_without_role(
        self, volunteer_id: str
    ) -> bool:
        availability = (
            self.list_of_volunteers_with_id_at_event.volunteer_at_event_with_id(
                volunteer_id=volunteer_id
            ).availablity
        )
        all_volunteers_in_roles_at_event_including_no_role_set = [
            self.volunteer_in_role_at_event_on_day(volunteer_id=volunteer_id, day=day)
            for day in availability.days_available()
        ]
        unallocated_roles = [
            volunteer_role
            for volunteer_role in all_volunteers_in_roles_at_event_including_no_role_set
            if volunteer_role.no_role_set
        ]

        return len(unallocated_roles) > 0

    def volunteer_has_at_least_one_day_in_role_and_all_roles_and_groups_match(
        self, volunteer_id: str
    ) -> bool:
        availability = (
            self.list_of_volunteers_with_id_at_event.volunteer_at_event_with_id(
                volunteer_id=volunteer_id
            ).availablity
        )
        all_volunteers_in_roles_at_event_including_no_role_set = [
            self.volunteer_in_role_at_event_on_day(volunteer_id=volunteer_id, day=day)
            for day in availability.days_available()
        ]
        allocated_roles = [
            volunteer_role.role_and_group
            for volunteer_role in all_volunteers_in_roles_at_event_including_no_role_set
            if not volunteer_role.no_role_set
        ]

        if len(allocated_roles) == 0:
            print("No roles, False")
            return False

        all_match = allocated_roles.count(allocated_roles[0]) == len(allocated_roles)

        return all_match


def DEPRECATE_get_data_to_be_stored_for_volunteer_rota_page(
    interface: abstractInterface, event: Event
) -> DEPRECATE_DataToBeStoredWhilstConstructingVolunteerRotaPage:
    list_of_cadet_ids_with_groups = (
        DEPRECATE_load_list_of_cadets_ids_with_group_allocations_active_cadets_only(
            event=event, interface=interface
        )
    )
    unallocated_cadets_at_event = (
        DEPRECATE_get_list_of_cadets_unallocated_to_group_at_event(
            event=event, interface=interface
        )
    )
    volunteer_skills = load_list_of_volunteer_skills(interface.data)
    all_volunteers = get_list_of_all_volunteers(interface.data)
    volunteers_in_roles_at_event = (
        DEPRECATE_get_volunteers_in_role_at_event_with_active_allocations(
            event=event, interface=interface
        )
    )
    list_of_volunteers_at_event = DEPRECATE_load_list_of_volunteers_at_event(
        event=event, interface=interface
    )

    dict_of_volunteers_with_last_roles = (
        DEPRECATE_get_dict_of_volunteers_with_last_roles(
            interface=interface,
            list_of_volunteer_ids=list_of_volunteers_at_event.list_of_volunteer_ids,
            avoid_event=event,
        )
    )

    return DEPRECATE_DataToBeStoredWhilstConstructingVolunteerRotaPage(
        event=event,
        list_of_cadet_ids_with_groups=list_of_cadet_ids_with_groups,
        unallocated_cadets_at_event=unallocated_cadets_at_event,
        volunteer_skills=volunteer_skills,
        volunteers_in_roles_at_event=volunteers_in_roles_at_event,
        list_of_volunteers_with_id_at_event=list_of_volunteers_at_event,
        dict_of_volunteers_with_last_roles=dict_of_volunteers_with_last_roles,
        all_volunteers=all_volunteers,
    )


def get_data_to_be_stored_for_volunteer_rota_page(
    data_layer: DataLayer, event: Event
) -> DEPRECATE_DataToBeStoredWhilstConstructingVolunteerRotaPage:
    list_of_cadet_ids_with_groups = (
        load_list_of_cadets_ids_with_group_allocations_active_cadets_only(
            event=event, data_layer=data_layer
        )
    )
    unallocated_cadets_at_event = get_list_of_cadets_unallocated_to_group_at_event(
        event=event, data_layer=data_layer
    )
    volunteer_skills = load_list_of_volunteer_skills(data_layer)
    all_volunteers = get_list_of_all_volunteers(data_layer)
    volunteers_in_roles_at_event = (
        get_volunteers_in_role_at_event_with_active_allocations(
            event=event, data_layer=data_layer
        )
    )
    list_of_volunteers_at_event = load_list_of_volunteers_at_event(
        event=event, data_layer=data_layer
    )
    list_of_volunteers_at_event_with_ids = load_list_of_volunteers_with_ids_at_event(
        event=event, data_layer=data_layer
    )  ## WANT TO DEPRECATE

    dict_of_volunteers_with_last_roles = get_dict_of_volunteers_with_last_roles(
        data_layer=data_layer,
        list_of_volunteers_at_event=list_of_volunteers_at_event,
        avoid_event=event,
    )

    return DEPRECATE_DataToBeStoredWhilstConstructingVolunteerRotaPage(
        event=event,
        list_of_cadet_ids_with_groups=list_of_cadet_ids_with_groups,
        unallocated_cadets_at_event=unallocated_cadets_at_event,
        volunteer_skills=volunteer_skills,
        volunteers_in_roles_at_event=volunteers_in_roles_at_event,
        all_volunteers=all_volunteers,
        list_of_volunteers_with_id_at_event=list_of_volunteers_at_event_with_ids,
        dict_of_volunteers_with_last_roles=dict_of_volunteers_with_last_roles,
    )


def sort_volunteer_data_for_event_by_day_sort_order(
    list_of_volunteers_at_event: ListOfVolunteersAtEventWithId,
    sort_by_day: Day,
    data_to_be_stored: DEPRECATE_DataToBeStoredWhilstConstructingVolunteerRotaPage,
) -> ListOfVolunteersAtEventWithId:
    tuple_of_volunteers_at_event_and_roles = [
        (
            volunteer_at_event,
            data_to_be_stored.volunteer_in_role_at_event_on_day(
                volunteer_id=volunteer_at_event.volunteer_id, day=sort_by_day
            ).role_and_group,
        )
        for volunteer_at_event in list_of_volunteers_at_event
    ]

    tuple_of_volunteers_at_event_and_roles.sort(key=lambda tup: tup[1])

    list_of_volunteers = [
        volunteer_at_event
        for volunteer_at_event, __ in tuple_of_volunteers_at_event_and_roles
    ]

    return ListOfVolunteersAtEventWithId(list_of_volunteers)


def get_cadet_location_string(
    data_to_be_stored: DEPRECATE_DataToBeStoredWhilstConstructingVolunteerRotaPage,
    volunteer_at_event: VolunteerAtEventWithId,
):
    list_of_groups = list_of_cadet_groups_associated_with_volunteer(
        data_to_be_stored=data_to_be_stored, volunteer_at_event=volunteer_at_event
    )
    if len(list_of_groups) == 0:
        return "x- no associated cadets -x"  ## trick to get at end of sort

    return str_type_of_group_given_list_of_groups(list_of_groups)


def str_type_of_group_given_list_of_groups(list_of_groups: List[Group]):
    types_of_groups = [group.type_of_group() for group in list_of_groups]
    unique_list_of_group_locations = list(set(types_of_groups))
    sorted_list_of_group_locations = sorted_locations(unique_list_of_group_locations)
    return ", ".join(sorted_list_of_group_locations)


def str_dict_skills(
    volunteer: Volunteer,
    data_to_be_stored: DEPRECATE_DataToBeStoredWhilstConstructingVolunteerRotaPage,
):
    dict_of_skills = data_to_be_stored.dict_of_skills_given_volunteer_id(volunteer.id)
    if dict_of_skills.empty():
        return "No skills recorded"

    return dict_of_skills.skills_held_as_str()



def get_sorted_and_filtered_list_of_volunteers_at_event(
    cache: AdHocCache,
        event: Event,
    sorts_and_filters: RotaSortsAndFilters,
) -> ListOfVolunteersAtEventWithId:
    list_of_volunteers_at_event = (
        filtered_list_of_volunteers_at_event(cache=cache, event=event, sorts_and_filters=sorts_and_filters)
    )
    sorted_list_of_volunteers_at_event = sort_list_of_volunteers_at_event(
        cache=cache,
        list_of_volunteers_at_event=list_of_volunteers_at_event,
        sorts_and_filters=sorts_and_filters,
    )

    return sorted_list_of_volunteers_at_event





def sort_list_of_volunteers_at_event(
    cache: AdHocCache,
    list_of_volunteers_at_event: ListOfVolunteersAtEvent,
    sorts_and_filters: RotaSortsAndFilters,
) -> ListOfVolunteersAtEvent:
    sort_by_location = sorts_and_filters.sort_by_location
    if sort_by_location:
        return sort_volunteer_data_for_event_by_location(
            list_of_volunteers_at_event=list_of_volunteers_at_event,
            cache=cache
        )

    sort_by_volunteer_name = sorts_and_filters.sort_by_volunteer_name
    if sort_by_volunteer_name is not arg_not_passed:
        return sort_volunteer_data_for_event_by_name_sort_order(
            cache=cache,
            volunteers_at_event=list_of_volunteers_at_event,
            sort_order=sort_by_volunteer_name,
        )

    sort_by_day = sorts_and_filters.sort_by_day
    if sort_by_day is not arg_not_passed:
        return sort_volunteer_data_for_event_by_day_sort_order(
            list_of_volunteers_at_event=list_of_volunteers_at_event,
            sort_by_day=sorts_and_filters.sort_by_day,
            cache=cache
        )

    return list_of_volunteers_at_event


def sort_volunteer_data_for_event_by_location(
    list_of_volunteers_at_event: ListOfVolunteersAtEventWithId,
    data_to_be_stored: DEPRECATE_DataToBeStoredWhilstConstructingVolunteerRotaPage,
) -> ListOfVolunteersAtEventWithId:
    list_of_locations = [
        get_cadet_location_string(
            data_to_be_stored=data_to_be_stored, volunteer_at_event=volunteer_at_event
        )
        for volunteer_at_event in list_of_volunteers_at_event
    ]

    locations_and_volunteers = zip(list_of_locations, list_of_volunteers_at_event)

    sorted_by_location = sorted(locations_and_volunteers, key=lambda tup: tup[0])
    sorted_list_of_volunteers = ListOfVolunteersAtEventWithId(
        [location_and_volunteer[1] for location_and_volunteer in sorted_by_location]
    )

    return sorted_list_of_volunteers


def list_of_cadet_groups_associated_with_volunteer(
    data_to_be_stored: DEPRECATE_DataToBeStoredWhilstConstructingVolunteerRotaPage,
    volunteer_at_event: VolunteerAtEventWithId,
) -> List[Group]:
    list_of_cadet_ids = volunteer_at_event.list_of_associated_cadet_id
    list_of_groups = [
        data_to_be_stored.group_given_cadet_id(cadet_id)
        for cadet_id in list_of_cadet_ids
    ]
    list_of_groups = [group for group in list_of_groups if group is not missing_data]

    return list_of_groups


def get_volunteer_matrix(
    cache: AdHocCache, event: Event, sorts_and_filters: RotaSortsAndFilters
) -> pd.DataFrame:
    data_to_be_stored = get_data_to_be_stored_for_volunteer_rota_page(
        data_layer=cache._data_layer, event=event ##FIXME
    )

    list_of_volunteers_at_event = get_sorted_and_filtered_list_of_volunteers_at_event(
        cache=cache,
        event=event,
        sorts_and_filters=sorts_and_filters,
    )

    list_of_rows = [
        row_for_volunteer_at_event(
            event=event,
            volunteer_at_event=volunteer_at_event,
            data_to_be_stored=data_to_be_stored,
        )
        for volunteer_at_event in list_of_volunteers_at_event
    ]

    return pd.DataFrame(list_of_rows)


def row_for_volunteer_at_event(
    event: Event,
    volunteer_at_event: VolunteerAtEventWithId,
    data_to_be_stored: DEPRECATE_DataToBeStoredWhilstConstructingVolunteerRotaPage,
) -> pd.Series:
    id = volunteer_at_event.volunteer_id
    volunteer = data_to_be_stored.all_volunteers.object_with_id(id)
    name = volunteer.name
    skills_dict = data_to_be_stored.volunteer_skills.dict_of_skills_for_volunteer_id(id)
    preferred = volunteer_at_event.preferred_duties
    same_different = volunteer_at_event.same_or_different


    volunteers_in_roles_dict = dict(
        [
            (
                day.name,
                role_and_group_string_for_day(
                    volunteer_at_event=volunteer_at_event,
                    day=day,
                    volunteers_in_roles_at_event=data_to_be_stored.volunteers_in_roles_at_event,
                ),
            )
            for day in event.weekdays_in_event()
        ]
    )

    result_dict = dict(Name=name, Skills=str(skills_dict), preferred=preferred, same_different=same_different)
    result_dict.update(volunteers_in_roles_dict)

    return pd.Series(result_dict)


def role_and_group_string_for_day(
    volunteer_at_event: VolunteerAtEventWithId,
    day: Day,
    volunteers_in_roles_at_event: ListOfVolunteersWithIdInRoleAtEvent,
) -> str:
    if not volunteer_at_event.available_on_day(day):
        return "Unavailable"
    else:
        return str(
            volunteers_in_roles_at_event.member_matching_volunteer_id_and_day(
                volunteer_id=volunteer_at_event.volunteer_id,
                day=day,
                return_empty_if_missing=True,
            ).role_and_group
        )
