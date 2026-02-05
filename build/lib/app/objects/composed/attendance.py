import datetime
from dataclasses import dataclass
from typing import Dict
from app.objects.attendance import (
    ListOfRawAttendanceItemsForSpecificCadet,
    Attendance,
    unknown,
)
from app.objects.cadets import Cadet, ListOfCadets
from app.objects.day_selectors import Day
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

