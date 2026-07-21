from dataclasses import dataclass
from typing import Dict, List

import numpy as np
import pandas as pd

from app.backend.cadets_at_event.cadet_availability import get_attendance_matrix_for_cadets_at_event
from app.backend.cadets_at_event.instructor_marked_attendance import get_attendance_at_event_for_list_of_cadets, \
    get_attendance_history_at_event_on_day, update_attendance_for_cadet_on_day_at_event, \
    clear_cache_attendance_at_event_for_list_of_cadets
from app.backend.groups.cadets_with_groups_at_event import get_dict_of_cadets_with_groups_at_event
from app.backend.groups.list_of_groups import get_list_of_groups
from app.backend.registration_data.cadet_registration_data import get_list_of_active_cadets_at_event
from app.data_access.store.object_store import ObjectStore
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_lines import make_long_thing_detail_box
from app.objects.abstract_objects.abstract_tables import RowInTable
from app.objects.attendance import registration_not_taken, not_attending, unknown
from app.objects.cadets import Cadet, ListOfCadets
from app.objects.composed.attendance import AttendanceAtEventAcrossCadets, AttendanceOnDay
from app.objects.composed.cadets_at_event_with_groups import DictOfCadetsWithDaysAndGroupsAtEvent
from app.objects.day_selectors import Day
from app.objects.events import Event
from app.objects.groups import Group, ListOfGroups


def get_attendance_at_event_for_all_cadets_at_event(
    object_store: ObjectStore, event: Event
) -> AttendanceAtEventAcrossCadets:
    list_of_cadets = get_list_of_active_cadets_at_event(object_store=object_store, event=event)
    return get_attendance_at_event_for_list_of_cadets(
        object_store=object_store, event=event, list_of_cadets=list_of_cadets
    )


def get_attendance_on_day_for_all_cadets_at_event(
    object_store: ObjectStore, event: Event,  day: Day
) -> Dict[Cadet, AttendanceOnDay]:
    dict_of_attendance_at_event_for_list_of_cadets = (
        get_attendance_at_event_for_all_cadets_at_event(
            object_store=object_store, event=event
        )
    )

    return get_attendance_history_at_event_on_day(
        day=day,
        dict_of_attendance_at_event_for_list_of_cadets=dict_of_attendance_at_event_for_list_of_cadets,
    )


@dataclass
class RowForCadet:
    cadet: Cadet
    group: Group
    location: str
    group_order: int
    attendance: AttendanceOnDay

    @property
    def as_row_in_table(self) -> RowInTable:
        return RowInTable([
            self.cadet_first_name,
            self.cadet_surname,
            self.group_name,
            self.current_attendance,
            self.history
        ])

    @property
    def cadet_first_name(self):
        return self.cadet.first_name

    @property
    def cadet_surname(self):
        return self.cadet.surname

    @property
    def group_name(self):
        return self.group.name


    @property
    def current_attendance(self):
        return self.attendance.current_attendance.name

    @property
    def history(self):
        history = ", ".join(self.attendance.history_of_attendance.as_list_of_str())

        return make_long_thing_detail_box(history, "Click triangle to see history")


class ListOfRowsForCadets(List[RowForCadet]):
    def sort_by(self, sort_by:str):
        if sort_by==sort_by_group:
            self.sort_by_group()
        elif sort_by==sort_by_attendance:
            self.sort_by_attendance()
        elif sort_by==sort_by_firstname:
            self.sort_by_first_name()
        elif sort_by==sort_by_surname:
            self.sort_by_surname()
        else:
            raise Exception("%s not known" % sort_by)

    def sort_by_first_name(self):
        # first name, surname
        self.sort(key=lambda x: (x.cadet_first_name, x.cadet_surname))

    def sort_by_surname(self):
        # surname, first name
        self.sort(key=lambda x: (x.cadet_surname, x.cadet_first_name))

    def sort_by_group(self):
        ## group, attendance, first name, surname
        self.sort(key=lambda x: (x.group_order, x.current_attendance, x.cadet_first_name, x.cadet_surname))

    def sort_by_attendance(self):
        ## attendance, first name, surname
        self.sort(key=lambda x: (x.current_attendance, x.cadet_first_name, x.cadet_surname))





def get_cadet_data_as_list_of_rows_for_cadets(interface: abstractInterface, event: Event,
        day: Day) -> ListOfRowsForCadets:

    mark_unknown_cadets_across_groups_as_not_attending_or_unregistered(
        interface=interface, event=event,  day=day
    )
    current_attendance = get_attendance_on_day_for_all_cadets_at_event(
        interface.object_store, event=event, day=day
    )
    dict_of_cadets_with_groups_at_event = get_dict_of_cadets_with_groups_at_event(object_store=interface.object_store,
                                                                                  event=event)

    list_of_groups = get_list_of_groups(interface.object_store)

    list_of_rows = [row_for_cadet(cadet, day=day,
                                    attendance=attendance,
                                  list_of_groups=list_of_groups,
                                     dict_of_cadets_with_groups_at_event=dict_of_cadets_with_groups_at_event)
                    for cadet, attendance in current_attendance.items()]

    return ListOfRowsForCadets(list_of_rows)

