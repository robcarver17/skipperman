from dataclasses import dataclass
from typing import List

from app.objects.volunteers import Volunteer

from app.data_access.store.data_access import DataLayer

from app.OLD_backend.data.group_allocations import GroupAllocationsData
from app.OLD_backend.data.volunteer_allocation import VolunteerAllocationData

from app.OLD_backend.volunteers.volunteers import (
    EPRECATE_get_volunteer_name_from_id,
    get_sorted_list_of_volunteers, get_volunteer_from_id,
)

from app.objects.abstract_objects.abstract_interface import abstractInterface

from app.OLD_backend.data.volunteer_rota import VolunteerRotaData
from app.data_access.configuration.skills_and_roles import get_volunteer_roles
from app.OLD_backend.data.patrol_boats import PatrolBoatsData

from app.objects.exceptions import missing_data
from app.objects.events import Event
from app.objects.groups import LAKE_TRAINING, Group, GROUP_UNALLOCATED_TEXT_DONTUSE
from app.data_access.configuration.groups import all_groups_names
from app.objects_OLD.volunteers_at_event import (
    ListOfVolunteersAtEvent, DEPRECATE_VolunteerAtEvent,
)
from app.objects.volunteer_at_event_with_id import ListOfVolunteersAtEventWithId
from app.objects_OLD.primtive_with_id.identified_volunteer_at_event import ListOfIdentifiedVolunteersAtEvent
from app.objects.volunteer_roles_and_groups_with_id import NO_ROLE_SET, VolunteerWithIdInRoleAtEvent, \
    ListOfVolunteersWithIdInRoleAtEvent, RoleAndGroupDEPRECATE

from app.objects.day_selectors import Day


@dataclass
class SwapData:
    event: Event
    original_day: Day
    day_to_swap_with: Day
    swap_boats: bool
    swap_roles: bool
    volunteer_id_to_swap_with: str
    original_volunteer_id: str


def update_role_at_event_for_volunteer_on_day_at_event(
    interface: abstractInterface,
    event: Event,
    day: Day,
    volunteer_id: str,
    new_role: str,
):
    volunteer_in_role_at_event_on_day = VolunteerWithIdInRoleAtEvent(
        day=day, volunteer_id=volunteer_id
    )
    update_role_at_event_for_volunteer_on_day(
        interface=interface,
        event=event,
        volunteer_in_role_at_event_on_day=volunteer_in_role_at_event_on_day,
        new_role=new_role,
    )


def get_volunteer_role_at_event_on_day(
    interface: abstractInterface, event: Event, volunteer_id: str, day: Day
) -> str:
    volunteer_role_data = VolunteerRotaData(interface.data)
    return volunteer_role_data.get_volunteer_role_at_event_on_day_for_volunteer_id(
        event=event, volunteer_id=volunteer_id, day=day
    )


def DEPRECATE_get_volunteer_with_role_at_event_on_day(
    interface: abstractInterface, event: Event, volunteer_id: str, day: Day
) -> VolunteerWithIdInRoleAtEvent:
    volunteer_role_data = VolunteerRotaData(interface.data)
    return volunteer_role_data.get_volunteer_with_id_in_role_at_event_on_day_from_id(
        event=event, volunteer_id=volunteer_id, day=day
    )

def get_volunteer_with_role_at_event_on_day(
    data_layer: DataLayer, event: Event, volunteer: Volunteer, day: Day
) -> VolunteerWithIdInRoleAtEvent:
    volunteer_role_data = VolunteerRotaData(data_layer)
    return volunteer_role_data.get_volunteer_with_role_at_event_on_day_from_volunteer(
        event=event, volunteer=volunteer, day=day
    )



