from dataclasses import dataclass

from app.backend.cadets_at_event.dict_of_all_cadet_at_event_data import (
    get_dict_of_all_event_info_for_cadets,
)

from app.backend.volunteers.list_of_volunteers import sort_list_of_volunteers
from app.backend.volunteers.roles_and_teams import (
    reorder_tuple_of_item_and_role_and_group,
)

from app.objects.volunteers import ListOfVolunteers

from app.backend.volunteers.volunteers_at_event import (
    get_dict_of_all_event_data_for_volunteers,
)

from app.data_access.store.object_store import ObjectStore

from app.backend.registration_data.cadet_and_volunteer_connections_at_event import (
    get_cadet_location_string_for_volunteer,
)
from app.objects.composed.volunteer_roles import no_role_set

from app.objects.day_selectors import Day
from app.objects.events import Event
from app.objects.utilities.exceptions import arg_not_passed
from app.objects.utilities.utils import print_dict_nicely
from app.objects.composed.volunteers_with_skills import (
    SkillsDict,
)
from app.objects.composed.volunteers_with_all_event_data import (
    DictOfAllEventDataForVolunteers,
    AllEventDataForVolunteer,
)


@dataclass
class RotaSortsAndFilters:
    sort_by_volunteer_name: str
    sort_by_day: Day
    skills_filter: SkillsDict
    availability_filter: dict
    sort_by_location: bool


def get_sorted_and_filtered_dict_of_volunteers_at_event(
    object_store: ObjectStore,
    event: Event,
    sorts_and_filters: RotaSortsAndFilters,
) -> DictOfAllEventDataForVolunteers:

    dict_of_all_event_data_for_volunteers = get_dict_of_all_event_data_for_volunteers(
        object_store=object_store, event=event
    )

    filtered_dict_of_all_event_data_for_volunteers = filter_dict_of_volunteers_at_event(
        sorts_and_filters=sorts_and_filters,
        dict_of_all_event_data_for_volunteers=dict_of_all_event_data_for_volunteers,
    )
    sorted_list_of_volunteers_at_event = sort_dict_of_volunteer_data_at_event(
        object_store=object_store,
        filtered_dict_of_all_event_data_for_volunteers=filtered_dict_of_all_event_data_for_volunteers,
        sorts_and_filters=sorts_and_filters,
    )

    return sorted_list_of_volunteers_at_event


def filter_dict_of_volunteers_at_event(
    dict_of_all_event_data_for_volunteers: DictOfAllEventDataForVolunteers,
    sorts_and_filters: RotaSortsAndFilters,
) -> DictOfAllEventDataForVolunteers:

    skills_filter = sorts_and_filters.skills_filter
    availability_filter_dict = sorts_and_filters.availability_filter

    list_of_volunteers = []

    for (
        volunteer,
        event_data_for_volunteer,
    ) in dict_of_all_event_data_for_volunteers.items():
        if volunteer_passes_filter(
            event_data_for_volunteer=event_data_for_volunteer,
            skills_filter=skills_filter,
            availability_filter_dict=availability_filter_dict,
        ):
            list_of_volunteers.append(volunteer)

    return dict_of_all_event_data_for_volunteers.sort_by_list_of_volunteers(
        ListOfVolunteers(list_of_volunteers)
    )


def volunteer_passes_filter(
    event_data_for_volunteer: AllEventDataForVolunteer,
    skills_filter: SkillsDict,
    availability_filter_dict: dict,
) -> bool:
    filter_by_skills = filter_volunteer_by_skills(
        event_data_for_volunteer=event_data_for_volunteer,
        skills_filter=skills_filter,
    )
    filter_by_availability = filter_volunteer_by_availability(
        event_data_for_volunteer=event_data_for_volunteer,
        availability_filter_dict=availability_filter_dict,
    )

    return filter_by_skills and filter_by_availability


