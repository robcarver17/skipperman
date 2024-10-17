from dataclasses import dataclass

from app.OLD_backend.rota.rota_cadet_and_volunteer_data import get_cadet_location_string
from app.OLD_backend.rota.volunteer_rota import load_list_of_volunteers_at_event, \
    get_volunteers_in_role_at_event_with_active_allocations, \
    get_volunteer_role_and_group_event_on_day_for_volunteer_at_event
from app.OLD_backend.volunteers.volunteers import load_list_of_volunteer_skills, get_sorted_list_of_volunteers

from app.data_access.store.DEPRECATE_ad_hoc_cache import AdHocCache

from app.objects.day_selectors import Day
from app.objects.events import Event
from app.objects.exceptions import arg_not_passed
from app.objects.utils import print_dict_nicely
from app.objects.composed.volunteers_with_skills import SkillsDict, DictOfVolunteersWithSkills
from app.objects_OLD.volunteers_at_event import ListOfVolunteersAtEvent, DEPRECATE_VolunteerAtEvent
from app.objects_OLD.volunteers_in_roles import FILTER_ALL, FILTER_AVAILABLE, \
    FILTER_UNAVAILABLE, FILTER_ALLOC_AVAILABLE, FILTER_UNALLOC_AVAILABLE
from app.objects.volunteer_roles_and_groups_with_id import ListOfVolunteersWithIdInRoleAtEvent


@dataclass
class RotaSortsAndFilters:
    sort_by_volunteer_name: str
    sort_by_day: Day
    skills_filter: SkillsDict
    availability_filter: dict
    sort_by_location: bool



def get_sorted_and_filtered_list_of_volunteers_at_event(
    cache: AdHocCache,
        event: Event,
    sorts_and_filters: RotaSortsAndFilters,
) -> ListOfVolunteersAtEvent:
    list_of_volunteers_at_event = (
        filtered_list_of_volunteers_at_event(cache=cache, event=event, sorts_and_filters=sorts_and_filters)
    )
    sorted_list_of_volunteers_at_event = sort_list_of_volunteers_at_event(
        cache=cache,
        list_of_volunteers_at_event=list_of_volunteers_at_event,
        sorts_and_filters=sorts_and_filters,
    )

    return sorted_list_of_volunteers_at_event