def sort_volunteer_data_for_event_by_name_sort_order(
    data_layer: DataLayer,
    volunteers_at_event: ListOfVolunteersAtEventWithId,
    sort_order,
) -> ListOfVolunteersAtEventWithId:
    list_of_volunteers = get_sorted_list_of_volunteers(
        data_layer=data_layer, sort_by=sort_order
    )
    ## this works because if an ID is missing we just ignore it
    return volunteers_at_event.sort_by_list_of_volunteer_ids(
        list_of_volunteers.list_of_ids
    )


def dict_of_groups_for_dropdown(
    interface: abstractInterface,
):  ## Future proof to when groups come from files
    dict_of_groups = {group: group for group in all_groups_names}
    dict_of_groups[GROUP_UNALLOCATED_TEXT_DONTUSE] = GROUP_UNALLOCATED_TEXT_DONTUSE

    return dict_of_groups


MAKE_UNAVAILABLE = "* UNAVAILABLE *"


def dict_of_roles_for_dropdown(interface: abstractInterface):
    volunteer_roles = get_volunteer_roles(interface)
    dict_of_roles = {role: role for role in volunteer_roles}
    dict_of_roles[NO_ROLE_SET] = NO_ROLE_SET
    dict_of_roles[MAKE_UNAVAILABLE] = MAKE_UNAVAILABLE

    return dict_of_roles


def boat_related_role_str_and_group_on_day_for_volunteer_id(
    interface: abstractInterface, day: Day, event: Event, volunteer_id: str
) -> str:
    volunteer_rota = VolunteerRotaData(interface.data)
    volunteer_on_day = volunteer_rota.get_volunteer_with_id_in_role_at_event_on_day_from_id(
        event=event, day=day, volunteer_id=volunteer_id
    )
    if volunteer_on_day is missing_data:
        return ""
    elif volunteer_on_day.requires_boat:
        if volunteer_on_day.group.is_unallocated:
            return volunteer_on_day.role
        else:
            return "%s - %s" % (
                volunteer_on_day.group.name,
                volunteer_on_day.role,
            )
    else:
        return ""


def is_possible_to_copy_roles_for_non_grouped_roles_only(
    interface: abstractInterface, event: Event, volunteer_id: str, day: Day
) -> bool:
    ## Only possible if: none of the roles require a group, and all the roles don't currently match

    role_today = DEPRECATE_get_volunteer_with_role_at_event_on_day(
        interface=interface, volunteer_id=volunteer_id, day=day, event=event
    )
    if role_today.no_role_set:
        return False

    all_volunteer_positions = (
        get_list_of_volunteer_with_role_across_days_for_volunteer_at_event(
            interface=interface, event=event, volunteer_id=volunteer_id
        )
    )

    all_roles = [
        volunteer_with_role.role for volunteer_with_role in all_volunteer_positions
    ]

    no_roles_to_copy = len(all_roles) == 0
    all_roles_match = len(set(all_roles)) <= 1

    roles_require_groups = [
        volunteer_with_role.requires_group
        for volunteer_with_role in all_volunteer_positions
    ]
    at_least_one_role_require_group = any(roles_require_groups)

    ## copy not possible if all roles the same, or at least one requires a group, or nothing to copy
    if all_roles_match or at_least_one_role_require_group or no_roles_to_copy:
        return False
    else:
        return True


def get_list_of_volunteer_with_role_across_days_for_volunteer_at_event(
    interface: abstractInterface, event: Event, volunteer_id: str
) -> List[VolunteerWithIdInRoleAtEvent]:
    ## Only possible if: none of the roles require a group, and all the roles don't currently match

    volunteers_with_roles_in_event_including_missing_data = [
        DEPRECATE_get_volunteer_with_role_at_event_on_day(
            interface=interface, volunteer_id=volunteer_id, day=day, event=event
        )
        for day in event.weekdays_in_event()
    ]

    all_volunteer_positions = [
        volunteer_with_role
        for volunteer_with_role in volunteers_with_roles_in_event_including_missing_data
        if volunteer_with_role is not missing_data
    ]

    return all_volunteer_positions


