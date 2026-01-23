from datetime import datetime

from app.data_access.sql.generic_sql_data import GenericSqlData, date2int, int2date
from app.data_access.sql.shared_column_names import *
from app.objects.attendance import ListOfRawAttendanceItemsForSpecificCadet, RawAttendanceItem, Attendance
from app.objects.cadets import ListOfCadets, Cadet
from app.objects.composed.attendance import  AttendanceAcrossDays, AttendanceOnDay, AttendanceAtEventAcrossCadets
from app.objects.day_selectors import Day
from app.objects.events import  Event

CADET_ATTENDANCE_TABLE = "cadet_attendance"
INDEX_CADET_ATTENDANCE_TABLE = "index_cadet_attendance"


class SqlDataAttendanceAtEventsForSpecificCadet(
    GenericSqlData
):
    def get_events_cadet_attended(self, cadet: Cadet):
        raw_list = self.read(cadet.id)
        return raw_list.list_of_event_ids()

    def delete_attendance_data_for_cadet(self, cadet: Cadet):
        try:
            if self.table_does_not_exist(CADET_ATTENDANCE_TABLE):
                return

            ## NEEDS TO DELETE OLD
            ## TEMPORARY UNTIL CAN DO PROPERLY
            self.cursor.execute("DELETE FROM %s WHERE %s='%s'" % (CADET_ATTENDANCE_TABLE, CADET_ID, int(cadet.id)))

            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing attendance" % str(e1))
        finally:
            self.close()


    def delete_attendance_data_at_event(self, event: Event):
        try:
            if self.table_does_not_exist(CADET_ATTENDANCE_TABLE):
                return

            ## NEEDS TO DELETE OLD
            ## TEMPORARY UNTIL CAN DO PROPERLY
            self.cursor.execute("DELETE FROM %s WHERE %s='%s'" % (CADET_ATTENDANCE_TABLE, EVENT_ID, int(event.id)))

            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing attendance" % str(e1))
        finally:
            self.close()

    def update_attendance_for_cadet_on_day_at_event(self, event: Event,
                                                    cadet: Cadet, day: Day,
                                                    attendance: Attendance):
        try:
            if self.table_does_not_exist(CADET_ATTENDANCE_TABLE):
                self.create_table()

            insertion = "INSERT INTO %s (%s, %s, %s, %s, %s) VALUES (?,?,?,?,?)" % (
                CADET_ATTENDANCE_TABLE,
                CADET_ID,
                EVENT_ID,
                DAY,
                ATTENDANCE_DATETIME,
                CADET_ATTENDANCE)

            self.cursor.execute(insertion, (
                int(cadet.id),
                int(event.id),
                day.name,
                date2int(datetime.now()),
                attendance.name
            ))

            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing attendance" % str(e1))
        finally:
            self.close()

    def get_attendance_at_event_for_list_of_cadets(
            self, list_of_cadets: ListOfCadets, event: Event
    ) -> AttendanceAtEventAcrossCadets:
        return AttendanceAtEventAcrossCadets(
            [
                (cadet, self.get_attendance_dict_for_cadet(cadet=cadet,
                                                           event=event)) for cadet in list_of_cadets
            ]
        )

    def get_attendance_dict_for_cadet(self, cadet: Cadet, event: Event) -> AttendanceAcrossDays:

        raw_list = self.get_raw_attendance_at_event_for_cadet(cadet_id=cadet.id, event_id=event.id)
        list_of_days = raw_list.list_of_days()
        return AttendanceAcrossDays(dict([
            (day,AttendanceOnDay.create_from_subset_of_list_of_attendance(
                list_of_attendance=raw_list,
                day=day
            )
             )
            for day in list_of_days
        ]))


    def get_raw_attendance_at_event_for_cadet(
        self, cadet_id: str, event_id: str
    ) -> ListOfRawAttendanceItemsForSpecificCadet:
        try:
            if self.table_does_not_exist(CADET_ATTENDANCE_TABLE):
                return ListOfRawAttendanceItemsForSpecificCadet.create_empty()

            cursor = self.cursor
            cursor.execute('''SELECT %s, %s, %s FROM %s WHERE %s="%s" AND %s="%s" ''' % (

                DAY,
                ATTENDANCE_DATETIME,
                CADET_ATTENDANCE,

                CADET_ATTENDANCE_TABLE,
                CADET_ID,
                int(cadet_id),
                EVENT_ID,
                int(event_id)
            ))
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading attendance" % str(e1))
        finally:
            self.close()

        new_list = [RawAttendanceItem(
            event_id=event_id,
            day=Day[str(raw_item[0])],
            datetime_marked=int2date(raw_item[1]),
            attendance=Attendance[str(raw_item[2])]
        ) for raw_item in raw_list]

        return ListOfRawAttendanceItemsForSpecificCadet(new_list)


    def read(
        self, cadet_id: str
    ) -> ListOfRawAttendanceItemsForSpecificCadet:
        try:
            if self.table_does_not_exist(CADET_ATTENDANCE_TABLE):
                return ListOfRawAttendanceItemsForSpecificCadet.create_empty()

            cursor = self.cursor
            cursor.execute('''SELECT %s, %s, %s, %s FROM %s WHERE %s="%s" ''' % (

                EVENT_ID,
                DAY,
                ATTENDANCE_DATETIME,
                CADET_ATTENDANCE,

                CADET_ATTENDANCE_TABLE,
                CADET_ID,
                int(cadet_id)
            ))
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading attendance" % str(e1))
        finally:
            self.close()

        new_list = [RawAttendanceItem(
            event_id=str(raw_item[0]),
            day=Day[str(raw_item[1])],
            datetime_marked=int2date(raw_item[2]),
            attendance=Attendance[str(raw_item[3])]
        ) for raw_item in raw_list]

        return ListOfRawAttendanceItemsForSpecificCadet(new_list)

    def write(
        self,
        list_of_attendance: ListOfRawAttendanceItemsForSpecificCadet,
        cadet_id: str,
    ):
        try:
            if self.table_does_not_exist(CADET_ATTENDANCE_TABLE):
                self.create_table()

            ## NEEDS TO DELETE OLD
            ## TEMPORARY UNTIL CAN DO PROPERLY
            self.cursor.execute("DELETE FROM %s WHERE %s='%s'" % (CADET_ATTENDANCE_TABLE, CADET_ID, int(cadet_id)))

            for attendance in list_of_attendance:

                insertion = "INSERT INTO %s (%s, %s, %s, %s, %s) VALUES (?,?,?,?,?)" % (
                    CADET_ATTENDANCE_TABLE,
                    CADET_ID,
                    EVENT_ID,
                    DAY,
                    ATTENDANCE_DATETIME,
                    CADET_ATTENDANCE)

                self.cursor.execute(insertion, (
                    int(cadet_id),
                    int(attendance.event_id),
                    attendance.day.name,
                    date2int(attendance.datetime_marked),
                    attendance.attendance.name
                    ))

            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing attendance" % str(e1))
        finally:
            self.close()

    def create_table(self):

        # name: str
        # hidden: bool
        # id: str = arg_not_passed

        table_creation_query = """
                CREATE TABLE %s (
                    %s INTEGER,
                    %s INTEGER,
                    %s STR, 
                    %s INTEGER,
                    %s STR 

                );
            """ % (CADET_ATTENDANCE_TABLE,
                   CADET_ID,
                   EVENT_ID,
                   DAY,
                   ATTENDANCE_DATETIME,
                   CADET_ATTENDANCE)

        index_creation_query = "CREATE INDEX %s ON %s (%s)" % (
       INDEX_CADET_ATTENDANCE_TABLE,
        CADET_ATTENDANCE_TABLE,
        CADET_ID)

        try:
            self.cursor.execute(table_creation_query)
            self.cursor.execute(index_creation_query)
            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when creating attendance table" % str(e1))
        finally:
            self.close()

