from app.data_access.sql.shared_column_names import *
from app.data_access.sql.generic_sql_data import GenericSqlData
from app.objects.day_selectors import Day
from app.objects.patrol_boats_with_volunteers_with_id import ListOfVolunteersWithIdAtEventWithPatrolBoatsId, \
    VolunteerWithIdAtEventWithPatrolBoatId, OLD_EMPTY_VOLUNTEER_ID, EMPTY_VOLUNTEER_ID

PATROL_BOATS_AND_VOLUNTEERS_TABLE = "patrol_boats_and_volunteers_table"
INDEX_PATROL_BOATS_AND_VOLUNTEERS_TABLE = "index_patrol_boats_and_volunteers_table"


class SqlDataListOfVolunteersAtEventWithPatrolBoats(
    GenericSqlData
):
    def read(self, event_id: str) -> ListOfVolunteersWithIdAtEventWithPatrolBoatsId:
        if self.table_does_not_exist(PATROL_BOATS_AND_VOLUNTEERS_TABLE):
            return ListOfVolunteersWithIdAtEventWithPatrolBoatsId.create_empty()

        try:
            cursor = self.cursor
            cursor.execute('''SELECT %s, %s, %s  FROM %s WHERE %s='%s' ''' % (

                VOLUNTEER_ID, PATROL_BOAT_ID, DAY,
                PATROL_BOATS_AND_VOLUNTEERS_TABLE,
                EVENT_ID, int(event_id)))

            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading patrol boats and volunteers at event" % str(e1))
        finally:
            self.close()

        new_list = [
            VolunteerWithIdAtEventWithPatrolBoatId(
                volunteer_id=str(raw_item[0]),
                patrol_boat_id=str(raw_item[1]),
                day=Day[raw_item[2]]
            )
            for raw_item in raw_list
        ]

        return ListOfVolunteersWithIdAtEventWithPatrolBoatsId(new_list)

    def write(
        self,
        people_and_boats: ListOfVolunteersWithIdAtEventWithPatrolBoatsId,
        event_id: str,
    ):
        try:
            if self.table_does_not_exist(PATROL_BOATS_AND_VOLUNTEERS_TABLE):
                self.create_table()

            ## NEEDS TO DELETE OLD
            ## TEMPORARY UNTIL CAN DO PROPERLY
            self.cursor.execute("DELETE FROM %s WHERE %s='%s'" % (PATROL_BOATS_AND_VOLUNTEERS_TABLE,
                                                                  EVENT_ID,
                                                                  int(event_id)))

            for volunteer_and_boat in people_and_boats:
                volunteer_id = volunteer_and_boat.volunteer_id

                ## FIXME TEMP CODE
                if volunteer_id==OLD_EMPTY_VOLUNTEER_ID:
                    volunteer_id=int(EMPTY_VOLUNTEER_ID)
                else:
                    volunteer_id = int(volunteer_id)

                day = volunteer_and_boat.day.name
                patrol_boat_id = int(volunteer_and_boat.patrol_boat_id)

                insertion = "INSERT INTO %s (%s, %s, %s, %s) VALUES (?,?,?,?)" % (
                    PATROL_BOATS_AND_VOLUNTEERS_TABLE,
                    EVENT_ID, VOLUNTEER_ID, PATROL_BOAT_ID, DAY)

                self.cursor.execute(insertion, (
                    int(event_id),
                    volunteer_id,
                patrol_boat_id,
                day))

            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing volunteers on patrol boats at event" % str(e1))
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
                    %s INTEGER,
                    %s STR
                );
            """ % (PATROL_BOATS_AND_VOLUNTEERS_TABLE,
                   EVENT_ID, VOLUNTEER_ID, PATROL_BOAT_ID, DAY)

        ## FIXME NO INDEX REMOVE ONCE ISSUE RESOLVED

        try:
            self.cursor.execute(table_creation_query)
            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when creating patrol boats at event table" % str(e1))
        finally:
            self.close()
