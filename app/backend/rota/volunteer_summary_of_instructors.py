from typing import Dict, List

from app.backend.cadets_at_event.dict_of_all_cadet_at_event_data import (
    get_dict_of_all_event_info_for_cadets,
)
from app.backend.groups.group_notes_at_event import get_dict_of_group_notes_at_event
from app.backend.rota.volunteer_rota_summary import (
    get_sorted_list_of_groups_at_event,
    get_sorted_roles_at_event,
)
from app.backend.volunteers.roles_and_teams import get_dict_of_teams_and_roles
from app.backend.volunteers.volunteers_at_event import (
    get_dict_of_all_event_data_for_volunteers,
)
from app.data_access.configuration.configuration import MAX_GROUP_SIZE_PER_INSTRUCTOR
from app.data_access.store.object_store import ObjectStore
from app.objects.composed.volunteer_roles import RoleWithSkills
from app.objects.composed.volunteer_with_group_and_role_at_event import (
    DictOfVolunteersAtEventWithDictOfDaysRolesAndGroups,
)
from app.objects.day_selectors import Day
from app.objects.events import Event
from app.objects.groups import Group
from app.objects.utilities.utils import flatten
from app.objects.abstract_objects.abstract_tables import Table, RowInTable
from app.objects.abstract_objects.abstract_form import textAreaInput


def get_summary_table_of_instructors_and_groups_for_event(
    object_store: ObjectStore, event: Event
) -> Table:
    volunteer_event_data = get_dict_of_all_event_data_for_volunteers(
        object_store=object_store, event=event
    )
    volunteers_in_roles_at_event = (
        volunteer_event_data.dict_of_volunteers_at_event_with_days_and_roles
    )
    sorted_list_of_groups = get_sorted_list_of_groups_at_event(
        object_store=object_store, event=event
    )
    list_of_instructor_type_roles_at_event_sorted_by_seniority = (
        get_list_of_instructor_type_roles_at_event_sorted_by_seniority(
            object_store, event
        )
    )

    list_of_rows = [
        get_top_row_of_table_of_instructor_counts(
            event=event,
            list_of_instructor_type_roles_at_event_sorted_by_seniority=list_of_instructor_type_roles_at_event_sorted_by_seniority,
        )
    ]
    for group in sorted_list_of_groups:
        this_row = get_summary_row_of_instructors_for_group_at_event(
            object_store=object_store,
            volunteers_in_roles_at_event=volunteers_in_roles_at_event,
            group=group,
            list_of_instructor_type_roles_at_event_sorted_by_seniority=list_of_instructor_type_roles_at_event_sorted_by_seniority,
        )
        list_of_rows.append(this_row)

    return Table(list_of_rows, has_column_headings=True, has_row_headings=True)


def get_top_row_of_table_of_instructor_counts(
    event: Event, list_of_instructor_type_roles_at_event_sorted_by_seniority: list
) -> RowInTable:
    list_of_days = [day.name for day in event.days_in_event()]
    instructor_roles_as_names = [
        role.name for role in list_of_instructor_type_roles_at_event_sorted_by_seniority
    ]
    return RowInTable(
        [
            "",
        ]
        + list_of_days
        + instructor_roles_as_names
        + ["NOTES", "Instructor count", "Spare capacity"]
    )


def get_summary_row_of_instructors_for_group_at_event(
    object_store: ObjectStore,
    volunteers_in_roles_at_event: DictOfVolunteersAtEventWithDictOfDaysRolesAndGroups,
    group: Group,
    list_of_instructor_type_roles_at_event_sorted_by_seniority: list,
) -> RowInTable:
    cadet_count_for_group_over_days_as_dict = (
        get_cadet_count_for_group_over_days_as_dict(
            object_store=object_store,
            event=volunteers_in_roles_at_event.event,
            group=group,
        )
    )
    cadet_count_for_group_over_days = get_cadet_count_for_group_over_days(
        cadet_count_for_group_over_days_as_dict, group=group
    )

    instructor_names = [
        get_names_of_instructor_with_day_annotation_or_blank_with_role_in_group(
            volunteers_in_roles_at_event=volunteers_in_roles_at_event,
            role=role,
            group=group,
        )
        for role in list_of_instructor_type_roles_at_event_sorted_by_seniority
    ]
    instructor_count_allocated_to_group_as_dict = (
        get_instructor_count_allocated_to_group_as_dict(
            volunteers_in_roles_at_event=volunteers_in_roles_at_event,
            group=group,
        )
    )
    instructor_count = get_instructor_count_allocated_to_group_with_day_annotation(
        volunteers_in_roles_at_event=volunteers_in_roles_at_event,
        group=group,
    )
    group_notes = get_group_notes_for_group(
        object_store=object_store, event=volunteers_in_roles_at_event.event, group=group
    )

    warning = display_warning(
        cadet_count_for_group_over_days_as_dict=cadet_count_for_group_over_days_as_dict,
        instructor_count_allocated_to_group_as_dict=instructor_count_allocated_to_group_as_dict,
    )

    return RowInTable(
        [group.name]
        + cadet_count_for_group_over_days
        + instructor_names
        + [group_notes, instructor_count, warning]
    )


