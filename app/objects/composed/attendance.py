import datetime
from dataclasses import dataclass
from typing import Dict

from app.objects.attendance import ListOfRawAttendanceItemsForSpecificCadet, Attendance, not_attending, registration_not_taken
from app.objects.cadets import Cadet
from app.objects.composed.cadets_at_event_with_registration_data import DictOfCadetsWithRegistrationData
from app.objects.day_selectors import Day
from app.objects.events import ListOfEvents, Event



class HistoryOfAttendanceOnDay(Dict[datetime.datetime, Attendance]):
    pass

@dataclass
class AttendanceOnDay:
    current_attendance: Attendance
    history_of_attendance: HistoryOfAttendanceOnDay

    @property
    def last_updated(self) -> datetime.datetime:
        history = self.history_of_attendance
        all_dates =  list(history.keys())
        all_dates.sort()

        return all_dates[-1]

    @classmethod
    def create_without_history(cls, attendance: Attendance):
        return cls(
            current_attendance=attendance,
            history_of_attendance=HistoryOfAttendanceOnDay([
                (datetime.datetime.now(), attendance)
            ])
        )

    @classmethod
    def create_from_subset_of_list_of_attendance(cls, list_of_attendance: ListOfRawAttendanceItemsForSpecificCadet):
        list_as_tuples = list_of_attendance.list_of_tuple_of_datetime_marked_and_attendance()
        list_as_tuples.sort(key = lambda x: x[0])
        final_item= list_as_tuples[-1]
        current_attendance = final_item[1]

        list_as_dict = dict(
            [
                (changed_date, attendance) for changed_date, attendance in list_as_tuples
            ]
        )

        return cls(
            current_attendance=current_attendance,
            history_of_attendance=HistoryOfAttendanceOnDay(list_as_dict)
        )

    def update_attendance(self, new_attendance: Attendance, datetime_marked: datetime.datetime):
        self.history_of_attendance[datetime_marked] =new_attendance
        self.current_attendance = new_attendance

class AttendanceAcrossDays(Dict[Day, AttendanceOnDay]):
    def attendance_on_day(self, day):
        return self.get(day)

    def update_attendance_on_day(self, day: Day, new_attendance: Attendance, datetime_marked: datetime.datetime):
        attendance_on_day = self.attendance_on_day(day)
        attendance_on_day.update_attendance(new_attendance=new_attendance, datetime_marked=datetime_marked)
        self[day] = attendance_on_day

class DictOfAttendanceAtEvent(Dict[Cadet, AttendanceAcrossDays]):
    def __init__(self, raw_dict: Dict[Cadet, AttendanceAcrossDays],
                 dict_of_list_of_raw_attendance: Dict[Cadet, ListOfRawAttendanceItemsForSpecificCadet],
                 event: Event
):

        super().__init__(raw_dict)
        self._dict_of_raw_attendance = dict_of_list_of_raw_attendance
        self._event = event

    @property
    def dict_of_list_of_raw_attendance(self) ->  Dict[Cadet, ListOfRawAttendanceItemsForSpecificCadet]:
        return self._dict_of_raw_attendance

    def update_attendance_for_cadet_on_day(self, cadet: Cadet, day: Day, new_attendance: Attendance):
        current_datetime = datetime.datetime.now()
        attendance_for_cadet = self.attendance_for_cadet_across_days(cadet)
        attendance_for_cadet.update_attendance_on_day(day=day, new_attendance=new_attendance,
                                                      datetime_marked=current_datetime)
        self[cadet] = attendance_for_cadet

        underlying_raw_attendance = self.dict_of_list_of_raw_attendance.get(cadet, ListOfRawAttendanceItemsForSpecificCadet([]))
        underlying_raw_attendance.add_new_attendance_for_cadet_on_day(
            day=day,
            event_id=self._event.id,
            attendance=new_attendance,
            datetime_marked=current_datetime
        )

    def attendance_for_cadet_across_days(self, cadet: Cadet) -> AttendanceAcrossDays:
        return self.get(cadet)

def compose_dict_of_attendance_at_event(dict_of_list_of_raw_attendance: Dict[Cadet, ListOfRawAttendanceItemsForSpecificCadet],
                                        list_of_events: ListOfEvents,
                                        dict_of_registration_data: DictOfCadetsWithRegistrationData,
                                        event_id: str) -> DictOfAttendanceAtEvent:

    event = list_of_events.event_with_id(event_id)
    raw_dict = create_raw_dict_of_attendance_at_event(dict_of_list_of_raw_attendance=dict_of_list_of_raw_attendance,
                                                      dict_of_registration_data=dict_of_registration_data,
                                                      event=event)

    return DictOfAttendanceAtEvent(
        raw_dict=raw_dict,
        dict_of_list_of_raw_attendance=dict_of_list_of_raw_attendance,
        event=event
    )



def create_raw_dict_of_attendance_at_event(dict_of_list_of_raw_attendance: Dict[Cadet, ListOfRawAttendanceItemsForSpecificCadet],
                                           dict_of_registration_data: DictOfCadetsWithRegistrationData,
                                           event: Event) -> Dict[Cadet, AttendanceAcrossDays]:

    all_cadets_at_event = dict_of_registration_data.list_of_active_cadets()
    raw_dict = dict(
        [
        (cadet, attendance_for_cadet_at_event(
            event=event,
            cadet=cadet,
            dict_of_registration_data=dict_of_registration_data,
            dict_of_list_of_raw_attendance=dict_of_list_of_raw_attendance
        ))
        for cadet in all_cadets_at_event
        ]
    )

    return raw_dict

def attendance_for_cadet_at_event(cadet: Cadet, event: Event,
                                  dict_of_registration_data: DictOfCadetsWithRegistrationData,
                                  dict_of_list_of_raw_attendance: Dict[Cadet, ListOfRawAttendanceItemsForSpecificCadet]) -> AttendanceAcrossDays:

    availability_dict = dict_of_registration_data.registration_data_for_cadet(cadet).availability
    list_of_raw_attendance = dict_of_list_of_raw_attendance.get(cadet,
                                                                        ListOfRawAttendanceItemsForSpecificCadet([]))
    dict_for_cadet = dict([
        (day, attendance_on_day_for_cadet_at_event(
            event=event,
            day=day,
            registered_on_day= availability_dict.available_on_day(day),
            list_of_raw_attendance=list_of_raw_attendance
        ))
        for day in event.days_in_event()
    ])

    return AttendanceAcrossDays(dict_for_cadet)

def attendance_on_day_for_cadet_at_event(event: Event,
                                         day: Day,
                                         registered_on_day: bool,
                                  list_of_raw_attendance: ListOfRawAttendanceItemsForSpecificCadet) -> AttendanceOnDay:

    subset_of_attendance = list_of_raw_attendance.subset_for_cadet_at_event_on_day(
        day=day,
        event_id=event.id
    )

    if len(subset_of_attendance)==0:
        return default_attendance_on_day_for_cadet_at_event(registered_on_day)
    else:
        return AttendanceOnDay.create_from_subset_of_list_of_attendance(
            subset_of_attendance
        )


def default_attendance_on_day_for_cadet_at_event(
                                         registered_on_day: bool,
                                  ) -> AttendanceOnDay:

    if registered_on_day:
        return AttendanceOnDay.create_without_history(registration_not_taken)
    else:
        return AttendanceOnDay.create_without_history(not_attending)