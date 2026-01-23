from typing import List

from app.data_access.sql.generic_sql_data import GenericSqlData
from app.objects.wa_field_mapping import ListOfWAFieldMappings, WAFieldMap
from app.data_access.sql.shared_column_names import *

DATA_FIELD_MAPPING_TABLE = "data_field_mapping"
INDEX_DATA_FIELD_MAPPING_TABLE = "index_data_field_mapping"


class SqlDataWAFieldMapping(GenericSqlData):
    def read(self, event_id: str) -> ListOfWAFieldMappings:
        try:
            if self.table_does_not_exist(DATA_FIELD_MAPPING_TABLE):
                return ListOfWAFieldMappings.create_empty()

            cursor = self.cursor
            cursor.execute('''SELECT %s, %s FROM %s WHERE %s='%s' ORDER BY %s''' % (
                WA_FIELD, SM_FIELD, DATA_FIELD_MAPPING_TABLE, EVENT_ID, int(event_id), SM_FIELD
            ))
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading event mapping" % str(e1))
        finally:
            self.close()

        new_list = [
        WAFieldMap(skipperman_field = str(raw_mapping[0]), wa_field = str(raw_mapping[1]))
        for raw_mapping in raw_list]

        return ListOfWAFieldMappings(new_list)

    def write(self, wa_field_mapping: ListOfWAFieldMappings, event_id: str):
        try:
            if self.table_does_not_exist(DATA_FIELD_MAPPING_TABLE):
                self.create_table()

            event_id_as_int = int(event_id)
            self.cursor.execute("DELETE FROM %s WHERE %s='%s'" % (DATA_FIELD_MAPPING_TABLE,
                                                                  EVENT_ID,
                                                                  event_id_as_int))

            for event_map in wa_field_mapping:
                skipperman_field = str(event_map.skipperman_field)
                wa_field = str(event_map.wa_field)

                insertion = "INSERT INTO %s (%s, %s, %s) VALUES (?,?, ?)" % (
                    DATA_FIELD_MAPPING_TABLE,
                    EVENT_ID,
                    SM_FIELD, WA_FIELD)
                self.cursor.execute(insertion, (
                    event_id_as_int, skipperman_field, wa_field))

            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing event mappings" % str(e1))
        finally:
            self.close()

    def create_table(self):

        table_creation_query = """
                    CREATE TABLE %s (
                        %s INT, 
                        %s STR,
                        %s STR
                    );
                """ % (DATA_FIELD_MAPPING_TABLE,
                       EVENT_ID,
                       WA_FIELD, SM_FIELD)

        index_creation_query = "CREATE UNIQUE INDEX %s ON %s (%s, %s, %s)" % (
            INDEX_DATA_FIELD_MAPPING_TABLE,
            DATA_FIELD_MAPPING_TABLE,
            EVENT_ID,
            WA_FIELD,
            SM_FIELD)

        try:
            self.cursor.execute(table_creation_query)
            self.cursor.execute(index_creation_query)
            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when creating WA mapping table" % str(e1))
        finally:
            self.close()


MAPPING_TEMPLATE_DATA_TABLE = "mapping_template_data_table"
INDEX_MAPPING_TEMPLATE_DATA_TABLE = "index_mapping_template_data_table"

class SqlDataWAFieldMappingTemplates(GenericSqlData):
    def list_of_template_names(self) -> List[str]:
        cursor = self.cursor
        cursor.execute('''SELECT DISTINCT %s FROM %s ORDER BY %s''' % (
            MAPPING_TEMPLATE_NAME, MAPPING_TEMPLATE_DATA_TABLE, MAPPING_TEMPLATE_NAME
        ))
        raw_list = cursor.fetchall()
        list_of_names = [item[0] for item in raw_list]

        return list_of_names

    def read(self, template_name: str) -> ListOfWAFieldMappings:
        try:
            if self.table_does_not_exist(MAPPING_TEMPLATE_DATA_TABLE):
                return ListOfWAFieldMappings.create_empty()

            template_name = str(template_name)

            cursor = self.cursor
            cursor.execute('''SELECT %s, %s FROM %s WHERE %s='%s' ORDER BY %s''' % (
                WA_FIELD, SM_FIELD, MAPPING_TEMPLATE_DATA_TABLE, MAPPING_TEMPLATE_NAME, template_name, SM_FIELD
            ))
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading event mapping" % str(e1))
        finally:
            self.close()

        new_list = [
        WAFieldMap(skipperman_field = str(raw_mapping[0]), wa_field = str(raw_mapping[1]))
        for raw_mapping in raw_list]

        return ListOfWAFieldMappings(new_list)

    def write(
        self, wa_field_mapping: ListOfWAFieldMappings, template_name: str
    ):
        try:
            if self.table_does_not_exist(MAPPING_TEMPLATE_DATA_TABLE):
                self.create_table()
            template_name = str(template_name)
            self.cursor.execute("DELETE FROM %s WHERE %s='%s'" % (MAPPING_TEMPLATE_DATA_TABLE,
                                                                  MAPPING_TEMPLATE_NAME,
                                                                  template_name))

            for event_map in wa_field_mapping:
                skipperman_field = str(event_map.skipperman_field)
                wa_field = str(event_map.wa_field)

                insertion = "INSERT INTO %s (%s, %s, %s) VALUES (?,?, ?)" % (
                    MAPPING_TEMPLATE_DATA_TABLE,
                    MAPPING_TEMPLATE_NAME,
                    SM_FIELD, WA_FIELD)
                self.cursor.execute(insertion, (
                    template_name, skipperman_field, wa_field))

            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing event mappings" % str(e1))
        finally:
            self.close()

    def create_table(self):

        table_creation_query = """
                        CREATE TABLE %s (
                            %s STR, 
                            %s STR,
                            %s STR
                        );
                    """ % (MAPPING_TEMPLATE_DATA_TABLE,
                           MAPPING_TEMPLATE_NAME,
                           WA_FIELD, SM_FIELD)

        index_creation_query = "CREATE UNIQUE INDEX %s ON %s (%s, %s, %s)" % (
            INDEX_MAPPING_TEMPLATE_DATA_TABLE,
            MAPPING_TEMPLATE_DATA_TABLE,
            MAPPING_TEMPLATE_NAME,
            WA_FIELD,
            SM_FIELD)

        try:
            self.cursor.execute(table_creation_query)
            self.cursor.execute(index_creation_query)
            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when creating WA mapping table" % str(e1))
        finally:
            self.close()

