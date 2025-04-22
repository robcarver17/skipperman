from typing import Dict, List

import pandas as pd

from app.backend.rota.volunteer_rota_summary import get_sorted_list_of_groups_at_event, get_sorted_roles_at_event
from app.backend.volunteers.roles_and_teams import get_dict_of_teams_and_roles
from app.backend.volunteers.volunteers_at_event import get_dict_of_all_event_data_for_volunteers
from app.data_access.store.object_store import ObjectStore
from app.objects.abstract_objects.abstract_tables import PandasDFTable
from app.objects.composed.volunteer_roles import RoleWithSkills
from app.objects.composed.volunteer_with_group_and_role_at_event import \
    DictOfVolunteersAtEventWithDictOfDaysRolesAndGroups
from app.objects.day_selectors import Day
from app.objects.events import Event
from app.objects.groups import Group
from app.objects.utils import flatten


def get_summary_list_of_instructors_and_groups_for_event(object_store: ObjectStore, event: Event) -> PandasDFTable:
    return PandasDFTable(
        get_summary_list_of_of_instructors_and_groups_for_event_as_pd_df(
            object_store=object_store, event=event
        )
    )


def get_summary_list_of_of_instructors_and_groups_for_event_as_pd_df(
    object_store: ObjectStore, event: Event
) -> pd.DataFrame:
    volunteer_event_data = get_dict_of_all_event_data_for_volunteers(
        object_store=object_store, event=event
    )
    volunteers_in_roles_at_event = (
        volunteer_event_data.dict_of_volunteers_at_event_with_days_and_roles
    )
    sorted_list_of_groups = get_sorted_list_of_groups_at_event(object_store=object_store, event=event)
    list_of_instructor_type_roles_at_event_sorted_by_seniority = get_list_of_instructor_type_roles_at_event_sorted_by_seniority(object_store, event)

    list_of_rows_as_dicts = []
    for group in sorted_list_of_groups:
        this_row = get_summary_row_of_instructors_for_group_at_event(
            object_store=object_store,
            volunteers_in_roles_at_event=volunteers_in_roles_at_event,
            group=group,
            list_of_instructor_type_roles_at_event_sorted_by_seniority=list_of_instructor_type_roles_at_event_sorted_by_seniority
        )
        list_of_rows_as_dicts.append(this_row)

    df =  pd.DataFrame(list_of_rows_as_dicts)
    df.index = sorted_list_of_groups

    return df


def get_summary_row_of_instructors_for_group_at_event( object_store: ObjectStore,
                                                       volunteers_in_roles_at_event: DictOfVolunteersAtEventWithDictOfDaysRolesAndGroups,
                                                       group: Group,
                                                       list_of_instructor_type_roles_at_event_sorted_by_seniority: list) -> dict:

    instructor_names_dict = dict([
                                (role.name,
        get_names_of_instructor_with_day_annotation_or_blank_with_role_in_group(
            volunteers_in_roles_at_event=volunteers_in_roles_at_event,
            role=role,
            group=group
        )
                                )
        for role in list_of_instructor_type_roles_at_event_sorted_by_seniority
    ])
    instructor_count = get_instructor_count_allocated_to_group_with_day_annotation(
        volunteers_in_roles_at_event=volunteers_in_roles_at_event,
        group=group,
        list_of_instructor_type_roles_at_event_sorted_by_seniority=list_of_instructor_type_roles_at_event_sorted_by_seniority
    )

    instructor_names_dict.update({'Instructor count': instructor_count})

    return instructor_names_dict


def get_names_of_instructor_with_day_annotation_or_blank_with_role_in_group(volunteers_in_roles_at_event: DictOfVolunteersAtEventWithDictOfDaysRolesAndGroups,
                                                                   role: RoleWithSkills,
                                                                   group: Group):
    dict_of_instructors_by_day = get_dict_of_instructors_by_day_for_specific_role_in_group(
        volunteers_in_roles_at_event=volunteers_in_roles_at_event,
        role=role,
        group=group
    )

    if check_all_instructors_same_across_days(dict_of_instructors_by_day):
        instructors_on_first_day =list(dict_of_instructors_by_day.values())[0]
        return ", ".join(instructors_on_first_day)
    else:
        return annotate_dict_of_instructors(dict_of_instructors_by_day)


