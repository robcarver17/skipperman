from app.data_access.sql.generic_sql_data import GenericSqlData
from app.data_access.sql.shared_column_names import *
from app.objects.day_selectors import DaySelector
from app.objects.volunteer_at_event_with_id import ListOfVolunteersAtEventWithId, VolunteerAtEventWithId

VOLUNTEERS_AT_EVENT_TABLE="volunteers_at_event"
INDEX_VOLUNTEERS_AT_EVENT_TABLE="index_volunteers_at_event"


class SqlDataListOfVolunteersAtEvent(GenericSqlData):
    def read(self, event_id: str) -> ListOfVolunteersAtEventWithId:
        try:
            if self.table_does_not_exist(VOLUNTEERS_AT_EVENT_TABLE):
                return ListOfVolunteersAtEventWithId.create_empty()

            cursor = self.cursor
            cursor.execute('''SELECT %s, %s, %s, %s, %s, %s, %s FROM %s WHERE %s='%s' ''' % (
                VOLUNTEER_ID,
                VOLUNTEER_AVAILABLITY,
                PREFERRED_DUTIES,
                SAME_OR_DIFFERENT_DUTIES,
                VOLUNTEER_ANY_OTHER_INFORMATION,
                VOLUNTEER_STATUS,
                VOLUNTEER_NOTES,
            VOLUNTEERS_AT_EVENT_TABLE,

            EVENT_ID, int(event_id)
            ))
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading volunteers at event" % str(e1))
        finally:
            self.close()

        new_list = [
            VolunteerAtEventWithId(
                volunteer_id=str(raw_item[0]),
                availablity=DaySelector.from_str(raw_item[1]),
                preferred_duties=str(raw_item[2]),
                same_or_different=str(raw_item[3]),
                any_other_information=str(raw_item[4]),
                self_declared_status=str(raw_item[5]),
                notes=str(raw_item[6]),
                list_of_associated_cadet_id=[]
            )
            for raw_item in raw_list]

        return ListOfVolunteersAtEventWithId(new_list)

    def write(
        self, list_of_volunteers_at_event: ListOfVolunteersAtEventWithId, event_id: str
    ):
        try:
            if self.table_does_not_exist(VOLUNTEERS_AT_EVENT_TABLE):
                self.create_table()

            ## NEEDS TO DELETE OLD
            ## TEMPORARY UNTIL CAN DO PROPERLY
            self.cursor.execute("DELETE FROM %s WHERE %s='%s'" % (VOLUNTEERS_AT_EVENT_TABLE, EVENT_ID, event_id))

            for volunteer_at_event in list_of_volunteers_at_event:
                volunteer_id = int(volunteer_at_event.volunteer_id)
                availability = volunteer_at_event.availablity.as_str()
                preferred_duties = str(volunteer_at_event.preferred_duties)
                same_or_different = str(volunteer_at_event.same_or_different)
                any_other_information = str(volunteer_at_event.any_other_information)
                self_declared_status = str(volunteer_at_event.self_declared_status)
                notes = str(volunteer_at_event.notes)

                insertion = "INSERT INTO %s (%s, %s, %s, %s, %s, %s, %s, %s) VALUES (?, ?,?,?, ?,?,?,?)" % (
                    VOLUNTEERS_AT_EVENT_TABLE,
                    EVENT_ID,
                    VOLUNTEER_ID,
                VOLUNTEER_AVAILABLITY,
                PREFERRED_DUTIES,
                SAME_OR_DIFFERENT_DUTIES,
                VOLUNTEER_ANY_OTHER_INFORMATION,
                VOLUNTEER_STATUS,
                VOLUNTEER_NOTES)
                self.cursor.execute(insertion,
                                    (int(event_id),
                                     volunteer_id,
                                     availability,
                                     preferred_duties,
                                     same_or_different,
                                     any_other_information,
                                     self_declared_status,
                                     notes))

            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing to volunteers at event table event# %s" % (str(e1), event_id))
        finally:
            self.close()

    def create_table(self):

        table_creation_query = """
                        CREATE TABLE %s (
                            %s INT, 
                            %s INT, 
                            %s STR,
                            %s STR,
                            %s STR,
                            %s STR,
                            %s STR,
                            %s STR
                        );
                    """ % (VOLUNTEERS_AT_EVENT_TABLE,
                           EVENT_ID,
                           VOLUNTEER_ID,
                           VOLUNTEER_AVAILABLITY,
                           PREFERRED_DUTIES,
                           SAME_OR_DIFFERENT_DUTIES,
                           VOLUNTEER_ANY_OTHER_INFORMATION,
                           VOLUNTEER_STATUS,
                           VOLUNTEER_NOTES
                           )

        index_creation_query = "CREATE UNIQUE INDEX %s ON %s (%s,  %s)" % (
            INDEX_VOLUNTEERS_AT_EVENT_TABLE,
        VOLUNTEERS_AT_EVENT_TABLE,
        EVENT_ID,
        VOLUNTEER_ID)

        try:
            self.cursor.execute(table_creation_query)
            self.cursor.execute(index_creation_query)
            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when creating volunteers at event table" % str(e1))
        finally:
            self.close()


