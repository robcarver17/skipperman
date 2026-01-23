import datetime
from dataclasses import dataclass
from typing import Dict, List

from app.data_access.configuration.configuration import local_timezone
from app.objects.attendance import (
    ListOfRawAttendanceItemsForSpecificCadet,
    Attendance,
    unknown,
    not_attending,
    registration_not_taken,
    absent,
)
from app.objects.cadets import Cadet, ListOfCadets
from app.objects.day_selectors import Day, DaySelector
from app.objects.events import ListOfEvents, Event
from app.objects.utilities.exceptions import arg_not_passed


class HistoryOfAttendanceOnDay(Dict[datetime.datetime, Attendance]):
    def update_attendance(
        self, new_attendance: Attendance, datetime_marked: datetime.datetime
    ):
        if new_attendance is unknown:
            return

        self[datetime_marked] = new_attendance

    def as_list_of_str(self):
        sorted_by_date = dict(
            sorted(self.items(), key=lambda item: item[0], reverse=True)
        )
        return [
            "%s (%s)" % (attendance.name, datetime_marked.strftime("%d/%m %H:%M"))
            for datetime_marked, attendance in sorted_by_date.items()
        ]


@dataclass
class AttendanceOnDay:
    current_attendance: Attendance
    history_of_attendance: HistoryOfAttendanceOnDay

    @property
    def last_updated(self) -> datetime.datetime:
        history = self.history_of_attendance
        all_dates = list(history.keys())
        all_dates.sort()

        return all_dates[-1]

    @classmethod
    def create_without_history(cls):
        return cls(
            current_attendance=unknown,
            history_of_attendance=HistoryOfAttendanceOnDay([]),
        )

    @classmethod
    def create_from_subset_of_list_of_attendance(
        cls, list_of_attendance: ListOfRawAttendanceItemsForSpecificCadet,
            day: Day
    ):
        list_as_tuples = (
            list_of_attendance.list_of_tuple_of_datetime_marked_and_attendance_on_day(day)
        )
        list_as_tuples.sort(key=lambda x: x[0])
        final_item = list_as_tuples[-1]
        current_attendance = final_item[1]

        list_as_dict = dict(
            [(changed_date, attendance) for changed_date, attendance in list_as_tuples]
        )

        return cls(
            current_attendance=current_attendance,
            history_of_attendance=HistoryOfAttendanceOnDay(list_as_dict),
        )

    def update_attendance(
        self, new_attendance: Attendance, datetime_marked: datetime.datetime
    ):
        self.history_of_attendance.update_attendance(new_attendance, datetime_marked)
        self.current_attendance = new_attendance



class AttendanceAcrossDays(Dict[Day, AttendanceOnDay]):
    def attendance_on_day(self, day):
        return self.get(day, AttendanceOnDay.create_without_history())

    def update_attendance_on_day(
        self, day: Day, new_attendance: Attendance, datetime_marked: datetime.datetime = arg_not_passed
    ):
        if datetime_marked is arg_not_passed:
            datetime_marked = datetime.datetime.now(
                
            )
        attendance_on_day = self.attendance_on_day(day)
        attendance_on_day.update_attendance(
            new_attendance=new_attendance, datetime_marked=datetime_marked
        )
        self[day] = attendance_on_day

class AttendanceAtEventAcrossCadets(Dict[Cadet, AttendanceAcrossDays]):
    def attendance_for_cadet(self, cadet: Cadet):
        return self.get(cadet, AttendanceAcrossDays())

    def list_of_cadets(self) -> ListOfCadets:
        return ListOfCadets(list(self.keys()))