def filtered_list_of_volunteers_at_event(
    cache: AdHocCache, event: Event, sorts_and_filters: RotaSortsAndFilters
) -> ListOfVolunteersAtEvent:
    skills_filter = sorts_and_filters.skills_filter
    original_list_of_volunteers_at_event_with_ids = cache.get_from_cache(load_list_of_volunteers_at_event,
        event=event)

    volunteer_skills = cache.get_from_cache(load_list_of_volunteer_skills)
    availability_filter_dict = sorts_and_filters.availability_filter
    list_of_volunteers_in_roles_at_event = cache.get_from_cache(get_volunteers_in_role_at_event_with_active_allocations,
            event=event)

    new_list = ListOfVolunteersAtEvent(
        [
            volunteer
            for volunteer in original_list_of_volunteers_at_event_with_ids
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


def filter_volunteer(
    volunteer_at_event: DEPRECATE_VolunteerAtEvent,
    list_of_volunteers_in_roles_at_event: ListOfVolunteersWithIdInRoleAtEvent,
    skills_filter: SkillsDict,
    volunteer_skills: DictOfVolunteersWithSkills,
    availability_filter_dict: dict,
) -> bool:
    filter_by_skills = filter_volunteer_by_skills(
        volunteer_at_event=volunteer_at_event,
        skills_filter=skills_filter,
        volunteer_skills=volunteer_skills,
    )
    filter_by_availability = filter_volunteer_by_availability(
        volunteer_at_event=volunteer_at_event,
        list_of_volunteers_in_roles_at_event=list_of_volunteers_in_roles_at_event,
        availability_filter_dict=availability_filter_dict,
    )

    return filter_by_skills and filter_by_availability


def filter_volunteer_by_skills(
    volunteer_at_event: DEPRECATE_VolunteerAtEvent,
    skills_filter: SkillsDict,
    volunteer_skills: DictOfVolunteersWithSkills,
) -> bool:
    volunteer_skills = volunteer_skills.skills_for_volunteer_id(
        volunteer_id=volunteer_at_event.volunteer_id
    )
    if not any(skills_filter.values()):
        ## nothing to filter on
        return True

    required_skill_present = [
        skill
        for skill, filter_by_this_skill in skills_filter.items()
        if filter_by_this_skill and skill in volunteer_skills
    ]

    return any(required_skill_present)


def filter_volunteer_by_availability(
    volunteer_at_event: DEPRECATE_VolunteerAtEvent,
    list_of_volunteers_in_roles_at_event: ListOfVolunteersWithIdInRoleAtEvent,
    availability_filter_dict: dict,
) -> bool:
    filter_by_day = [
        filter_volunteer_by_availability_on_given_day(
            volunteer_at_event=volunteer_at_event,
            list_of_volunteers_in_roles_at_event=list_of_volunteers_in_roles_at_event,
            day=Day[name_of_day],
            availability_filter=availability_filter,
        )
        for name_of_day, availability_filter in availability_filter_dict.items()
    ]

    return all(filter_by_day)


def filter_volunteer_by_availability_on_given_day(
    volunteer_at_event: DEPRECATE_VolunteerAtEvent,
    list_of_volunteers_in_roles_at_event: ListOfVolunteersWithIdInRoleAtEvent,
    day: Day,
    availability_filter: str,
) -> bool:
    if availability_filter == FILTER_ALL:
        return True  ## no filtering

    role_today = (
        list_of_volunteers_in_roles_at_event.member_matching_volunteer_id_and_day(
            volunteer_at_event.volunteer_id, day=day, return_empty_if_missing=True
        )
    )

    unallocated = role_today.no_role_set
    allocated = not unallocated
    available = volunteer_at_event.available_on_day(day)

    if availability_filter == FILTER_AVAILABLE:
        return available
    elif availability_filter == FILTER_UNAVAILABLE:
        return not available
    elif availability_filter == FILTER_ALLOC_AVAILABLE:
        return available and allocated
    elif availability_filter == FILTER_UNALLOC_AVAILABLE:
        return available and unallocated

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
    list_of_volunteers_at_event: ListOfVolunteersAtEvent,
    cache: AdHocCache,
) -> ListOfVolunteersAtEvent:
    list_of_locations = [
        cache.get_from_cache(get_cadet_location_string,
             volunteer_at_event=volunteer_at_event
        )
        for volunteer_at_event in list_of_volunteers_at_event
    ]

    locations_and_volunteers = zip(list_of_locations, list_of_volunteers_at_event)

    sorted_by_location = sorted(locations_and_volunteers, key=lambda tup: tup[0])
    sorted_list_of_volunteers = ListOfVolunteersAtEvent(
        [location_and_volunteer[1] for location_and_volunteer in sorted_by_location]
    )

    return sorted_list_of_volunteers


def sort_volunteer_data_for_event_by_name_sort_order(
    cache: AdHocCache,
    volunteers_at_event: ListOfVolunteersAtEvent,
    sort_order: str,
) -> ListOfVolunteersAtEvent:
    list_of_all_volunteers = cache.get_from_cache(get_sorted_list_of_volunteers,
         sort_by=sort_order
    )
    ## this works because if an ID is missing we just ignore it
    return volunteers_at_event.sort_by_list_of_volunteer_ids(
        list_of_all_volunteers.list_of_ids
    )



def sort_volunteer_data_for_event_by_day_sort_order(
    cache: AdHocCache,
    list_of_volunteers_at_event: ListOfVolunteersAtEvent,
    sort_by_day: Day,
) -> ListOfVolunteersAtEvent:
    tuple_of_volunteers_at_event_and_roles = [
        (
            volunteer_at_event,
            cache.get_from_cache(get_volunteer_role_and_group_event_on_day_for_volunteer_at_event,
                                 event = volunteer_at_event.event,
                                 volunteer_at_event=volunteer_at_event, day=sort_by_day,
                                 ))

        for volunteer_at_event in list_of_volunteers_at_event
    ]

    tuple_of_volunteers_at_event_and_roles.sort(key=lambda tup: tup[1])

    list_of_volunteers = [
        volunteer_at_event
        for volunteer_at_event, __ in tuple_of_volunteers_at_event_and_roles
    ]

    return ListOfVolunteersAtEvent(list_of_volunteers)



def get_explanation_of_sorts_and_filters(sorts_and_filters: RotaSortsAndFilters):
    explanation = ""
    if sorts_and_filters.sort_by_volunteer_name is not arg_not_passed:
        explanation += (
            "Sorting by: volunteer name (%s). "
            % sorts_and_filters.sort_by_volunteer_name
        )
    if sorts_and_filters.sort_by_day is not arg_not_passed:
        explanation += (
            " Sorting by: group / role on %s. " % sorts_and_filters.sort_by_day.name
        )
    if sorts_and_filters.sort_by_location:
        explanation += " Sorting by: cadet location. "

    explanation += print_dict_nicely(
        " Availability filter", sorts_and_filters.availability_filter
    )
    explanation += explain_skills_filter(skills_filter=sorts_and_filters.skills_filter, prepend_text=" Skills filter")

    return explanation


def explain_skills_filter(skills_filter: SkillsDict, prepend_text: str) -> str:
    if skills_filter.empty():
        return ""

    return " %s: %s" % (prepend_text, skills_filter.skills_held_as_str())