def row_for_cadet(cadet: Cadet, attendance: AttendanceOnDay,
                     day: Day,
                  list_of_groups: ListOfGroups,
                     dict_of_cadets_with_groups_at_event: DictOfCadetsWithDaysAndGroupsAtEvent)-> RowForCadet:

    group = dict_of_cadets_with_groups_at_event.days_and_groups_for_cadet(cadet).group_on_day(day)
    group_idx = list_of_groups.index(group)

    return RowForCadet(cadet=cadet, attendance=attendance, group=group, group_order=group_idx,
                       location=group.location.name)

def mark_unknown_cadets_across_groups_as_not_attending_or_unregistered(
    interface: abstractInterface, event: Event,  day: Day
):
    availability_dict = get_attendance_matrix_for_cadets_at_event(
        object_store=interface.object_store, event=event
    )
    attendance_dict = get_attendance_on_day_for_all_cadets_at_event(
        object_store=interface.object_store, event=event, day=day
    )
    list_of_cadets = ListOfCadets(list(attendance_dict.keys()))
    for cadet in list_of_cadets:
        attending = availability_dict.get(cadet).available_on_day(day)
        attendance = registration_not_taken if attending else not_attending
        current_attendance = attendance_dict.get(cadet).current_attendance

        if current_attendance == unknown:
            ## set attedance
            update_attendance_for_cadet_on_day_at_event(
                interface=interface,
                event=event,
                cadet=cadet,
                day=day,
                attendance=attendance,
            )

    #### NEEDS TO WRITE TO SQL, CLEAR THAT PART OF CACHE SO RELOADED
    clear_cache_attendance_at_event_for_list_of_cadets(
        object_store=interface.object_store, event=event, list_of_cadets=list_of_cadets
    )


sort_by_surname = "Surname"
sort_by_firstname = "First name"
sort_by_group = "Group"
sort_by_attendance = "Current attendance"


def get_summary_table_as_df(object_store: ObjectStore, sorted_list_of_rows: ListOfRowsForCadets,

                      ):

    df_groups = df_over_groups(object_store=object_store, sorted_list_of_rows=sorted_list_of_rows)
    blank_row = pd.DataFrame(np.array([['']*len(df_groups.columns)]), columns=df_groups.columns, index=[''])
    sum_original_df = pd.DataFrame(np.array([list(df_groups.sum(axis=0).values)]), columns=df_groups.columns, index=['TOTAL'])

    location_df = summary_of_attendance_over_all_locations(sorted_list_of_rows)

    df = pd.concat([df_groups, blank_row, location_df, blank_row, sum_original_df], axis=0)

    return df

from app.backend.groups.list_of_groups import order_list_of_groups

def df_over_groups(object_store: ObjectStore, sorted_list_of_rows: ListOfRowsForCadets):
    all_groups = ListOfGroups(list(set([row.group for row in sorted_list_of_rows])))
    all_groups = order_list_of_groups(object_store=object_store, list_of_groups=all_groups)
    all_group_names = all_groups.list_of_names()
    all_current_attendance= list(set([row.current_attendance for row in sorted_list_of_rows]))

    df = pd.DataFrame(

                 [
                     counts_over_groups(
                         sorted_list_of_rows=sorted_list_of_rows,
                         group_name=group_name,
                         all_current_attendance=all_current_attendance
                     )  for group_name in all_group_names
                 ]
             )
    df.index = all_group_names

    return df

def counts_over_groups(sorted_list_of_rows: ListOfRowsForCadets, group_name: str, all_current_attendance: List[str]):
    return dict(
        [(current_attendance, count_of_status_and_group_order(
            sorted_list_of_rows=sorted_list_of_rows,
            group_name=group_name,
            current_attendance=current_attendance
        )) for current_attendance in all_current_attendance]
    )

def count_of_status_and_group_order(sorted_list_of_rows: ListOfRowsForCadets,
                                    group_name: str,
                                    current_attendance: str

                                    ):
    return sum([1 for row in sorted_list_of_rows if row.group_name==group_name
                and row.current_attendance==current_attendance])

def summary_of_attendance_over_all_locations(sorted_list_of_rows: ListOfRowsForCadets) -> pd.DataFrame:
    all_current_attendance= list(set([row.current_attendance for row in sorted_list_of_rows]))
    all_locations = list(set([row.location for row in sorted_list_of_rows]))

    location_df = pd.DataFrame(

                 [
                     summary_of_attendance_over_location(
                         sorted_list_of_rows=sorted_list_of_rows,
                         location=location,
                         all_current_attendance=all_current_attendance
                     )  for location in all_locations
                 ]
             )
    location_df.index = all_locations

    return location_df

def summary_of_attendance_over_location(sorted_list_of_rows: ListOfRowsForCadets, location:str,
                                        all_current_attendance: List[str]) -> Dict[str, int]:
    return dict([
        (current_attendance, count_of_attendance_at_location(sorted_list_of_rows, location=location,
                                                   current_attendance=current_attendance))
        for current_attendance in all_current_attendance
    ])

def count_of_attendance_at_location(sorted_list_of_rows: ListOfRowsForCadets, location:str,
                                    current_attendance: str
                                    ) -> int:
    return sum([1 for row in sorted_list_of_rows if row.location==location and row.current_attendance==current_attendance])
