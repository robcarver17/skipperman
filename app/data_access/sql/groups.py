import pandas as pd

from app.data_access.sql.generic_sql_data import GenericSqlData, bool2int, int2bool
from app.data_access.sql.shared_column_names import *
from app.objects.cadet_with_id_with_group_at_event import ListOfCadetIdsWithGroups
from app.objects.groups import ListOfGroups

### GROUPS
GROUPS_TABLE = "groups_table"
INDEX_NAME_GROUPS_TABLE = "group_id"

class SqlDataListOfGroups(GenericSqlData):
    def read(self) -> ListOfGroups:
        try:
            if self.table_does_not_exist(GROUPS_TABLE):
                self.create_table()

            cursor = self.cursor
            cursor.execute('''SELECT %s, %s, %s, %s, %s, %s FROM %s ORDER BY %s''' % (
                GROUP_NAME, LOCATION, PROTECTED, HIDDEN, STREAMER, GROUP_ID,
                GROUPS_TABLE, GROUP_ORDER
            ))
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading groups" % str(e1))
        finally:
            self.close()

        if len(raw_list) == 0:
            return ListOfGroups.create_empty()

        raw_dict = {
            'name': [ans[0] for ans in raw_list],
            'location': [ans[1] for ans in raw_list],
            'protected': [int2bool(ans[2]) for ans in raw_list],
            'hidden': [int2bool(ans[3]) for ans in raw_list],
            'streamer': [ans[4] for ans in raw_list],
            'id': [ans[5] for ans in raw_list],
        }

        df = pd.DataFrame(raw_dict)

        return ListOfGroups.from_df_of_str(df)

    def write(
            self, list_of_groups: ListOfGroups
    ):
        try:
            if self.table_does_not_exist(GROUPS_TABLE):
                self.create_table()

            ## NEEDS TO DELETE OLD
            ## TEMPORARY UNTIL CAN DO PROPERLY
            self.cursor.execute("DELETE FROM %s" % (GROUPS_TABLE))

            for idx, group in enumerate(list_of_groups):
                name = group.name
                location = group.location.name
                protected = bool2int(group.protected)
                hidden = bool2int(group.hidden)
                streamer = group.streamer
                id = group.id

                insertion = "INSERT INTO %s (%s, %s, %s, %s, %s, %s, %s) VALUES (?,?,?,?,?,?, ?)" % (
                    GROUPS_TABLE,
                    GROUP_NAME, LOCATION, PROTECTED, HIDDEN, STREAMER, GROUP_ID, GROUP_ORDER)

                self.cursor.execute(insertion, (
                    name, location, protected, hidden, streamer, id, idx))

            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing groups" % str(e1))
        finally:
            self.close()

    def create_table(self):

        table_creation_query = """
            CREATE TABLE %s (
                %s STR, 
                %s STR,
                %s INTEGER,
                %s INTEGER,
                %s STR,
                %s STR,
                %s STR
            );
        """ % (GROUPS_TABLE,
                GROUP_NAME, LOCATION, PROTECTED, HIDDEN, STREAMER, GROUP_ID,GROUP_ORDER)

        index_creation_query = "CREATE UNIQUE INDEX %s ON %s (%s)" % (INDEX_NAME_GROUPS_TABLE, GROUPS_TABLE, GROUP_ID)

        try:
            self.cursor.execute(table_creation_query)
            self.cursor.execute(index_creation_query)
            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when creating groups table" % str(e1))
        finally:
            self.close()

#### GROUPS WITH IDS

CADETS_WITH_GROUP_ID_TABLE = "list_of_cadet_ids_with_groups"
INDEX_NAME_CADETS_WITH_GROUP_ID_TABLE = "event_cadet_day"

class SqlDataListOfCadetsWithGroups(GenericSqlData):
    def read(self, event_id: str) -> ListOfCadetIdsWithGroups:
        if self.table_does_not_exist(CADETS_WITH_GROUP_ID_TABLE):
            self.create_table()

        try:
            cursor = self.cursor
            cursor.execute('''SELECT %s, %s, %s FROM %s WHERE %s='%s' ''' % (
                CADET_ID, DAY, GROUP_ID,
                CADETS_WITH_GROUP_ID_TABLE, EVENT_ID, event_id
            ))
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading groups at events" % str(e1))
        finally:
            self.close()

        if len(raw_list)==0:
            return ListOfCadetIdsWithGroups.create_empty()

        raw_dict = {
            'cadet_id': [ans[0] for ans in raw_list],
            'day': [ans[1] for ans in raw_list],
            'group_id': [ans[2] for ans in raw_list],
        }

        df = pd.DataFrame(raw_dict)

        return ListOfCadetIdsWithGroups.from_df_of_str(df)

    def write(
        self, list_of_cadets_with_groups: ListOfCadetIdsWithGroups, event_id: str
    ):
        try:
            if self.table_does_not_exist(CADETS_WITH_GROUP_ID_TABLE):
                self.create_table()

            ## NEEDS TO DELETE OLD
            ## TEMPORARY UNTIL CAN DO PROPERLY
            self.cursor.execute("DELETE FROM %s WHERE %s='%s'" % (CADETS_WITH_GROUP_ID_TABLE, EVENT_ID, event_id))

            for cadet_with_group_ids in list_of_cadets_with_groups:
                cadet_id = cadet_with_group_ids.cadet_id
                group_id =cadet_with_group_ids.group_id
                day_name =cadet_with_group_ids.day.name

                insertion = "INSERT INTO %s (%s, %s, %s, %s) VALUES (?, ?,?,?)" % (
                    CADETS_WITH_GROUP_ID_TABLE,
                    EVENT_ID, CADET_ID, DAY, GROUP_ID)
                self.cursor.execute(insertion,
                                    (event_id, cadet_id, day_name, group_id))

            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing to groups at event table" % str(e1))
        finally:
            self.close()

    def create_table(self):

        table_creation_query = """
            CREATE TABLE %s (
                %s STR, 
                %s STR,
                %s STR,
                %s STR
            );
        """ % (CADETS_WITH_GROUP_ID_TABLE, EVENT_ID, CADET_ID, DAY, GROUP_ID)

        index_creation_query = "CREATE UNIQUE INDEX %s ON %s (%s, %s, %s)" % (INDEX_NAME_CADETS_WITH_GROUP_ID_TABLE,
                                                                              CADETS_WITH_GROUP_ID_TABLE,
                                                                              EVENT_ID,
                                                                              CADET_ID,
                                                                              DAY)
        try:
            self.cursor.execute(table_creation_query)
            self.cursor.execute(index_creation_query)
            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when creating table" % str(e1))

