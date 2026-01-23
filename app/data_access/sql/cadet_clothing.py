from app.data_access.sql.generic_sql_data import GenericSqlData
from app.objects.clothing import ListOfCadetsWithClothingAndIdsAtEvent, CadetWithClothingAndIdsAtEvent
from app.data_access.sql.shared_column_names import *

CADET_WITH_CLOTHING_AT_EVENT_TABLE = "cadet_with_clothing_at_event"
INDEX_CADET_WITH_CLOTHING_AT_EVENT_TABLE = "index_cadet_with_clothing_at_event"


class SqlDataListOfCadetsWithClothingAtEvent(
    GenericSqlData
):
    def read(self, event_id: str) -> ListOfCadetsWithClothingAndIdsAtEvent:
        try:
            if self.table_does_not_exist(CADET_WITH_CLOTHING_AT_EVENT_TABLE):
                return ListOfCadetsWithClothingAndIdsAtEvent.create_empty()

            cursor = self.cursor
            cursor.execute('''SELECT %s, %s, %s FROM %s WHERE %s='%s' ''' % (
                CADET_ID, CADET_CLOTHING_SIZE, CADET_CLOTHING_COLOUR,
                CADET_WITH_CLOTHING_AT_EVENT_TABLE,
                EVENT_ID, int(event_id)
            ))
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading cadet clothing at event" % str(e1))
        finally:
            self.close()

        new_list = [
            CadetWithClothingAndIdsAtEvent(cadet_id=str(raw_item[0]), size=str(raw_item[1]),
                                           colour=str(raw_item[2]))
            for raw_item in raw_list]

        return ListOfCadetsWithClothingAndIdsAtEvent(new_list)


    def write(
        self,
        list_of_cadets_with_clothing: ListOfCadetsWithClothingAndIdsAtEvent,
        event_id: str,
    ):
        try:
            if self.table_does_not_exist(CADET_WITH_CLOTHING_AT_EVENT_TABLE):
                self.create_table()

            ## NEEDS TO DELETE OLD
            ## TEMPORARY UNTIL CAN DO PROPERLY
            self.cursor.execute("DELETE FROM %s WHERE %s='%s'" % (CADET_WITH_CLOTHING_AT_EVENT_TABLE, EVENT_ID, event_id))

            for cadet_with_clothing in list_of_cadets_with_clothing:
                cadet_id = int(cadet_with_clothing.cadet_id)
                size = str(cadet_with_clothing.size)
                colour = str(cadet_with_clothing.colour)

                insertion = "INSERT INTO %s (%s, %s, %s, %s) VALUES (?, ?,?, ?)" % (
                    CADET_WITH_CLOTHING_AT_EVENT_TABLE,
                    EVENT_ID,
                    CADET_ID,
                    CADET_CLOTHING_SIZE,
                    CADET_CLOTHING_COLOUR)
                self.cursor.execute(insertion,
                                    (int(event_id), cadet_id, size, colour))

            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing to cadet clothing table event# %s" % (str(e1), event_id))
        finally:
            self.close()

    def create_table(self):

        table_creation_query = """
                        CREATE TABLE %s (
                            %s INT, 
                            %s INT, 
                            %s STR,
                            %s STR
                        );
                    """ % (CADET_WITH_CLOTHING_AT_EVENT_TABLE,
                           EVENT_ID,
                           CADET_ID,
                           CADET_CLOTHING_SIZE,
                           CADET_CLOTHING_COLOUR)

        index_creation_query = "CREATE UNIQUE INDEX %s ON %s (%s,  %s)" % (
            INDEX_CADET_WITH_CLOTHING_AT_EVENT_TABLE,
            CADET_WITH_CLOTHING_AT_EVENT_TABLE,
            EVENT_ID,
            CADET_ID)

        try:
            self.cursor.execute(table_creation_query)
            self.cursor.execute(index_creation_query)
            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when creating identified cadets clothing table" % str(e1))
        finally:
            self.close()
