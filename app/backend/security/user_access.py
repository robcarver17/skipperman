from typing import List

from app.backend.volunteers.volunteers_with_roles_and_groups_at_event import (
    is_volunteer_senior_instructor_at_event,
)
from app.backend.rota.volunteer_table import get_list_of_groups_volunteer_is_instructor_for
from app.data_access.store.object_store import ObjectStore

from app.backend.events.list_of_events import get_sorted_list_of_events
from app.backend.groups.list_of_groups import order_list_of_groups

from app.objects.groups import Group
from app.objects.volunteers import Volunteer

from app.backend.volunteers.skills import is_volunteer_qualified_as_SI
from app.backend.events.cadets_at_event import get_list_of_all_groups_at_event

from app.backend.security.logged_in_user import (
    get_volunteer_for_logged_in_user_or_superuser,
    SUPERUSER,
)
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.events import ListOfEvents, Event


def get_list_of_events_entitled_to_see(
    object_store: ObjectStore, volunteer: Volunteer, sort_by: str
):
    all_events = get_sorted_list_of_events(object_store, sort_by=sort_by)
    all_events = ListOfEvents(
        [
            event
            for event in all_events
            if can_volunteer_see_event(
                object_store=object_store, event=event, volunteer=volunteer
            )
        ]
    )

    return all_events


def is_volunteer_SI_or_super_user(interface: abstractInterface):
    volunteer = get_volunteer_for_logged_in_user_or_superuser(interface)

    if volunteer is SUPERUSER:
        return True
    return is_volunteer_qualified_as_SI(
        object_store=interface.object_store, volunteer=volunteer
    )


def can_volunteer_see_event(
    object_store: ObjectStore, event: Event, volunteer: Volunteer
):
    if volunteer == SUPERUSER:
        return True

    list_of_groups = get_list_of_groups_volunteer_can_see(
        object_store=object_store, event=event, volunteer=volunteer
    )
    return len(list_of_groups) > 0


def get_list_of_groups_volunteer_can_see(
    object_store: ObjectStore, event: Event, volunteer: Volunteer
) -> List[Group]:
    can_see_all_groups = can_see_all_groups_and_award_qualifications(
        object_store=object_store, event=event, volunteer=volunteer
    )

    if can_see_all_groups:
        relevant_groups = get_list_of_all_groups_at_event(
            object_store=object_store, event=event
        )
    else:
        relevant_groups = get_list_of_groups_volunteer_is_instructor_for(
            object_store=object_store, event=event, volunteer=volunteer
        )

    ordered_groups = order_list_of_groups(
        object_store=object_store, list_of_groups=relevant_groups
    )

    return ordered_groups


def can_see_all_groups_and_award_qualifications(
    object_store: ObjectStore, event: Event, volunteer: Volunteer
) -> bool:
    is_superuser = volunteer == SUPERUSER
    if is_superuser:
        return True

    is_senior_instructor_at_event = is_volunteer_senior_instructor_at_event(
        object_store=object_store, event=event, volunteer=volunteer
    )

    return is_senior_instructor_at_event
