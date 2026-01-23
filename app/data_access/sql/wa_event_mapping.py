
from app.data_access.sql.generic_sql_data import GenericSqlData
from app.objects.wa_event_mapping import ListOfWAEventMaps, WAEventMap
from app.data_access.sql.shared_column_names import *

WA_EVENT_MAPPING_TABLE = "wa_event_mapping"
INDEX_WA_EVENT_MAPPING_TABLE = "index_wa_event_mapping"


class SqlDataWAEventMapping(GenericSqlData):
    def read(self) -> ListOfWAEventMaps:
        try:
            if self.table_does_not_exist(WA_EVENT_MAPPING_TABLE):
                return ListOfWAEventMaps.create_empty()

            cursor = self.cursor
            cursor.execute('''SELECT %s, %s FROM %s''' % (
                    EVENT_ID,
                WA_ID,
                WA_EVENT_MAPPING_TABLE
            ))
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading event mapping" % str(e1))
        finally:
            self.close()

        new_list = [
        WAEventMap(event_id=str(raw_mapping[0]), wa_id=str(raw_mapping[1]))
        for raw_mapping in raw_list]

        return ListOfWAEventMaps(new_list)

    def write(self, wa_event_mapping: ListOfWAEventMaps):
        try:
            if self.table_does_not_exist(WA_EVENT_MAPPING_TABLE):
                self.create_table()

            self.cursor.execute("DELETE FROM %s" % (WA_EVENT_MAPPING_TABLE))

            for event_map in wa_event_mapping:
                event_id = int(event_map.event_id)
                wa_id = int(event_map.wa_id)

                insertion = "INSERT INTO %s (%s, %s) VALUES (?,?)" % (
                    WA_EVENT_MAPPING_TABLE,
                EVENT_ID, WA_ID)

                self.cursor.execute(insertion, (
                    event_id, wa_id))

            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing event mappings" % str(e1))
        finally:
            self.close()

    def create_table(self):

        table_creation_query = """
                CREATE TABLE %s (
                    %s INTEGER,
                    %s INTEGER
                );
            """ % (WA_EVENT_MAPPING_TABLE,
                   EVENT_ID, WA_ID)

        index_creation_query = "CREATE UNIQUE INDEX %s ON %s (%s, %s)" % (
            INDEX_WA_EVENT_MAPPING_TABLE,
        WA_EVENT_MAPPING_TABLE,
        EVENT_ID,
        WA_ID)

        try:
            self.cursor.execute(table_creation_query)
            self.cursor.execute(index_creation_query)
            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when creating WA mapping table" % str(e1))
        finally:
            self.close()

