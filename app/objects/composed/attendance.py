import datetime
from dataclasses import dataclass
from typing import Dict, List

from app.objects.attendance import ListOfRawAttendanceItemsForSpecificCadet, Attendance, unknown, not_attending, registration_not_taken, absent
from app.objects.cadets import Cadet, ListOfCadets
from app.objects.day_selectors import Day, DaySelector
from app.objects.events import ListOfEvents, Event



class HistoryOfAttendanceOnDay(Dict[datetime.datetime, Attendance]):
    def update_attendance(self, new_attendance: Attendance, datetime_marked: datetime.datetime):
        if new_attendance is unknown:
            return

        self[datetime_marked] = new_attendance

    def as_list_of_str(self):
        sorted_by_date = dict(sorted(self.items(), key=lambda item: item[0], reverse=True))
        return [
            "%s (%s)" % (attendance.name,
                         datetime_marked.strftime("%d/%m %H:%M")) for datetime_marked, attendance in sorted_by_date.items()
        ]

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
    def create_without_history(cls):
        return cls(
            current_attendance=unknown,
            history_of_attendance=HistoryOfAttendanceOnDay([
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
        self.history_of_attendance.update_attendance(new_attendance, datetime_marked)
        self.current_attendance = new_attendance

class AttendanceAcrossDays(Dict[Day, AttendanceOnDay]):
    def attendance_on_day(self, day):
        return self.get(day)

    def update_attendance_on_day(self, day: Day, new_attendance: Attendance, datetime_marked: datetime.datetime):
        attendance_on_day = self.attendance_on_day(day)
        attendance_on_day.update_attendance(new_attendance=new_attendance, datetime_marked=datetime_marked)
        self[day] = attendance_on_day

class AttendanceAcrossDaysAndEvents(Dict[Event, AttendanceAcrossDays]):
    def update_attendance_for_cadet_on_day_at_event(self, event: Event, day: Day, new_attendance: Attendance, datetime_marked: datetime.datetime):
        attendance_for_cadet_at_event = self.attendance_for_cadet_at_event(event)
        attendance_for_cadet_at_event.update_attendance_on_day(day=day, new_attendance=new_attendance,
                                                      datetime_marked=datetime_marked)
        self[event] = attendance_for_cadet_at_event


    def attendance_for_cadet_at_event(self, event: Event) -> AttendanceAcrossDays:
        return self.get(event, AttendanceAcrossDays())


class DictOfAttendanceAcrossEvents(Dict[Cadet, AttendanceAcrossDaysAndEvents]):
    def __init__(self, raw_dict: Dict[Cadet, AttendanceAcrossDaysAndEvents],
                 dict_of_list_of_raw_attendance: Dict[str, ListOfRawAttendanceItemsForSpecificCadet],
):

        super().__init__(raw_dict)
        self._dict_of_raw_attendance = dict_of_list_of_raw_attendance

    def mark_unknown_cadets_as_not_attending_or_unregistered(self, day: Day,
                                                             event: Event,
                                                             availability_dict: Dict[Cadet, DaySelector]
                                                             ):

        for cadet in self.list_of_cadets:
            attending = availability_dict.get(cadet).available_on_day(day)
            attendance = registration_not_taken if attending else not_attending
            current_attendance = self.attendance_for_cadet_across_days_and_events(cadet).attendance_for_cadet_at_event(event).attendance_on_day(day).current_attendance
            if current_attendance == unknown:
                self.update_attendance_for_cadet_on_day_at_event(event=event,
                                                                 day=day,
                                                                 cadet=cadet,
                                                                 new_attendance=attendance,

                                                                 )


    def mark_all_unregistered_cadets_as_absent(self, day: Day,
                                               event: Event):
        for cadet in self.list_of_cadets:
            current_attendance = self.attendance_for_cadet_across_days_and_events(cadet).attendance_for_cadet_at_event(event).attendance_on_day(day).current_attendance
            if current_attendance==unknown or current_attendance == registration_not_taken:
                self.update_attendance_for_cadet_on_day_at_event(event=event,
                                                                 day=day,
                                                                 cadet=cadet,
                                                                 new_attendance=absent
                                                                 )


    def attendance_for_cadet_across_days_and_events(self, cadet: Cadet) -> AttendanceAcrossDaysAndEvents:
        return self.get(cadet, AttendanceAcrossDaysAndEvents())

    def update_attendance_for_cadet_on_day_at_event(self, event: Event, cadet: Cadet, day: Day, new_attendance: Attendance):
        current_datetime = datetime.datetime.now()
        attendance_for_cadet = self.attendance_for_cadet_across_days_and_events(cadet)
        current_attendance = attendance_for_cadet.attendance_for_cadet_at_event(event).attendance_on_day(day).current_attendance
        if current_attendance==new_attendance:
            return

        attendance_for_cadet.update_attendance_for_cadet_on_day_at_event(
                                                event=event, day=day, new_attendance=new_attendance,
                                                      datetime_marked=current_datetime)
        self[cadet] = attendance_for_cadet

        underlying_raw_attendance = self.dict_of_list_of_raw_attendance.get(cadet.id, ListOfRawAttendanceItemsForSpecificCadet([]))
        underlying_raw_attendance.add_new_attendance_for_cadet_on_day(
            day=day,
            event_id=event.id,
            attendance=new_attendance,
            datetime_marked=current_datetime
        )
        self._dict_of_raw_attendance[cadet.id] = underlying_raw_attendance

    @property
    def dict_of_list_of_raw_attendance(self) ->  Dict[str, ListOfRawAttendanceItemsForSpecificCadet]:
        return self._dict_of_raw_attendance

    @property
    def list_of_cadets(self) -> ListOfCadets:
        return ListOfCadets(list(self.keys()))


def compose_dict_of_attendance_across_events(list_of_cadet_ids: List[str],
                                           dict_of_list_of_raw_attendance: Dict[str, ListOfRawAttendanceItemsForSpecificCadet],
                                            list_of_events: ListOfEvents,
                                           list_of_cadets: ListOfCadets,
                            ) -> DictOfAttendanceAcrossEvents:

    list_of_cadets = ListOfCadets([list_of_cadets.cadet_with_id(cadet_id) for cadet_id in list_of_cadet_ids])
    raw_dict = create_raw_dict_of_attendance_at_events(dict_of_list_of_raw_attendance=dict_of_list_of_raw_attendance,
                                                      list_of_cadets=list_of_cadets,
                                                       list_of_events=list_of_events
                                                      )

    return DictOfAttendanceAcrossEvents(
        raw_dict=raw_dict,
        dict_of_list_of_raw_attendance=dict_of_list_of_raw_attendance,
    )



def create_raw_dict_of_attendance_at_events(
                                           dict_of_list_of_raw_attendance: Dict[str, ListOfRawAttendanceItemsForSpecificCadet],
                                            list_of_events: ListOfEvents,
                                           list_of_cadets: ListOfCadets) -> Dict[Cadet, AttendanceAcrossDaysAndEvents]:

    raw_dict = dict(
        [
        (cadet, attendance_for_cadet_across_events(
            cadet=cadet,
            list_of_events = list_of_events,
            dict_of_list_of_raw_attendance=dict_of_list_of_raw_attendance,
            )
         )
        for cadet in list_of_cadets
        ]
    )

    return raw_dict


def attendance_for_cadet_across_events(cadet: Cadet,
                                       list_of_events: ListOfEvents,
                                       dict_of_list_of_raw_attendance: Dict[str, ListOfRawAttendanceItemsForSpecificCadet]) -> AttendanceAcrossDaysAndEvents:
    raw_dict = dict(
        [
        (event, attendance_for_cadet_at_event(
            cadet=cadet,
            event=event,
            dict_of_list_of_raw_attendance=dict_of_list_of_raw_attendance
        )
         )
        for event in list_of_events
        ]
    )

    return AttendanceAcrossDaysAndEvents(raw_dict)

def attendance_for_cadet_at_event(cadet: Cadet, event: Event,
                                  dict_of_list_of_raw_attendance: Dict[str, ListOfRawAttendanceItemsForSpecificCadet]) -> AttendanceAcrossDays:

    list_of_raw_attendance = dict_of_list_of_raw_attendance.get(cadet.id,
                                                                        ListOfRawAttendanceItemsForSpecificCadet([]))
    dict_for_cadet = dict([
        (day, attendance_on_day_for_cadet_at_event(
            event=event,
            day=day,
            list_of_raw_attendance=list_of_raw_attendance
        ))
        for day in event.days_in_event()
    ])

    return AttendanceAcrossDays(dict_for_cadet)

def attendance_on_day_for_cadet_at_event(event: Event,
                                         day: Day,
                                  list_of_raw_attendance: ListOfRawAttendanceItemsForSpecificCadet) -> AttendanceOnDay:

    subset_of_attendance = list_of_raw_attendance.subset_for_cadet_at_event_on_day(
        day=day,
        event_id=event.id
    )

    if len(subset_of_attendance)==0:
        return AttendanceOnDay.create_without_history()
    else:
        return AttendanceOnDay.create_from_subset_of_list_of_attendance(
            subset_of_attendance
        )


