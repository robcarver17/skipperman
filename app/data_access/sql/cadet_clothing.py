from app.data_access.sql.cadets import SqlDataListOfCadets
from app.data_access.sql.generic_sql_data import GenericSqlData
from app.objects.cadets import ListOfCadets
from app.objects.clothing import ListOfCadetsWithClothingAndIdsAtEvent, CadetWithClothingAndIdsAtEvent, ClothingAtEvent, \
    UNALLOCATED_COLOUR
from app.data_access.sql.shared_column_names import *
from app.objects.composed.clothing_at_event import   DictOfCadetsWithClothingAtEvent
from app.objects.utilities.exceptions import MultipleMatches

CADET_WITH_CLOTHING_AT_EVENT_TABLE = "cadet_with_clothing_at_event"
INDEX_CADET_WITH_CLOTHING_AT_EVENT_TABLE = "index_cadet_with_clothing_at_event"

class SqlDataListOfCadetsWithClothingAtEvent(
    GenericSqlData
):
    def add_new_cadet_with_clothing_to_event(self, event_id: str, cadet_id:str, size: str):
        try:
            if self.table_does_not_exist(CADET_WITH_CLOTHING_AT_EVENT_TABLE):
                self.create_table()

            if self.does_cadet_have_clothing_record_at_event(event_id=event_id, cadet_id=cadet_id):
                raise MultipleMatches("Already have clothing record for cadet with ID %s at event ID %s" % (event_id, cadet_id))

            insertion = "INSERT INTO %s (%s, %s, %s, %s) VALUES (?, ?,?, ?)" % (
                CADET_WITH_CLOTHING_AT_EVENT_TABLE,
                EVENT_ID,
                CADET_ID,
                CADET_CLOTHING_SIZE,
                CADET_CLOTHING_COLOUR)
            self.cursor.execute(insertion,
                                (int(event_id), cadet_id, size, UNALLOCATED_COLOUR))

            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing to cadet clothing table event# %s" % (str(e1), event_id))
        finally:
            self.close()

    def does_cadet_have_clothing_record_at_event(self, event_id: str, cadet_id:str):
        cursor = self.cursor
        cursor.execute("SELECT COUNT(*) FROM %s WHERE %s='%s' AND %s='%s' " % (
            CADET_WITH_CLOTHING_AT_EVENT_TABLE,
            EVENT_ID, int(event_id),
            CADET_ID, int(cadet_id)
        ))
        raw_list = cursor.fetchall()
        count = int(raw_list[0][0])

        if count>1:
            raise MultipleMatches("Multiple clothing records for cadet with ID %s at event ID %s" % (event_id, cadet_id))
        elif count==0:
            return False
        else:
            return True


    def remove_clothing_for_cadet_at_event(self, event_id: str, cadet_id: str):
        try:
            if self.table_does_not_exist(CADET_WITH_CLOTHING_AT_EVENT_TABLE):
                self.create_table()

            self.cursor.execute("DELETE FROM %s WHERE %s='%s' AND %s='%s'" %
                            (CADET_WITH_CLOTHING_AT_EVENT_TABLE, EVENT_ID, int(event_id),
                             CADET_ID, int(cadet_id)))

        except Exception as e1:
            raise Exception("Error %s when writing to cadet clothing table event# %s" % (str(e1), event_id))
        finally:
            self.close()

    def clear_colour_group_for_cadet(
            self, event_id: str, cadet_id: str
    ):
        self.change_colour_group_for_cadet(event_id=event_id,
                                           cadet_id=cadet_id,
                                           colour=UNALLOCATED_COLOUR)

    def change_colour_group_for_cadet(self, event_id: str, cadet_id:str, colour:str):
        try:
            if self.table_does_not_exist(CADET_WITH_CLOTHING_AT_EVENT_TABLE):
                self.create_table()

            insertion = "UPDATE %s SET %s=? WHERE %s=%d AND %s=%d" % (
                    CADET_WITH_CLOTHING_AT_EVENT_TABLE,
                    CADET_CLOTHING_COLOUR,
            CADET_ID,
            int(cadet_id),
            EVENT_ID,
            int(event_id))
            self.cursor.execute(insertion,
                                (colour,))

            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing to cadet clothing table event# %s" % (str(e1), event_id))
        finally:
            self.close()

    def change_clothing_size_for_cadet(self, event_id: str, cadet_id:str, size:str):
        try:
            if self.table_does_not_exist(CADET_WITH_CLOTHING_AT_EVENT_TABLE):
                self.create_table()


            insertion = "UPDATE %s SET %s=? WHERE %s=%d AND %s=%d" % (
                    CADET_WITH_CLOTHING_AT_EVENT_TABLE,
                    CADET_CLOTHING_SIZE,
            CADET_ID,
            int(cadet_id),
            EVENT_ID,
            int(event_id))
            self.cursor.execute(insertion,
                                (size,))

            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing to cadet clothing table event# %s" % (str(e1), event_id))
        finally:
            self.close()

    def get_dict_of_cadets_with_clothing_at_event(self, event_id: str) -> DictOfCadetsWithClothingAtEvent:
        raw_data = self.read(event_id)
        new_dict = {}
        for raw_item in raw_data:
            cadet_id = raw_item.cadet_id
            cadet = self.list_of_cadets.cadet_with_id(cadet_id)
            new_dict [cadet] = ClothingAtEvent(colour=raw_item.colour,
                                               size =raw_item.size)

        return DictOfCadetsWithClothingAtEvent(new_dict)

    @property
    def list_of_cadets(self)-> ListOfCadets:
        list_of_cadets = getattr(self, "_list_of_cadets", None)
        if list_of_cadets is None:
            list_of_cadets = self._list_of_cadets = SqlDataListOfCadets(self.db_connection).read()

        return list_of_cadets

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
            self.cursor.execute("DELETE FROM %s WHERE %s='%s'" % (CADET_WITH_CLOTHING_AT_EVENT_TABLE, EVENT_ID, int(event_id)))

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