def is_possible_to_swap_roles_on_one_day_for_non_grouped_roles_only(
    interface: abstractInterface, event: Event, volunteer_id: str, day: Day
) -> bool:
    ## Only possible if: none of the roles require a group, and all the roles don't currently match

    volunteer_with_role = DEPRECATE_get_volunteer_with_role_at_event_on_day(
        interface=interface, volunteer_id=volunteer_id, day=day, event=event
    )

    if volunteer_with_role.no_role_set:
        return False

    role_requires_group = volunteer_with_role.requires_group
    possible_to_swap = not role_requires_group

    return possible_to_swap


def swap_roles_for_volunteers_in_allocation(
    interface: abstractInterface, swap_data: SwapData
):
    volunteer_rota_data = VolunteerRotaData(interface.data)
    try:
        volunteer_rota_data.swap_roles_for_volunteers_in_allocation(
            event=swap_data.event,
            original_volunteer_id=swap_data.original_volunteer_id,
            volunteer_id_to_swap_with=swap_data.volunteer_id_to_swap_with,
            day_to_swap_with=swap_data.day_to_swap_with,
            original_day=swap_data.original_day,
        )
    except Exception as e:
        first_name = EPRECATE_get_volunteer_name_from_id(
            interface=interface, volunteer_id=swap_data.original_volunteer_id
        )
        second_name = EPRECATE_get_volunteer_name_from_id(
            interface=interface, volunteer_id=swap_data.volunteer_id_to_swap_with
        )
        interface.log_error(
            "Swap roles of %s and %s failed on day %s, error %s"
            % (first_name, second_name, swap_data.day_to_swap_with.name, str(e))
        )


def swap_roles_and_groups_for_volunteers_in_allocation(
    interface: abstractInterface,
    event: Event,
    original_day: Day,
    original_volunteer_id: str,
    day_to_swap_with: Day,
    volunteer_id_to_swap_with: str,
):
    volunteer_rota_data = VolunteerRotaData(interface.data)
    volunteer_rota_data.swap_roles_and_groups_for_volunteers_in_allocation(
        event=event,
        original_day=original_day,
        day_to_swap_with=day_to_swap_with,
        original_volunteer_id=original_volunteer_id,
        volunteer_id_to_swap_with=volunteer_id_to_swap_with,
    )


def volunteer_is_on_lake(
    data_layer: DataLayer, event: Event, volunteer_id: str
) -> bool:
    volunteer_rota_data = VolunteerRotaData(data_layer)
    return volunteer_rota_data.volunteer_is_on_lake(
        event=event, volunteer_id=volunteer_id
    )


def list_of_cadet_groups_associated_with_volunteer(
    data_layer: DataLayer,
    event: Event,
    volunteer_at_event: DEPRECATE_VolunteerAtEvent,
) -> List[Group]:
    group_data = GroupAllocationsData(data_layer)
    list_of_cadet_ids = volunteer_at_event.list_of_associated_cadet_id
    list_of_groups = []
    for cadet_id in list_of_cadet_ids:
        list_of_groups_this_cadet = [
            group_data.CONSIDER_USING_ACTIVE_FILTER_get_list_of_cadet_ids_with_groups_at_event(
                event
            ).group_for_cadet_id_on_day(cadet_id, day)
            for day in event.weekdays_in_event()
        ]
        list_of_groups += list_of_groups_this_cadet

    list_of_groups = list(set(list_of_groups))
    list_of_groups = [group for group in list_of_groups if group is not missing_data]

    return list_of_groups


def lake_in_list_of_groups(list_of_groups: List[Group]):
    types_of_groups = [group.type_of_group() for group in list_of_groups]
    return LAKE_TRAINING in types_of_groups


def groups_for_volunteer_at_event(
    data_layer: DataLayer, event: Event, volunteer: Volunteer
) -> List[Group]:
    list_of_groups = [
        get_volunteer_with_role_at_event_on_day(
            data_layer=data_layer, volunteer=volunteer, day=day, event=event
        ).group
        for day in event.weekdays_in_event()
    ]
    list_of_groups = [group for group in list_of_groups if group is not missing_data]

    return list(set(list_of_groups))


