from dataclasses import dataclass
from typing import Dict, List

from app.backend.groups.list_of_groups import get_list_of_groups
from app.backend.reporting.options_and_parameters.report_type_specific_parameters import (
    SpecificParametersForTypeOfReport, GroupAnnotations,
)
from app.backend.rota.volunteer_summary_of_instructors import \
    get_list_of_instructor_type_roles_at_event_sorted_by_seniority, get_list_of_instructors_on_day_for_specific_role_in_group
from app.backend.volunteers.volunteers_at_event import get_dict_of_all_event_data_for_volunteers
from app.data_access.store.object_store import ObjectStore
from app.objects.composed.volunteer_roles import RoleWithSkills
from app.objects.composed.volunteer_with_group_and_role_at_event import \
    DEPRECATED_DictOfVolunteersAtEventWithDictOfDaysRolesAndGroups
from app.objects.day_selectors import Day
from app.objects.events import Event
from app.objects.groups import unallocated_group, Group, ListOfGroups
from app.objects.utilities.exceptions import arg_not_passed

FIRST_CADET = "First cadet"
SECOND_CADET = "Second cadet"
GROUP = "Group"
BOAT_CLASS = "Boat class"
SAIL_NUMBER = "Sail number"



def get_specific_parameters_for_boat_report(
    object_store: ObjectStore,
        event: Event = arg_not_passed
) -> SpecificParametersForTypeOfReport:

    list_of_groups = get_list_of_groups(object_store)  ## will be ordered
    list_of_groups.add_unallocated()
    if event is arg_not_passed:
        group_annotations = arg_not_passed
    else:
        group_annotations = get_dict_of_group_annotations(object_store=object_store, event=event, list_of_groups=list_of_groups)

    specific_parameters_for_boat_report = SpecificParametersForTypeOfReport(
        #    entry_columns=[FIRST_CADET, SECOND_CADET, GROUP, BOAT_CLASS, SAIL_NUMBER, CLUB_BOAT],
        group_by_column=GROUP,
        report_type="Sailors with boats report",
        group_order=list_of_groups.list_of_names(),
        unallocated_group=unallocated_group.name,
        group_annotations=group_annotations
    )

    return specific_parameters_for_boat_report

def get_dict_of_group_annotations(object_store: ObjectStore, event: Event, list_of_groups: ListOfGroups) -> GroupAnnotations:
    list_of_roles =  (
        get_list_of_instructor_type_roles_at_event_sorted_by_seniority(
            object_store, event
        )
    )
    volunteer_event_data = get_dict_of_all_event_data_for_volunteers(
        object_store=object_store, event=event
    )
    volunteers_in_roles_at_event = (
        volunteer_event_data.dict_of_volunteers_at_event_with_days_and_roles
    )

    dict_over_days = dict(
        [
            (day.name, get_dict_of_group_annotations_on_day(
                day=day,
                volunteers_in_roles_at_event=volunteers_in_roles_at_event,
                list_of_roles=list_of_roles,
                list_of_groups=list_of_groups
            ))
            for day in event.days_in_event()
        ]
    )

    return GroupAnnotations(dict_over_days)

def get_dict_of_group_annotations_on_day(day: Day, list_of_roles: List[RoleWithSkills],
                                         volunteers_in_roles_at_event: DEPRECATED_DictOfVolunteersAtEventWithDictOfDaysRolesAndGroups,
                                         list_of_groups: ListOfGroups) -> Dict[str,str]:

    dict_of_group_annotations = dict(
        [
            (group.name,
            get_annotation_for_group(
                day=day,
                 group=group,
                list_of_roles=list_of_roles,
                volunteers_in_roles_at_event=volunteers_in_roles_at_event
            ))

            for group in list_of_groups
        ]
    )

    return dict_of_group_annotations



def get_annotation_for_group(day: Day, group: Group, list_of_roles: List[RoleWithSkills],
    volunteers_in_roles_at_event: DEPRECATED_DictOfVolunteersAtEventWithDictOfDaysRolesAndGroups
                             ) -> str:
    instructors = get_instructors_at_event_for_group( day=day, group=group,
                                                     list_of_roles=list_of_roles,
                                                     volunteers_in_roles_at_event=volunteers_in_roles_at_event)
    streamer = group.streamer

    return "- ".join([streamer, instructors])


def get_instructors_at_event_for_group(day: Day,
                                       group: Group,
                                       volunteers_in_roles_at_event: DEPRECATED_DictOfVolunteersAtEventWithDictOfDaysRolesAndGroups,
                                       list_of_roles: List[RoleWithSkills]) ->str:
    instructors = []
    for role in list_of_roles:
        instructors+=\
        get_list_of_instructors_on_day_for_specific_role_in_group(
            volunteers_in_roles_at_event=volunteers_in_roles_at_event,
            role=role,
            group=group,
            day=day
        )


    return ", ".join(instructors)



@dataclass
class AdditionalParametersForBoatReport:
    display_full_names: bool
    exclude_lake_groups: bool
    exclude_river_training_groups: bool
    exclude_unallocated_groups: bool
    in_out_columns: bool
