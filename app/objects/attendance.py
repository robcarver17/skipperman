import datetime
from dataclasses import dataclass
from enum import Enum

from app.objects.day_selectors import Day
from app.objects.utilities.generic_objects import GenericSkipperManObject
from app.objects.utilities.generic_list_of_objects import (
    GenericListOfObjects,
    get_subset_of_list_that_matches_multiple_attr,
)
from app.objects.utilities.transform_data import transform_datetime_into_str

Attendance = Enum(
    "Attendance",
    [
        "Not attending today",
        "Attending, register not yet taken",
        "Present",
        "Absent",
        "Temporary absence",
        "Will be late",
        "Late and arrived",
        "Returned to parent or club",
        "Unknown",
    ],
)

unknown = Attendance["Unknown"]
not_attending = Attendance["Not attending today"]
registration_not_taken = Attendance["Attending, register not yet taken"]
present = Attendance["Present"]
absent = Attendance["Absent"]
will_be_late = Attendance["Will be late"]
returned = Attendance["Returned to parent or club"]
temporary_absence = Attendance["Temporary absence"]


transition_matrix = {
    not_attending: [not_attending, registration_not_taken, present],
    registration_not_taken: [present, absent, will_be_late],
    will_be_late: [present, absent],
    present: [returned, temporary_absence],
    temporary_absence: [present, returned],
    returned: [],
}


@dataclass
class RawAttendanceItem(GenericSkipperManObject):
    event_id: str
    day: Day
    datetime_marked: datetime.datetime
    attendance: Attendance

    def as_str_dict(self) -> dict:
        return dict(
            event_id=self.event_id,
            day=self.day.name,
            attendance=self.attendance.name,
            datetime_marked=transform_datetime_into_str(self.datetime_marked),
        )


class ListOfRawAttendanceItemsForSpecificCadet(GenericListOfObjects):
    @property
    def _object_class_contained(self):
        return RawAttendanceItem

    def list_of_tuple_of_datetime_marked_and_attendance(self):
        return [(item.datetime_marked, item.attendance) for item in self]

    def subset_for_cadet_at_event_on_day(self, event_id: str, day: Day):
        subset = get_subset_of_list_that_matches_multiple_attr(
            self, dict_of_attributes={"day": day, "event_id": event_id}
        )

        return ListOfRawAttendanceItemsForSpecificCadet(subset)

    def add_new_attendance_for_cadet_on_day(
        self,
        event_id: str,
        datetime_marked: datetime.datetime,
        day: Day,
        attendance: Attendance,
    ):
        self.append(
            RawAttendanceItem(
                event_id=event_id,
                day=day,
                attendance=attendance,
                datetime_marked=datetime_marked,
            )
        )
