from app.objects.utils import in_x_not_in_y
from app.backend.volunteers.roles_and_teams import get_list_of_roles_with_skills

from app.backend.volunteers.volunteers_at_event import get_dict_of_all_event_data_for_volunteers

from app.data_access.store.object_store import ObjectStore
from app.objects.composed.volunteers_on_patrol_boats_with_skills_and_roles import \
    ListOfVolunteersAtEventWithSkillsAndRolesAndPatrolBoats, VolunteerAtEventWithSkillsAndRolesAndPatrolBoats, ListOfVolunteersAtEventWithSkillsAndRolesAndPatrolBoatsOnSpecificday

from app.objects.day_selectors import Day
from app.objects.events import Event
from app.objects.patrol_boats import PatrolBoat


def get_sorted_volunteers_allocated_to_patrol_boat_at_event_on_days_sorted_by_role(
    object_store: ObjectStore, patrol_boat: PatrolBoat, day: Day, event: Event
) -> ListOfVolunteersAtEventWithSkillsAndRolesAndPatrolBoatsOnSpecificday:
    all_volunteers = get_list_of_volunteers_at_event_with_skills_and_roles_and_patrol_boats(
        object_store=object_store, event=event
    )
    volunteers_on_boat_on_day = all_volunteers.assigned_to_boat_on_day(
        patrol_boat=patrol_boat, day=day
    )

    sorted_list_of_volunteers_on_boats = sort_list_of_volunteers_for_day_and_event_by_role(
        volunteers_on_boat_on_day=volunteers_on_boat_on_day,
        object_store=object_store,
    )

    return sorted_list_of_volunteers_on_boats


def get_list_of_volunteers_at_event_with_skills_and_roles_and_patrol_boats(object_store: ObjectStore,
                                                                           event: Event) -> ListOfVolunteersAtEventWithSkillsAndRolesAndPatrolBoats:
    all_event_data = get_dict_of_all_event_data_for_volunteers(
        object_store=object_store,
        event=event
    )
    list_of_volunteers = all_event_data.dict_of_volunteers_at_event_with_patrol_boats.list_of_volunteers_allocated_to_patrol_boat_at_event_on_any_day()

    return ListOfVolunteersAtEventWithSkillsAndRolesAndPatrolBoats(
        [VolunteerAtEventWithSkillsAndRolesAndPatrolBoats(
            event=event,
            volunteer=volunteer,
            skills=all_event_data.dict_of_volunteers_with_skills.dict_of_skills_for_volunteer(volunteer),
            patrol_boat_by_day=all_event_data.dict_of_volunteers_at_event_with_patrol_boats.patrol_boats_for_volunteer(volunteer),
            role_and_group_by_day=all_event_data.dict_of_volunteers_at_event_with_days_and_role.days_and_roles_for_volunteer(volunteer),
            availability=all_event_data.dict_of_registration_data_for_volunteers_at_event.get_data_for_volunteer(volunteer).availablity,
        )
         for volunteer in list_of_volunteers]
    )

def sort_list_of_volunteers_for_day_and_event_by_role(
        object_store: ObjectStore,
    volunteers_on_boat_on_day: ListOfVolunteersAtEventWithSkillsAndRolesAndPatrolBoatsOnSpecificday
) -> ListOfVolunteersAtEventWithSkillsAndRolesAndPatrolBoatsOnSpecificday:

    volunteer_roles = get_list_of_roles_with_skills(object_store)
    new_list = ListOfVolunteersAtEventWithSkillsAndRolesAndPatrolBoatsOnSpecificday()
    for role in volunteer_roles:
        list_of_volunteers_with_this_role = (
            volunteers_on_boat_on_day.has_volunteer_role_on_day(role=role)
        )
        new_list += list_of_volunteers_with_this_role

    remaining_not_in_any_role = in_x_not_in_y(x=volunteers_on_boat_on_day, y=new_list)
    new_list += remaining_not_in_any_role

    return new_list