def load_list_of_identified_volunteers_at_event(
    interface: abstractInterface, event: Event
) -> ListOfIdentifiedVolunteersAtEvent:
    volunteer_allocation_data = VolunteerAllocationData(interface.data)
    return volunteer_allocation_data.load_list_of_identified_volunteers_at_event(event)


def DEPRECATE_load_list_of_volunteers_at_event(
    interface: abstractInterface, event: Event
) -> ListOfVolunteersAtEventWithId:
    volunteer_allocation_data = VolunteerAllocationData(interface.data)
    return volunteer_allocation_data.load_list_of_volunteers_with_ids_at_event(event)


def load_list_of_volunteers_at_event(
    data_layer: DataLayer, event: Event
) -> ListOfVolunteersAtEvent:
    volunteer_allocation_data = VolunteerAllocationData(data_layer)
    return volunteer_allocation_data.get_list_of_volunteers_at_event(event)


def load_list_of_volunteers_with_ids_at_event(
    data_layer: DataLayer, event: Event
) -> ListOfVolunteersAtEventWithId:
    volunteer_allocation_data = VolunteerAllocationData(data_layer)
    return volunteer_allocation_data.load_list_of_volunteers_with_ids_at_event(event)


def delete_volunteer_at_event(
    data_layer: DataLayer,  event: Event, volunteer: Volunteer
):
    volunteer_id = volunteer.id

    volunteer_allocation_data = VolunteerAllocationData(data_layer)
    volunteer_allocation_data.delete_volunteer_with_id_at_event(
        event=event, volunteer_id=volunteer_id
    )

    patrol_boat_data = PatrolBoatsData(data_layer)
    patrol_boat_data.delete_volunteer_with_id_at_event(
        event=event, volunteer_id=volunteer_id
    )

    delete_role_at_event_for_volunteer_on_all_days(
        data_layer=data_layer, volunteer_id=volunteer_id, event=event
    )


def update_volunteer_notes_at_event(
    interface: abstractInterface, event: Event, volunteer_id: str, new_notes: str
):
    volunteer_allocation_data = VolunteerAllocationData(interface.data)
    volunteer_allocation_data.update_volunteer_notes_at_event(
        event=event, volunteer_id=volunteer_id, new_notes=new_notes
    )


def add_volunteer_to_event_with_just_id(
    interface: abstractInterface, volunteer_id: str, event: Event
):
    volunteer_allocation_data = VolunteerAllocationData(interface.data)
    volunteer_allocation_data.add_volunteer_to_event_with_just_id(
        event=event, volunteer_id=volunteer_id
    )


def is_volunteer_already_at_event(
    interface: abstractInterface, volunteer_id: str, event: Event
) -> bool:
    volunteers_at_event_data = VolunteerAllocationData(interface.data)
    return volunteers_at_event_data.is_volunteer_already_at_event(
        volunteer_id=volunteer_id, event=event
    )


def delete_role_at_event_for_volunteer_on_day(
    data_layer: DataLayer, volunteer: Volunteer, day: Day, event: Event
):
    volunteer_rota_data = VolunteerRotaData(data_layer)
    volunteer_rota_data.delete_role_at_event_for_volunteer_on_day(
        event=event, day=day, volunteer=volunteer
    )

    ### and patrol boat data
    patrol_boat_data = PatrolBoatsData(data_layer)
    patrol_boat_data.remove_volunteer_from_patrol_boat_on_day_at_event(
        event=event, volunteer=volunteer, day=day
    )


def delete_role_at_event_for_volunteer_on_all_days(
    data_layer: DataLayer, volunteer_id: str, event: Event
):
    volunteer_rota_data = VolunteerRotaData(data_layer)
    volunteer_rota_data.delete_role_at_event_for_volunteer_on_all_days(
        event=event, volunteer_id=volunteer_id
    )


