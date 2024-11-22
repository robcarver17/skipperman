from typing import List, Dict

from app.backend.volunteers.volunteers_at_event import load_list_of_volunteers_at_event
from app.OLD_backend.volunteers.volunteers import DEPRECATE_get_volunteer_from_id
from app.backend.rota.changes import get_all_roles_across_recent_events_for_volunteer_as_list
from app.data_access.store.DEPRECATE_ad_hoc_cache import AdHocCache
from app.data_access.store.data_access import DataLayer
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.exceptions import arg_not_passed
from app.objects.events import Event, SORT_BY_START_ASC
from app.objects.volunteers import Volunteer
from app.objects_OLD.volunteers_at_event import (
    ListOfVolunteersAtEvent,
    DEPRECATE_VolunteerAtEvent,
)
from app.objects.volunteer_roles_and_groups_with_id import RoleAndGroupDEPRECATE


def DEPRECATE_get_dict_of_volunteers_with_last_roles(
    interface: abstractInterface, list_of_volunteer_ids: List[str], avoid_event: Event
) -> Dict[str, RoleAndGroupDEPRECATE]:
    return dict(
        [
            (
                volunteer_id,
                DEPRECATE_get_last_role_for_volunteer_id(
                    interface=interface,
                    volunteer_id=volunteer_id,
                    avoid_event=avoid_event,
                ),
            )
            for volunteer_id in list_of_volunteer_ids
        ]
    )


def get_dict_of_volunteers_with_last_roles(
    data_layer: DataLayer,
    list_of_volunteers_at_event: ListOfVolunteersAtEvent,
    avoid_event: Event,
) -> Dict[str, RoleAndGroupDEPRECATE]:
    return dict(
        [
            (
                volunteer_at_event.volunteer.id,
                get_last_role_for_volunteer_id(
                    data_layer=data_layer,
                    volunteer=volunteer_at_event.volunteer,
                    avoid_event=avoid_event,
                ),
            )
            for volunteer_at_event in list_of_volunteers_at_event
        ]
    )


def DEPRECATE_get_last_role_for_volunteer_id(
    interface: abstractInterface, volunteer_id: str, avoid_event: Event = arg_not_passed
) -> RoleAndGroupDEPRECATE:
    volunteer = DEPRECATE_get_volunteer_from_id(
        interface=interface, volunteer_id=volunteer_id
    )
    roles = get_all_roles_across_recent_events_for_volunteer_as_list(
        data_layer=interface.data,
        volunteer=volunteer,
        avoid_event=avoid_event,
        sort_by=SORT_BY_START_ASC,
    )
    if len(roles) == 0:
        return RoleAndGroupDEPRECATE()

    return roles[-1]  ## most recent role


def get_last_role_for_volunteer_id(
    data_layer: DataLayer, volunteer: Volunteer, avoid_event: Event = arg_not_passed
) -> RoleAndGroupDEPRECATE:
    roles = get_all_roles_across_recent_events_for_volunteer_as_list(
        data_layer=data_layer,
        volunteer=volunteer,
        avoid_event=avoid_event,
        sort_by=SORT_BY_START_ASC,
    )
    if len(roles) == 0:
        return RoleAndGroupDEPRECATE()

    return roles[-1]  ## most recent role


def get_previous_role_and_group_for_volunteer_at_event(
    cache: AdHocCache, volunteer_at_event: DEPRECATE_VolunteerAtEvent
) -> RoleAndGroupDEPRECATE:
    list_of_volunteers_at_event = cache.get_from_cache(
        load_list_of_volunteers_at_event, event=volunteer_at_event.event
    )

    dict_of_volunteers_with_last_roles = cache.get_from_cache(
        get_dict_of_volunteers_with_last_roles,
        list_of_volunteers_at_event=list_of_volunteers_at_event,
        avoid_event=volunteer_at_event.event,
    )

    previous_role = dict_of_volunteers_with_last_roles.get(
        volunteer_at_event.volunteer_id, RoleAndGroupDEPRECATE()
    )

    return previous_role