class AttendanceAcrossDaysAndEvents(Dict[Event, AttendanceAcrossDays]):
    def clean_attendance_data_for_event(self, event: Event):
        self.pop(event)

    def update_attendance_for_cadet_on_day_at_event(
        self,
        event: Event,
        day: Day,
        new_attendance: Attendance,
        datetime_marked: datetime.datetime,
    ):
        attendance_for_cadet_at_event = self.attendance_for_cadet_at_event(event)
        attendance_for_cadet_at_event.update_attendance_on_day(
            day=day, new_attendance=new_attendance, datetime_marked=datetime_marked
        )
        self[event] = attendance_for_cadet_at_event

    def attendance_for_cadet_at_event(self, event: Event) -> AttendanceAcrossDays:
        return self.get(event, AttendanceAcrossDays())

    @property
    def list_of_events(self):
        return list(self.keys())


class DictOfAttendanceAcrossEvents(Dict[Cadet, AttendanceAcrossDaysAndEvents]):
    def clean_attendance_data_for_event(self, event: Event):
        for cadet in self.list_of_cadets:
            attendance = self.attendance_for_cadet_across_days_and_events(cadet)
            attendance.clean_attendance_data_for_event(event)

            underlying_raw_attendance = self.dict_of_list_of_raw_attendance.get(
                cadet.id, ListOfRawAttendanceItemsForSpecificCadet([])
            )
            underlying_raw_attendance.clean_attendance_data_for_event(event.id)
            self._dict_of_raw_attendance[cadet.id] = underlying_raw_attendance

    def mark_unknown_cadets_as_not_attending_or_unregistered(
        self, day: Day, event: Event, availability_dict: Dict[Cadet, DaySelector]
    ):
        for cadet in self.list_of_cadets:
            attending = availability_dict.get(cadet).available_on_day(day)
            attendance = registration_not_taken if attending else not_attending
            current_attendance = (
                self.attendance_for_cadet_across_days_and_events(cadet)
                .attendance_for_cadet_at_event(event)
                .attendance_on_day(day)
                .current_attendance
            )
            if current_attendance == unknown:
                self.update_attendance_for_cadet_on_day_at_event(
                    event=event,
                    day=day,
                    cadet=cadet,
                    new_attendance=attendance,
                )

    def mark_all_unregistered_cadets_as_absent(self, day: Day, event: Event):
        for cadet in self.list_of_cadets:
            current_attendance = (
                self.attendance_for_cadet_across_days_and_events(cadet)
                .attendance_for_cadet_at_event(event)
                .attendance_on_day(day)
                .current_attendance
            )
            if (
                current_attendance == unknown
                or current_attendance == registration_not_taken
            ):
                self.update_attendance_for_cadet_on_day_at_event(
                    event=event, day=day, cadet=cadet, new_attendance=absent
                )

    def attendance_for_cadet_across_days_and_events(
        self, cadet: Cadet
    ) -> AttendanceAcrossDaysAndEvents:
        return self.get(cadet, AttendanceAcrossDaysAndEvents())

    def update_attendance_for_cadet_on_day_at_event(
        self, event: Event, cadet: Cadet, day: Day, new_attendance: Attendance
    ):
        current_datetime = datetime.datetime.now(local_timezone)
        attendance_for_cadet = self.attendance_for_cadet_across_days_and_events(cadet)
        current_attendance = (
            attendance_for_cadet.attendance_for_cadet_at_event(event)
            .attendance_on_day(day)
            .current_attendance
        )
        if current_attendance == new_attendance:
            return

        attendance_for_cadet.update_attendance_for_cadet_on_day_at_event(
            event=event,
            day=day,
            new_attendance=new_attendance,
            datetime_marked=current_datetime,
        )
        self[cadet] = attendance_for_cadet

        underlying_raw_attendance = self.dict_of_list_of_raw_attendance.get(
            cadet.id, ListOfRawAttendanceItemsForSpecificCadet([])
        )
        underlying_raw_attendance.add_new_attendance_for_cadet_on_day(
            day=day,
            event_id=event.id,
            attendance=new_attendance,
            datetime_marked=current_datetime,
        )
        self._dict_of_raw_attendance[cadet.id] = underlying_raw_attendance

    @property
    def list_of_cadets(self) -> ListOfCadets:
        return ListOfCadets(list(self.keys()))