def load_volunteers_in_role_at_event(
    interface: abstractInterface, event: Event
) -> ListOfVolunteersWithIdInRoleAtEvent:
    volunteer_role_data = VolunteerRotaData(interface.data)
    return volunteer_role_data.get_list_of_volunteers_in_roles_at_event(event)


def DEPRECATE_get_volunteers_in_role_at_event_with_active_allocations(
    interface: abstractInterface, event: Event
) -> ListOfVolunteersWithIdInRoleAtEvent:
    volunteer_role_data = VolunteerRotaData(interface.data)
    return volunteer_role_data.get_volunteers_with_id_in_role_at_event_who_are_also_allocated_to_event(
        event
    )


def get_volunteers_in_role_at_event_with_active_allocations(
    data_layer: DataLayer, event: Event
) -> ListOfVolunteersWithIdInRoleAtEvent:
    volunteer_role_data = VolunteerRotaData(data_layer)
    return volunteer_role_data.get_volunteers_with_id_in_role_at_event_who_are_also_allocated_to_event(
        event
    )

def update_role_at_event_for_volunteer_on_day(
    interface: abstractInterface,
    volunteer_in_role_at_event_on_day: VolunteerWithIdInRoleAtEvent,
    new_role: str,
    event: Event,
):
    volunteer = get_volunteer_from_id(data_layer=interface.data, volunteer_id=volunteer_in_role_at_event_on_day.volunteer_id)
    if new_role is NO_ROLE_SET:
        delete_role_at_event_for_volunteer_on_day(
            data_layer=interface.data,
            event=event,
            volunteer=volunteer,
            day=volunteer_in_role_at_event_on_day.day,
        )
    else:
        update_role_at_event_for_volunteer_on_day_if_switching_roles(
            interface=interface,
            volunteer_in_role_at_event_on_day=volunteer_in_role_at_event_on_day,
            new_role=new_role,
            event=event,
        )


def update_role_at_event_for_volunteer_on_day_if_switching_roles(
    interface: abstractInterface,
    volunteer_in_role_at_event_on_day: VolunteerWithIdInRoleAtEvent,
    new_role: str,
    event: Event,
):
    volunteer_rota_data = VolunteerRotaData(interface.data)
    volunteer_rota_data.update_role_at_event_for_volunteer_on_day_at_event(
        event=event,
        volunteer_in_role_at_event_on_day=volunteer_in_role_at_event_on_day,
        new_role=new_role,
    )


def update_group_at_event_for_volunteer_on_day(
    interface: abstractInterface,
    volunteer_in_role_at_event_on_day: VolunteerWithIdInRoleAtEvent,
    new_group: Group,
    event: Event,
):
    volunteer_rota_data = VolunteerRotaData(interface.data)
    volunteer_rota_data.update_group_at_event_for_volunteer_on_day(
        event=event,
        volunteer_in_role_at_event_on_day=volunteer_in_role_at_event_on_day,
        new_group=new_group,
    )


def update_role_and_group_at_event_for_volunteer_on_all_days_when_available(
    interface: abstractInterface,
    volunteer_id: str,
    new_role_and_group: RoleAndGroupDEPRECATE,
    event: Event,
):
    volunteer_rota_data = VolunteerRotaData(interface.data)
    volunteer_rota_data.update_role_and_group_at_event_for_volunteer_on_all_days_when_available(
        event=event,
        volunteer_id=volunteer_id,
        new_role_and_group=new_role_and_group,
    )