def display_warning(
    cadet_count_for_group_over_days_as_dict: Dict[str, int],
    instructor_count_allocated_to_group_as_dict: Dict[str, int],
):
    list_of_warnings = []
    for day in cadet_count_for_group_over_days_as_dict.keys():
        cadets = cadet_count_for_group_over_days_as_dict[day]
        instructors = instructor_count_allocated_to_group_as_dict[day]
        spare = (instructors * MAX_GROUP_SIZE_PER_INSTRUCTOR) - cadets

        if spare < 0:
            list_of_warnings.append("%s: %d OVER RATIO!" % (day[:3], -spare))
        else:
            list_of_warnings.append("%s: space for %d" % (day[:3], spare))

    return ", ".join(list_of_warnings)


def get_group_notes_for_group(
    object_store: ObjectStore, event: Event, group: Group
) -> textAreaInput:
    dict_of_group_notes = get_dict_of_group_notes_at_event(
        object_store=object_store, event=event
    )
    notes = dict_of_group_notes.notes_for_group(group)

    return textAreaInput(
        input_label="", input_name=get_group_notes_field_value(group), value=notes
    )


def get_group_notes_field_value(group: Group) -> str:
    return "GROUP_NOTES_%s" % group.id


def get_names_of_instructor_with_day_annotation_or_blank_with_role_in_group(
    volunteers_in_roles_at_event: DictOfVolunteersAtEventWithDictOfDaysRolesAndGroups,
    role: RoleWithSkills,
    group: Group,
):
    dict_of_instructors_by_day = (
        get_dict_of_instructors_by_day_for_specific_role_in_group(
            volunteers_in_roles_at_event=volunteers_in_roles_at_event,
            role=role,
            group=group,
        )
    )

    if check_all_instructors_same_across_days(dict_of_instructors_by_day):
        instructors_on_first_day = list(dict_of_instructors_by_day.values())[0]
        return ", ".join(instructors_on_first_day)
    else:
        return annotate_dict_of_instructors(dict_of_instructors_by_day)


def get_dict_of_instructors_by_day_for_specific_role_in_group(
    volunteers_in_roles_at_event: DictOfVolunteersAtEventWithDictOfDaysRolesAndGroups,
    role: RoleWithSkills,
    group: Group,
):
    days_in_event = volunteers_in_roles_at_event.event.days_in_event()

    dict_of_instructors_by_day = {}
    for day in days_in_event:
        list_of_volunteers = get_list_of_instructors_on_day_for_specific_role_in_group(
            volunteers_in_roles_at_event=volunteers_in_roles_at_event,
            role=role,
            group=group,
            day=day
        )
        dict_of_instructors_by_day[day] = list_of_volunteers

    return dict_of_instructors_by_day

def get_list_of_instructors_on_day_for_specific_role_in_group(
        volunteers_in_roles_at_event: DictOfVolunteersAtEventWithDictOfDaysRolesAndGroups,
        role: RoleWithSkills,
        group: Group,
        day: Day
) -> List[str]:
    list_of_volunteers = volunteers_in_roles_at_event.list_of_volunteers_with_roles_and_groups_and_teams_doing_role_on_day(
        role=role, day=day
    )
    list_of_volunteers = [
        volunteer_with_group.volunteer.name
        for volunteer_with_group in list_of_volunteers
        if volunteer_with_group.group == group
    ]
    list_of_volunteers.sort()

    return list_of_volunteers

def check_all_instructors_same_across_days(
    dict_of_instructors_by_day: Dict[Day, List[str]]
):
    return check_all_equal(list(dict_of_instructors_by_day.values()))


def check_count_of_instructors_same_across_days(
    dict_of_instructors_by_day: Dict[Day, List[str]]
):
    return check_all_equal(
        [
            len(instructors_on_day)
            for instructors_on_day in list(dict_of_instructors_by_day.values())
        ]
    )


def check_all_equal(some_list: list):
    return all(i == some_list[0] for i in some_list)


def annotate_dict_of_instructors(dict_of_instructors_by_day: Dict[Day, List[str]]):
    all_instructors = list(set(flatten(list(dict_of_instructors_by_day.values()))))
    all_instructors.sort()
    annotated_list = [
        annotate_specific_instructor(
            dict_of_instructors_by_day=dict_of_instructors_by_day, instructor=instructor
        )
        for instructor in all_instructors
    ]

    return ", ".join(annotated_list)


