from app.data_access.sql.generic_sql_data import GenericSqlData
from app.data_access.sql.shared_column_names import *
from app.objects.club_dinghies import ListOfClubDinghyLimits, ClubDinghyWithLimitAtEvent, \
    OLD_event_id_for_generic_limit, event_id_for_generic_limit

CLUB_DINGHY_LIMIT_TABLE = "club_dinghy_limits"
INDEX_CLUB_DINGHY_LIMIT_TABLE = "index_club_dinghy_limits"


class SqlDataListOfClubDinghyLimits(GenericSqlData):
    def read(self) -> ListOfClubDinghyLimits:
        try:
            if self.table_does_not_exist(CLUB_DINGHY_LIMIT_TABLE):
                return ListOfClubDinghyLimits.create_empty()

            cursor = self.cursor
            cursor.execute('''SELECT %s, %s, %s FROM %s ''' % (

                EVENT_ID,
                DINGHY_ID,
                CLUB_DINGHY_LIMIT,
            CLUB_DINGHY_LIMIT_TABLE)

                           )
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading dinghy limits table at event" % str(e1))
        finally:
            self.close()

        new_list = [
           ClubDinghyWithLimitAtEvent(event_id=str(raw_item[0]),
                                       club_dinghy_id = str(raw_item[1]),
                                       limit=int(raw_item[2]))
            for raw_item in raw_list]

        return ListOfClubDinghyLimits(new_list)

    def write(self, list_of_boats: ListOfClubDinghyLimits):
        try:
            if self.table_does_not_exist(CLUB_DINGHY_LIMIT_TABLE):
                self.create_table()

            ## NEEDS TO DELETE OLD
            ## TEMPORARY UNTIL CAN DO PROPERLY
            self.cursor.execute(
                "DELETE FROM %s" % (CLUB_DINGHY_LIMIT_TABLE))

            for limit_for_boat_at_event in list_of_boats:
                club_dinghy_id = int(limit_for_boat_at_event.club_dinghy_id)
                limit = int(limit_for_boat_at_event.limit)
                event_id= limit_for_boat_at_event.event_id


                ## FIXME OLD DATA CAN REMOVE
                if event_id == OLD_event_id_for_generic_limit:
                    event_id = int(event_id_for_generic_limit)
                else:
                    event_id = int(event_id)

                insertion = "INSERT INTO %s (%s, %s, %s) VALUES (?, ?,?)" % (
                    CLUB_DINGHY_LIMIT_TABLE,
                EVENT_ID,
                DINGHY_ID,
                CLUB_DINGHY_LIMIT)
                self.cursor.execute(insertion,
                                    (event_id,
                                     club_dinghy_id,
                                     limit))

            self.conn.commit()
        except Exception as e1:
            raise Exception(
                "Error %s when writing to dinghy limits table event" % str(e1))
        finally:
            self.close()

    def create_table(self):

        table_creation_query = """
                            CREATE TABLE %s (
                                %s INT, 
                                %s INT,
                                %s INT
                            );
                        """ % (CLUB_DINGHY_LIMIT_TABLE,
                               EVENT_ID,
                                DINGHY_ID,
                               CLUB_DINGHY_LIMIT
                               )

        index_creation_query = "CREATE UNIQUE INDEX %s ON %s (%s,  %s)" % (
        INDEX_CLUB_DINGHY_LIMIT_TABLE,
            CLUB_DINGHY_LIMIT_TABLE,
            EVENT_ID,
            DINGHY_ID
        )

        try:
            self.cursor.execute(table_creation_query)
            self.cursor.execute(index_creation_query)
            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when creating club dinghy limits at event table" % str(e1))
        finally:
            self.close()