def filter_volunteer_by_skills(
    event_data_for_volunteer: AllEventDataForVolunteer,
    skills_filter: SkillsDict,
) -> bool:
    volunteer_skills = event_data_for_volunteer.volunteer_skills.as_list_of_skills()
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
    event_data_for_volunteer: AllEventDataForVolunteer,
    availability_filter_dict: dict,
) -> bool:
    filter_by_day = [
        filter_volunteer_by_availability_on_given_day(
            event_data_for_volunteer=event_data_for_volunteer,
            day=Day[name_of_day],
            availability_filter=availability_filter,
        )
        for name_of_day, availability_filter in availability_filter_dict.items()
    ]

    return all(filter_by_day)


def filter_volunteer_by_availability_on_given_day(
    event_data_for_volunteer: AllEventDataForVolunteer,
    day: Day,
    availability_filter: str,
) -> bool:
    if availability_filter == FILTER_ALL:
        return True  ## no filtering

    role_today = event_data_for_volunteer.roles_and_groups.role_and_group_on_day(
        day
    ).role
    available = event_data_for_volunteer.registration_data.availablity.available_on_day(
        day
    )

    unallocated = role_today == no_role_set
    allocated = not unallocated

    if availability_filter == FILTER_AVAILABLE:
        return available
    elif availability_filter == FILTER_UNAVAILABLE:
        return not available
    elif availability_filter == FILTER_ALLOC_AVAILABLE:
        return available and allocated
    elif availability_filter == FILTER_UNALLOC_AVAILABLE:
        return available and unallocated


def sort_dict_of_volunteer_data_at_event(
    object_store: ObjectStore,
    filtered_dict_of_all_event_data_for_volunteers: DictOfAllEventDataForVolunteers,
    sorts_and_filters: RotaSortsAndFilters,
) -> DictOfAllEventDataForVolunteers:
    sort_by_location = sorts_and_filters.sort_by_location
    if sort_by_location:
        return sort_volunteer_data_for_event_by_location_of_connected_cadets(
            object_store=object_store,
            dict_of_all_event_data_for_volunteers=filtered_dict_of_all_event_data_for_volunteers,
        )

    sort_by_volunteer_name = sorts_and_filters.sort_by_volunteer_name
    if sort_by_volunteer_name is not arg_not_passed:
        return sort_volunteer_data_for_event_by_name_sort_order(
            dict_of_all_event_data_for_volunteers=filtered_dict_of_all_event_data_for_volunteers,
            sort_order=sort_by_volunteer_name,
        )

    sort_by_day = sorts_and_filters.sort_by_day
    if sort_by_day is not arg_not_passed:
        return sort_volunteer_data_for_event_by_day_sort_order(
            object_store=object_store,
            dict_of_all_event_data_for_volunteers=filtered_dict_of_all_event_data_for_volunteers,
            sort_by_day=sorts_and_filters.sort_by_day,
        )

    return filtered_dict_of_all_event_data_for_volunteers


def sort_volunteer_data_for_event_by_location_of_connected_cadets(
    object_store: ObjectStore,
    dict_of_all_event_data_for_volunteers: DictOfAllEventDataForVolunteers,
) -> DictOfAllEventDataForVolunteers:
    sorted_list_of_volunteers_at_event = (
        get_sorted_list_of_volunteers_at_event_sorted_by_location_of_connected_cadets(
            object_store=object_store,
            dict_of_all_event_data_for_volunteers=dict_of_all_event_data_for_volunteers,
        )
    )
    sorted_list_of_volunteer_event_data = (
        dict_of_all_event_data_for_volunteers.sort_by_list_of_volunteers(
            sorted_list_of_volunteers_at_event
        )
    )

    return sorted_list_of_volunteer_event_data