def annotate_specific_instructor(
    dict_of_instructors_by_day: Dict[Day, List[str]], instructor: str
) -> str:
    if instructor_present_for_all_days(
        dict_of_instructors_by_day=dict_of_instructors_by_day, instructor=instructor
    ):
        return instructor
    list_of_days = days_present_for(
        dict_of_instructors_by_day=dict_of_instructors_by_day, instructor=instructor
    )

    return "%s (%s)" % (instructor, ", ".join(list_of_days))


def instructor_present_for_all_days(
    dict_of_instructors_by_day: Dict[Day, List[str]], instructor: str
) -> bool:
    return all(
        instructor in instructors_for_day
        for instructors_for_day in list(dict_of_instructors_by_day.values())
    )


def days_present_for(dict_of_instructors_by_day: Dict[Day, List[str]], instructor: str):
    list_of_days = [
        day.name[:3]
        for day, instructors_on_day in dict_of_instructors_by_day.items()
        if instructor in instructors_on_day
    ]

    return list_of_days


def get_instructor_count_allocated_to_group_with_day_annotation(
    volunteers_in_roles_at_event: DictOfVolunteersAtEventWithDictOfDaysRolesAndGroups,
    group: Group,
):
    if group.is_unallocated:
        return ""

    dict_of_instructors_by_day_for_group = get_dict_of_instructors_by_day_for_group(
        volunteers_in_roles_at_event=volunteers_in_roles_at_event, group=group
    )

    if check_count_of_instructors_same_across_days(
        dict_of_instructors_by_day_for_group
    ):
        instructors_on_first_day = list(dict_of_instructors_by_day_for_group.values())[
            0
        ]
        print(instructors_on_first_day)
        return len(instructors_on_first_day)
    else:
        return annotate_count_across_days(dict_of_instructors_by_day_for_group)


def get_instructor_count_allocated_to_group_as_dict(
    volunteers_in_roles_at_event: DictOfVolunteersAtEventWithDictOfDaysRolesAndGroups,
    group: Group,
) -> Dict[str, int]:
    dict_of_instructors_by_day_for_group = get_dict_of_instructors_by_day_for_group(
        volunteers_in_roles_at_event=volunteers_in_roles_at_event, group=group
    )
    result_dict = {}
    for day in volunteers_in_roles_at_event.event.days_in_event():
        result_dict[day.name] = len(dict_of_instructors_by_day_for_group[day])

    return result_dict


def get_dict_of_instructors_by_day_for_group(
    volunteers_in_roles_at_event: DictOfVolunteersAtEventWithDictOfDaysRolesAndGroups,
    group: Group,
):
    days_in_event = volunteers_in_roles_at_event.event.days_in_event()

    dict_of_instructors_by_day = {}
    for day in days_in_event:
        list_of_volunteers = volunteers_in_roles_at_event.list_of_volunteers_with_roles_and_groups_and_teams_assigned_to_group_on_day(
            day=day, group=group
        )
        list_of_volunteers = [
            volunteer_with_group.volunteer.name
            for volunteer_with_group in list_of_volunteers
            if volunteer_with_group.in_instructor_team()
        ]
        list_of_volunteers.sort()
        dict_of_instructors_by_day[day] = list_of_volunteers

    return dict_of_instructors_by_day


def annotate_count_across_days(
    dict_of_instructors_by_day_for_group: Dict[Day, List[str]]
):
    list_of_labelled_counts = [
        "%d (%s)" % (len(instructors_on_day), day.name[:3])
        for day, instructors_on_day in dict_of_instructors_by_day_for_group.items()
    ]

    return ", ".join(list_of_labelled_counts)


def get_list_of_instructor_type_roles_at_event_sorted_by_seniority(
    object_store: ObjectStore, event: Event
):
    teams_and_roles = get_dict_of_teams_and_roles(object_store)
    roles_in_instructor_team = teams_and_roles.roles_in_instructor_team()

    roles_at_event = get_sorted_roles_at_event(object_store=object_store, event=event)
    sorted_list = []
    for role in roles_in_instructor_team:
        if role in roles_at_event:
            sorted_list.append(role)

    return sorted_list


def get_cadet_count_for_group_over_days(
    count_as_dict: Dict[Day, int], group: Group
) -> list:
    results = []
    for count in count_as_dict.items():
        if group.is_unallocated:
            results.append("")
        else:
            results.append(str(count))

    return results


def get_cadet_count_for_group_over_days_as_dict(
    object_store: ObjectStore, event: Event, group: Group
) -> Dict[str, int]:
    cadets_at_event_data = get_dict_of_all_event_info_for_cadets(object_store=object_store, event=event)
    dict_of_cadets_with_days_and_groups = (
        cadets_at_event_data.dict_of_cadets_with_days_and_groups
    )
    results = {}
    for day in cadets_at_event_data.event.days_in_event():
        if group.is_unallocated:
            results[day.name] = 0
        else:
            results[day.name] = len(
                dict_of_cadets_with_days_and_groups.list_of_cadets_in_group_on_day(
                    day=day, group=group
                )
            )

    return results
