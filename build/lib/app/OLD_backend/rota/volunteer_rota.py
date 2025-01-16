from typing import List

from app.backend.rota.changes import update_role_at_event_for_volunteer_on_day
from app.backend.volunteers.volunteers_at_event import load_list_of_volunteers_at_event
from app.data_access.store.DEPRECATE_ad_hoc_cache import AdHocCache
from app.objects.volunteers import Volunteer

from app.data_access.store.data_access import DataLayer

from app.OLD_backend.data.volunteer_allocation import VolunteerAllocationData

from app.objects.abstract_objects.abstract_interface import abstractInterface

from app.OLD_backend.data.volunteer_rota import VolunteerRotaData

from app.objects.exceptions import missing_data
from app.objects.events import Event
from app.objects.groups import LAKE_TRAINING_LOCATION, Group
from app.objects_OLD.volunteers_at_event import (
    DEPRECATE_VolunteerAtEvent,
)
from app.objects.volunteer_at_event_with_id import ListOfVolunteersAtEventWithId
from app.objects.identified_volunteer_at_event import (
    ListOfIdentifiedVolunteersAtEvent,
)
from app.objects.volunteer_roles_and_groups_with_id import (
    VolunteerWithIdInRoleAtEvent,
    ListOfVolunteersWithIdInRoleAtEvent,
    RoleAndGroupDEPRECATE,
)

from app.objects.day_selectors import Day





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


def get_list_of_volunteer_with_role_across_days_for_volunteer_at_event(
    interface: abstractInterface, event: Event, volunteer_id: str
) -> List[VolunteerWithIdInRoleAtEvent]:
    ## Only possible if: none of the roles require a group, and all the roles don't currently match

    volunteers_with_roles_in_event_including_missing_data = [
        DEPRECATE_get_volunteer_with_role_at_event_on_day(
            interface=interface, volunteer_id=volunteer_id, day=day, event=event
        )
        for day in event.days_in_event()
    ]

    all_volunteer_positions = [
        volunteer_with_role
        for volunteer_with_role in volunteers_with_roles_in_event_including_missing_data
        if volunteer_with_role is not missing_data
    ]

    return all_volunteer_positions


def volunteer_is_on_lake(
    data_layer: DataLayer, event: Event, volunteer_id: str
) -> bool:
    volunteer_rota_data = VolunteerRotaData(data_layer)
    return volunteer_rota_data.volunteer_is_on_lake(
        event=event, volunteer_id=volunteer_id
    )


def lake_in_list_of_groups(list_of_groups: List[Group]):
    types_of_groups = [group.type_of_group() for group in list_of_groups]
    return LAKE_TRAINING_LOCATION in types_of_groups


def groups_for_volunteer_at_event(
    data_layer: DataLayer, event: Event, volunteer: Volunteer
) -> List[Group]:
    list_of_groups = [
        get_volunteer_with_role_at_event_on_day(
            data_layer=data_layer, volunteer=volunteer, day=day, event=event
        ).group
        for day in event.days_in_event()
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


def load_list_of_volunteers_with_ids_at_event(
    data_layer: DataLayer, event: Event
) -> ListOfVolunteersAtEventWithId:
    volunteer_allocation_data = VolunteerAllocationData(data_layer)
    return volunteer_allocation_data.load_list_of_volunteers_with_ids_at_event(event)


def delete_role_at_event_for_volunteer_on_all_days(
    data_layer: DataLayer, volunteer_id: str, event: Event
):
    volunteer_rota_data = VolunteerRotaData(data_layer)
    volunteer_rota_data.delete_role_at_event_for_volunteer_on_all_days(
        event=event, volunteer_id=volunteer_id
    )


def get_volunteers_in_role_at_event(
    data_layer: DataLayer, event: Event
) -> ListOfVolunteersWithIdInRoleAtEvent:
    volunteer_role_data = VolunteerRotaData(data_layer)
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


def get_list_of_volunteer_roles_for_event_across_days(
    data_layer: DataLayer, event: Event, volunteer_at_event: DEPRECATE_VolunteerAtEvent
) -> List[VolunteerWithIdInRoleAtEvent]:
    volunteer_rota_data = VolunteerRotaData(data_layer)
    list_of_volunteer_roles = [
        volunteer_rota_data.get_volunteer_with_role_at_event_on_day_for_volunteer_at_event(
            event=event, volunteer_at_event=volunteer_at_event, day=day
        )
        for day in event.days_in_event()
    ]

    return list_of_volunteer_roles


def get_roles_for_group_info(
    cache: AdHocCache,
    event: Event,
    volunteer_in_role_at_event_on_day: VolunteerWithIdInRoleAtEvent,
) -> List[VolunteerWithIdInRoleAtEvent]:
    list_of_volunteers_at_event = cache.get_from_cache(
        load_list_of_volunteers_at_event, event=event
    )
    availability = list_of_volunteers_at_event.volunteer_at_event_with_id(
        volunteer_id=volunteer_in_role_at_event_on_day.volunteer_id
    ).availablity
    volunteers_in_role_at_event_with_active_allocations = cache.get_from_cache(
        get_volunteers_in_role_at_event_with_active_allocations, event=event
    )

    all_volunteers_in_roles_at_event_including_no_role_set = [
        volunteers_in_role_at_event_with_active_allocations.member_matching_volunteer_id_and_day(
            volunteer_id=volunteer_in_role_at_event_on_day.volunteer_id, day=day
        )
        for day in availability.days_available()
    ]

    return all_volunteers_in_roles_at_event_including_no_role_set