def get_sorted_list_of_volunteers_at_event_sorted_by_location_of_connected_cadets(
    object_store: ObjectStore,
    dict_of_all_event_data_for_volunteers: DictOfAllEventDataForVolunteers,
) -> ListOfVolunteers:
    dict_of_all_cadet_event_data = get_dict_of_all_event_info_for_cadets(
        object_store=object_store,
        event=dict_of_all_event_data_for_volunteers.event,
        active_only=True,
    )
    list_of_locations = [
        get_cadet_location_string_for_volunteer(
            volunteer_data_at_event=dict_of_all_event_data_for_volunteers.get_data_for_volunteer(
                volunteer
            ),
            dict_of_all_cadet_event_data=dict_of_all_cadet_event_data,
        )
        for volunteer in dict_of_all_event_data_for_volunteers.list_of_volunteers()
    ]

    list_of_volunteers_at_event = (
        dict_of_all_event_data_for_volunteers.list_of_volunteers()
    )
    locations_and_volunteers = zip(list_of_locations, list_of_volunteers_at_event)

    volunteers_and_location_sorted_by_location = sorted(
        locations_and_volunteers, key=lambda tup: tup[0]
    )
    sorted_list_of_volunteers_at_event = [
        location_and_volunteer[1]
        for location_and_volunteer in volunteers_and_location_sorted_by_location
    ]

    return ListOfVolunteers(sorted_list_of_volunteers_at_event)


def sort_volunteer_data_for_event_by_name_sort_order(
    dict_of_all_event_data_for_volunteers: DictOfAllEventDataForVolunteers,
    sort_order: str,
) -> DictOfAllEventDataForVolunteers:
    list_of_volunteers_at_event = (
        dict_of_all_event_data_for_volunteers.list_of_volunteers()
    )
    sorted_list_of_volunteers = sort_list_of_volunteers(
        list_of_volunteers=list_of_volunteers_at_event, sort_by=sort_order
    )
    sorted_dict_of_all_event_data_for_volunteers = (
        dict_of_all_event_data_for_volunteers.sort_by_list_of_volunteers(
            sorted_list_of_volunteers
        )
    )

    return sorted_dict_of_all_event_data_for_volunteers


def sort_volunteer_data_for_event_by_day_sort_order(
    object_store: ObjectStore,
    dict_of_all_event_data_for_volunteers: DictOfAllEventDataForVolunteers,
    sort_by_day: Day,
) -> DictOfAllEventDataForVolunteers:
    sorted_list_of_volunteers = (
        get_sorted_list_of_volunteers_at_event_sorted_by_role_and_group_on_day(
            object_store=object_store,
            dict_of_all_event_data_for_volunteers=dict_of_all_event_data_for_volunteers,
            sort_by_day=sort_by_day,
        )
    )

    return dict_of_all_event_data_for_volunteers.sort_by_list_of_volunteers(
        sorted_list_of_volunteers
    )


def get_sorted_list_of_volunteers_at_event_sorted_by_role_and_group_on_day(
    object_store: ObjectStore,
    dict_of_all_event_data_for_volunteers: DictOfAllEventDataForVolunteers,
    sort_by_day: Day,
) -> ListOfVolunteers:

    tuple_of_volunteers_at_event_and_roles = [
        (
            volunteer,
            volunteer_data.roles_and_groups.role_and_group_on_day(day=sort_by_day),
        )
        for volunteer, volunteer_data in dict_of_all_event_data_for_volunteers.items()
    ]
    sorted_tuples = reorder_tuple_of_item_and_role_and_group(
        object_store=object_store, list_of_tuples=tuple_of_volunteers_at_event_and_roles
    )

    sorted_list_of_volunteers = ListOfVolunteers([tuple[0] for tuple in sorted_tuples])

    return sorted_list_of_volunteers


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
    explanation += explain_skills_filter(
        skills_filter=sorts_and_filters.skills_filter, prepend_text=" Skills filter"
    )

    return explanation


def explain_skills_filter(skills_filter: SkillsDict, prepend_text: str) -> str:
    if skills_filter.empty():
        return ""

    return " %s: %s" % (prepend_text, skills_filter.skills_held_as_str())


FILTER_ALL = "All"
FILTER_AVAILABLE = "Available"
FILTER_UNALLOC_AVAILABLE = "Unallocated+Available"
FILTER_ALLOC_AVAILABLE = "Allocated+Available"
FILTER_UNAVAILABLE = "Unavailable"
FILTER_OPTIONS = [
    FILTER_ALL,
    FILTER_AVAILABLE,
    FILTER_UNALLOC_AVAILABLE,
    FILTER_ALLOC_AVAILABLE,
    FILTER_UNAVAILABLE,
]
