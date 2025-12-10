import pandas as pd

from app.data_access.sql.generic_sql_data import GenericSqlData
from app.objects.cadet_with_id_with_group_at_event import ListOfCadetIdsWithGroups


CADETS_WITH_GROUP_ID_TABLE = "list_of_cadet_ids_with_groups"
CADET_ID = "cadet_id"
GROUP_ID = "group_id"
EVENT_ID = "event_id"
DAY = "day"
INDEX_NAME_CADETS_WITH_GROUP_ID_TABLE = "event_cadet_day"

class SqlDataListOfCadetsWithGroups(GenericSqlData):
    def read(self, event_id: str) -> ListOfCadetIdsWithGroups:
        if self.table_does_not_exist(CADETS_WITH_GROUP_ID_TABLE):
            self.create_table()

        cursor = self.cursor
        cursor.execute('''SELECT %s, %s, %s FROM %s WHERE %s='%s' ''' % (
            CADET_ID, DAY, GROUP_ID,
            CADETS_WITH_GROUP_ID_TABLE, EVENT_ID, event_id
        ))
        raw_list = cursor.fetchall()

        if len(raw_list)==0:
            return ListOfCadetIdsWithGroups.create_empty()

        raw_dict = {
            CADET_ID: [ans[0] for ans in raw_list],
            DAY: [ans[1] for ans in raw_list],
            GROUP_ID: [ans[2] for ans in raw_list],
        }

        df = pd.DataFrame(raw_dict)

        return ListOfCadetIdsWithGroups.from_df_of_str(df)

    def write(
        self, list_of_cadets_with_groups: ListOfCadetIdsWithGroups, event_id: str
    ):
        if self.table_does_not_exist(CADETS_WITH_GROUP_ID_TABLE):
            self.create_table()

        ## NEEDS TO DELETE OLD
        ## TEMPORARY UNTIL CAN DO PROPERLY
        self.cursor.execute("DELETE FROM %s WHERE %s='%s'" % (CADETS_WITH_GROUP_ID_TABLE, EVENT_ID, event_id))

        for cadet_with_group_ids in list_of_cadets_with_groups:
            cadet_id = cadet_with_group_ids.cadet_id
            group_id =cadet_with_group_ids.group_id
            day_name =cadet_with_group_ids.day.name

            insertion = "INSERT INTO %s (%s, %s, %s, %s) VALUES ('%s', '%s', '%s', '%s')" % (
                CADETS_WITH_GROUP_ID_TABLE,
                    EVENT_ID, CADET_ID, DAY,    GROUP_ID,
                    event_id, cadet_id, day_name, group_id)
            self.cursor.execute(insertion)

        self.conn.commit()


    def create_table(self):
        self.cursor.execute(table_creation_query)
        self.cursor.execute(index_creation_query)
        self.conn.commit()

table_creation_query = """
    CREATE TABLE %s (
        %s STR, 
        %s STR,
        %s STR,
        %s STR
    );
""" % (CADETS_WITH_GROUP_ID_TABLE,EVENT_ID, CADET_ID,  DAY, GROUP_ID)

index_creation_query = "CREATE UNIQUE INDEX %s ON %s (%s, %s, %s)" % (INDEX_NAME_CADETS_WITH_GROUP_ID_TABLE,
                                                                    CADETS_WITH_GROUP_ID_TABLE,
                                                                    EVENT_ID,
                                                                    CADET_ID,
                                                                    DAY)