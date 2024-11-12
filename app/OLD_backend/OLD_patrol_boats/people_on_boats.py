from app.data_access.store.DEPRECATE_ad_hoc_cache import AdHocCache

from app.data_access.configuration.skills_and_roles import volunteer_roles
from app.objects.day_selectors import Day
from app.objects.events import Event
from app.objects.patrol_boats import PatrolBoat
from app.objects_OLD.patrol_boats import (
    ListOfVolunteersAtEventWithSkillsAndRolesAndPatrolBoats,
)
from app.objects.utils import in_x_not_in_y
from app.OLD_backend.OLD_patrol_boats.data import (
    get_list_of_voluteers_at_event_with_patrol_boats_from_cache,
)


def get_sorted_volunteers_allocated_to_patrol_boat_at_event_on_days_sorted_by_role(
    cache: AdHocCache, patrol_boat: PatrolBoat, day: Day, event: Event
) -> ListOfVolunteersAtEventWithSkillsAndRolesAndPatrolBoats:
    all_volunteers = get_list_of_voluteers_at_event_with_patrol_boats_from_cache(
        cache=cache, event=event
    )
    volunteers_on_boat_on_day = all_volunteers.assigned_to_boat_on_day(
        patrol_boat=patrol_boat, day=day
    )

    return sort_list_of_volunteers_for_day_and_event_by_role(
        volunteers_on_boat_on_day=volunteers_on_boat_on_day,
        day=day,
    )


def sort_list_of_volunteers_for_day_and_event_by_role(
    day: Day,
    volunteers_on_boat_on_day: ListOfVolunteersAtEventWithSkillsAndRolesAndPatrolBoats,
) -> ListOfVolunteersAtEventWithSkillsAndRolesAndPatrolBoats:
    new_list = ListOfVolunteersAtEventWithSkillsAndRolesAndPatrolBoats()
    for role in volunteer_roles:
        list_of_volunteers_with_this_role = (
            volunteers_on_boat_on_day.has_volunteer_role(day=day, role=role)
        )
        new_list += list_of_volunteers_with_this_role

    remaining_not_in_any_role = in_x_not_in_y(x=volunteers_on_boat_on_day, y=new_list)
    new_list += remaining_not_in_any_role

    return new_list
