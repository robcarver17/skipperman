

from app.data_access.sql.generic_sql_data import GenericSqlData, bool2int, int2bool
from app.data_access.sql.shared_column_names import *
from app.objects.groups import ListOfGroups, Group, GroupLocation

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

        new_list = []
        for raw_group in raw_list:
            group = Group(
                name=raw_group[0],
                location=GroupLocation[raw_group[1]],
                protected=int2bool(raw_group[2]),
                hidden=int2bool(raw_group[3]),
                streamer=raw_group[4],
                id=str(raw_group[5])
            )
            new_list.append(group)

        return ListOfGroups(new_list)

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
                id = int(group.id)

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

    def delete_table(self):
        self.conn.execute("DROP TABLE %s" % GROUPS_TABLE)
        self.conn.commit()
        self.close()

    def create_table(self):

        table_creation_query = """
            CREATE TABLE %s (
                %s STR, 
                %s STR,
                %s INTEGER,
                %s INTEGER,
                %s STR,
                %s INTEGER,
                %s INTEGER
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



