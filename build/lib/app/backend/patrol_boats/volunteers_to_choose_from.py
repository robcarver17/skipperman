from copy import copy

from app.objects.volunteers import ListOfVolunteers

from app.data_access.store.object_store import ObjectStore

from app.objects.day_selectors import Day
from app.objects.events import Event

from app.objects.composed.volunteers_with_all_event_data import (
    DictOfAllEventDataForVolunteers,
    AllEventDataForVolunteer,
)

from app.backend.volunteers.volunteers_at_event import (
    get_dict_of_all_event_data_for_volunteers,
)


def get_sorted_volunteer_data_for_volunteers_at_event_but_not_yet_on_patrol_boats_on_given_day(
    object_store: ObjectStore,
    event: Event,
    day: Day,
) -> DictOfAllEventDataForVolunteers:
    volunteer_data_for_volunteers_at_event_but_not_yet_on_patrol_boats_on_given_day = get_volunteer_data_for_volunteers_at_event_but_not_yet_on_patrol_boats_on_given_day(
        object_store=object_store, event=event, day=day
    )

    sorted_volunteer_data = sort_volunteer_data_by_role_on_day_and_skills_and_then_name(
        event_data=volunteer_data_for_volunteers_at_event_but_not_yet_on_patrol_boats_on_given_day,
        day=day,
    )

    return sorted_volunteer_data


def get_volunteer_data_for_volunteers_at_event_but_not_yet_on_patrol_boats_on_given_day(
    object_store: ObjectStore, event: Event, day: Day
) -> DictOfAllEventDataForVolunteers:
    dict_of_all_event_data_for_volunteers = get_dict_of_all_event_data_for_volunteers(
        object_store=object_store, event=event
    )

    return dict_of_all_event_data_for_volunteers.not_on_patrol_boat_on_given_day(day)


def sort_volunteer_data_by_role_on_day_and_skills_and_then_name(
    event_data: DictOfAllEventDataForVolunteers, day: Day
) -> DictOfAllEventDataForVolunteers:
    sorted_list_of_volunteers = ListOfVolunteers([])

    volunteers_in_boat_related_roles_on_day_of_event = (
        get_volunteers_in_boat_related_roles_on_day_of_event(event_data, day=day)
    )

    sorted_list_of_volunteers = move_volunteers_from_list_to_sorted_list(
        sorted_list_of_volunteers=sorted_list_of_volunteers,
        volunteers_to_move=volunteers_in_boat_related_roles_on_day_of_event,
    )

    all_volunteers_allocated_to_any_boat_or_day = (
        get_all_volunteers_allocated_to_any_boat_or_day(event_data)
    )

    sorted_list_of_volunteers = move_volunteers_from_list_to_sorted_list(
        sorted_list_of_volunteers=sorted_list_of_volunteers,
        volunteers_to_move=all_volunteers_allocated_to_any_boat_or_day,
    )

    list_of_volunteers_with_boat_skills = (
        get_list_of_volunteers_who_can_drive_safety_boat(event_data)
    )

    sorted_list_of_volunteers = move_volunteers_from_list_to_sorted_list(
        sorted_list_of_volunteers=sorted_list_of_volunteers,
        volunteers_to_move=list_of_volunteers_with_boat_skills,
    )

    ## Everyone else
    list_of_volunteers_to_choose_from = copy(event_data.list_of_volunteers())
    list_of_volunteers_to_choose_from_sorted_by_name = (
        list_of_volunteers_to_choose_from.sort_by_firstname()
    )

    sorted_list_of_volunteers = move_volunteers_from_list_to_sorted_list(
        sorted_list_of_volunteers=sorted_list_of_volunteers,
        volunteers_to_move=list_of_volunteers_to_choose_from_sorted_by_name,
    )

    return event_data.sort_by_list_of_volunteers(sorted_list_of_volunteers)


def move_volunteers_from_list_to_sorted_list(
    sorted_list_of_volunteers: ListOfVolunteers, volunteers_to_move: ListOfVolunteers
) -> ListOfVolunteers:

    for volunteer in volunteers_to_move:
        if volunteer not in sorted_list_of_volunteers:
            sorted_list_of_volunteers.append(volunteer)

    return sorted_list_of_volunteers


def get_volunteers_in_boat_related_roles_on_day_of_event(
    event_data: DictOfAllEventDataForVolunteers, day: Day
) -> ListOfVolunteers:
    volunteer_list = []
    for volunteer, event_data_for_volunteer in event_data.items():
        if event_data_for_volunteer.patrol_boats.on_any_patrol_boat_on_given_day(day):
            volunteer_list.append(volunteer)

    return ListOfVolunteers(volunteer_list)


def get_all_volunteers_allocated_to_any_boat_or_day(
    event_data: DictOfAllEventDataForVolunteers,
) -> ListOfVolunteers:
    volunteer_list = [
        volunteer
        for volunteer, event_data_for_volunteer in event_data.items()
        if event_data_for_volunteer.patrol_boats.assigned_to_any_boat_on_any_day()
    ]

    return ListOfVolunteers(volunteer_list)


def get_list_of_volunteers_who_can_drive_safety_boat(
    event_data: DictOfAllEventDataForVolunteers,
) -> ListOfVolunteers:
    volunteer_list = [
        volunteer
        for volunteer, event_data_for_volunteer in event_data.items()
        if event_data_for_volunteer.volunteer_skills.can_drive_safety_boat
    ]

    return ListOfVolunteers(volunteer_list)


def string_if_volunteer_can_drive_else_empty(
    event_data_for_volunteer: AllEventDataForVolunteer,
) -> str:
    ### MUST BE IN BRACKETS OR WON'T WORK WITH GETTING VOLUNTEER NAME

    if event_data_for_volunteer.volunteer_skills.can_drive_safety_boat:
        return "(PB2)"  ## can be anything
    else:
        return ""


def boat_related_role_str_and_group_on_day_for_volunteer_at_event(
    event_data_for_volunteer: AllEventDataForVolunteer, day: Day
) -> str:
    role_and_group = event_data_for_volunteer.roles_and_groups.role_and_group_on_day(
        day
    )

    if role_and_group.role.is_no_role_set():
        return ""

    if role_and_group.group.is_unallocated:
        role_str = role_and_group.role.name
    else:
        role_str = "%s - %s" % (role_and_group.group.name, role_and_group.role.name)

    role_str = " (%s)" % role_str

    return role_str