def get_dict_of_instructors_by_day_for_specific_role_in_group(volunteers_in_roles_at_event: DictOfVolunteersAtEventWithDictOfDaysRolesAndGroups,
                                                              role: RoleWithSkills,
                                                              group: Group):
    days_in_event = volunteers_in_roles_at_event.event.days_in_event()

    dict_of_instructors_by_day = {}
    for day in days_in_event:
        list_of_volunteers = volunteers_in_roles_at_event.list_of_volunteers_with_roles_and_groups_and_teams_doing_role_on_day(
            role=role,
            day=day
        )
        list_of_volunteers = [volunteer_with_group.volunteer.name for volunteer_with_group in list_of_volunteers if volunteer_with_group.group == group]
        list_of_volunteers.sort()
        dict_of_instructors_by_day[day] = list_of_volunteers

    return dict_of_instructors_by_day


def check_all_instructors_same_across_days(dict_of_instructors_by_day: Dict[Day, List[str]]):
    return check_all_equal(list(dict_of_instructors_by_day.values()))


def check_all_equal(some_list:list):
    return all(i == some_list[0] for i in some_list)


def annotate_dict_of_instructors(dict_of_instructors_by_day: Dict[Day, List[str]]):
    all_instructors = list(set(flatten(list(dict_of_instructors_by_day.values()))))
    all_instructors.sort()
    annotated_list = [
        annotate_specific_instructor(dict_of_instructors_by_day=dict_of_instructors_by_day,
                                     instructor=instructor)
        for instructor in all_instructors
    ]

    return ", ".join(annotated_list)


def annotate_specific_instructor(dict_of_instructors_by_day: Dict[Day, List[str]], instructor: str) -> str:
    if instructor_present_for_all_days(dict_of_instructors_by_day=dict_of_instructors_by_day, instructor=instructor):
        return instructor
    list_of_days = days_present_for(dict_of_instructors_by_day=dict_of_instructors_by_day, instructor=instructor)

    return "%s (%s)" % (instructor, ", ".join(list_of_days))


def instructor_present_for_all_days(dict_of_instructors_by_day: Dict[Day, List[str]], instructor:str) -> bool:
    return all(instructor in instructors_for_day for instructors_for_day in list(dict_of_instructors_by_day.values()))


def days_present_for(dict_of_instructors_by_day: Dict[Day, List[str]], instructor:str):
    list_of_days = [day.name for day, instructors_on_day in dict_of_instructors_by_day.items()
                    if instructor in instructors_on_day]

    return list_of_days


def get_instructor_count_allocated_to_group_with_day_annotation(volunteers_in_roles_at_event: DictOfVolunteersAtEventWithDictOfDaysRolesAndGroups,
                                            group: Group,
                                                                list_of_instructor_type_roles_at_event_sorted_by_seniority: list):

    dict_of_instructors_by_day_for_group = get_dict_of_instructors_by_day_for_group(
        volunteers_in_roles_at_event=volunteers_in_roles_at_event,
        group=group
    )

    if check_all_instructors_same_across_days(dict_of_instructors_by_day_for_group):
        instructors_on_first_day =list(dict_of_instructors_by_day_for_group.values())[0]
        return len(instructors_on_first_day)
    else:
        return annotate_count_across_days(dict_of_instructors_by_day_for_group)



def get_dict_of_instructors_by_day_for_group(volunteers_in_roles_at_event: DictOfVolunteersAtEventWithDictOfDaysRolesAndGroups,
                                                                   group: Group):
    days_in_event = volunteers_in_roles_at_event.event.days_in_event()

    dict_of_instructors_by_day = {}
    for day in days_in_event:
        list_of_volunteers = volunteers_in_roles_at_event.list_of_volunteers_with_roles_and_groups_and_teams_assigned_to_group_on_day(
            day=day,
            group=group
        )
        list_of_volunteers = [volunteer_with_group.volunteer.name for volunteer_with_group in list_of_volunteers]
        list_of_volunteers.sort()
        dict_of_instructors_by_day[day] = list_of_volunteers

    return dict_of_instructors_by_day

def annotate_count_across_days(dict_of_instructors_by_day_for_group: Dict[Day, List[str]]):
    list_of_labelled_counts = [
        "%d (%s)" % (len(instructors_on_day), day.name)
        for day, instructors_on_day  in dict_of_instructors_by_day_for_group.items()
    ]

    return ", ".join(list_of_labelled_counts)

def get_list_of_instructor_type_roles_at_event_sorted_by_seniority(object_store: ObjectStore, event: Event):
    teams_and_roles = get_dict_of_teams_and_roles(object_store)
    roles_in_instructor_team = teams_and_roles.roles_in_instructor_team()

    roles_at_event =get_sorted_roles_at_event(object_store=object_store, event=event)
    sorted_list = []
    for role in roles_in_instructor_team:
        if role in roles_at_event:
            sorted_list.append(role)

    return sorted_list