def copy_across_duties_for_volunteer_at_event_from_one_day_to_all_other_days(
    interface: abstractInterface,
    event: Event,
    volunteer_id: str,
    day: Day,
    allow_replacement: bool = True,
):
    volunteer_data = VolunteerRotaData(interface.data)
    try:
        volunteer_data.copy_across_duties_for_volunteer_at_event_from_one_day_to_all_other_days(
            event=event,
            day=day,
            volunteer_id=volunteer_id,
            allow_replacement=allow_replacement,
        )
    except Exception as e:
        name = EPRECATE_get_volunteer_name_from_id(
            interface=interface, volunteer_id=volunteer_id
        )
        print(
            "Can't copy across role data for %s on %s, error %s, conflicting change made?"
            % (name, day.name, str(e))
        )


def copy_earliest_valid_role_and_overwrite_for_volunteer(
    interface: abstractInterface, event: Event, volunteer_id: str
):
    valid_day = get_day_with_earliest_valid_role_and_group_for_volunteer_or_none(
        interface=interface, event=event, volunteer_id=volunteer_id
    )
    name = EPRECATE_get_volunteer_name_from_id(interface=interface, volunteer_id=volunteer_id)
    print("Valid day for volunteer %s is %s" % (name, str(valid_day)))
    if valid_day is None:
        return

    copy_across_duties_for_volunteer_at_event_from_one_day_to_all_other_days(
        interface=interface,
        event=event,
        volunteer_id=volunteer_id,
        day=valid_day,
        allow_replacement=True,
    )


def copy_earliest_valid_role_to_all_empty_for_volunteer(
    interface: abstractInterface, event: Event, volunteer_id: str
):
    valid_day = get_day_with_earliest_valid_role_and_group_for_volunteer_or_none(
        interface=interface, event=event, volunteer_id=volunteer_id
    )
    name = EPRECATE_get_volunteer_name_from_id(interface=interface, volunteer_id=volunteer_id)
    print("Valid day for volunteer %s is %s" % (name, str(valid_day)))
    if valid_day is None:
        return

    copy_across_duties_for_volunteer_at_event_from_one_day_to_all_other_days(
        interface=interface,
        event=event,
        volunteer_id=volunteer_id,
        day=valid_day,
        allow_replacement=False,
    )


def get_day_with_earliest_valid_role_and_group_for_volunteer_or_none(
    interface: abstractInterface, event: Event, volunteer_id: str
) -> Day:
    volunteer_data = VolunteerRotaData(interface.data)

    for day in event.weekdays_in_event():
        volunteer_with_role_and_group = (
            volunteer_data.get_volunteer_with_id_in_role_at_event_on_day_from_id(
                event=event, volunteer_id=volunteer_id, day=day
            )
        )
        role_and_group = volunteer_with_role_and_group.role_and_group
        if role_and_group.missing:
            continue
        else:
            return day

    return None


def volunteer_has_at_least_one_allocated_role_and_empty_spaces_to_fill(
    interface: abstractInterface, event: Event, volunteer_id: str
) -> bool:
    volunteer_data = VolunteerRotaData(interface.data)
    return volunteer_data.volunteer_has_at_least_one_allocated_role_and_empty_spaces_to_fill(
        event=event, volunteer_id=volunteer_id
    )


def volunteer_has_at_least_one_allocated_role_which_matches_others(
    interface: abstractInterface, event: Event, volunteer_id: str
) -> bool:
    volunteer_data = VolunteerRotaData(interface.data)
    return (
        volunteer_data.volunteer_has_at_least_one_allocated_role_which_matches_others(
            event=event, volunteer_id=volunteer_id
        )
    )


def get_list_of_volunteer_roles_for_event_across_days(data_layer: DataLayer, event: Event, volunteer_at_event: DEPRECATE_VolunteerAtEvent) -> List[VolunteerWithIdInRoleAtEvent]:
    volunteer_rota_data = VolunteerRotaData(data_layer)
    list_of_volunteer_roles = [
        volunteer_rota_data.get_volunteer_with_role_at_event_on_day_for_volunteer_at_event(
            event=event, volunteer_at_event=volunteer_at_event, day=day
        )
        for day in event.weekdays_in_event()
    ]

    return list_of_volunteer_roles
