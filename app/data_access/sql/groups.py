

from app.data_access.sql.generic_sql_data import GenericSqlData, bool2int, int2bool
from app.data_access.sql.shared_column_names import *
from app.objects.groups import ListOfGroups, Group, GroupLocation
from app.objects.utilities.exceptions import arg_not_passed, MultipleMatches, missing_data

### GROUPS
GROUPS_TABLE = "groups_table"
INDEX_NAME_GROUPS_TABLE = "group_id"

class SqlDataListOfGroups(GenericSqlData):

    def add_new_group(
            self, new_group: Group
    ):
        group_name = new_group.name
        if self.group_with_name_exists(group_name):
            raise Exception("group named %s already exists" % group_name)

        try:
            if self.table_does_not_exist(GROUPS_TABLE):
                self.create_table()

            group_id= str(self.next_available_id())
            idx = self.next_available_order()
            new_group.id = group_id

            self._add_group_without_commit_or_checks(group=new_group,
                                                     idx=idx,

                                                     )

            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing groups" % str(e1))
        finally:
            self.close()


    def next_available_id(self) ->int:
        return self.last_used_id()+1

    def last_used_id(self)-> int:
        try:
            if self.table_does_not_exist(GROUPS_TABLE):
                self.create_table()

            cursor = self.cursor
            statement = "SELECT MAX(%s) FROM %s" % (
                GROUP_ID,
                GROUPS_TABLE,
            )
            cursor.execute(statement)
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s reading groups data" % str(e1))
        finally:
            self.close()

        if len(raw_list) == 0:
            return -1
        else:
            return int(raw_list[0][0])

    def next_available_order(self) ->int:
        return self.last_used_order()+1

    def last_used_order(self)-> int:
        try:
            if self.table_does_not_exist(GROUPS_TABLE):
                self.create_table()

            cursor = self.cursor
            statement = "SELECT MAX(%s) FROM %s" % (
                GROUP_ORDER,
                GROUPS_TABLE,
            )
            cursor.execute(statement)
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s reading groups data" % str(e1))
        finally:
            self.close()

        if len(raw_list) == 0:
            return -1
        else:
            return int(raw_list[0][0])


    def modify_sailing_group(
            self, existing_group_id: str, new_group: Group
    ):
        existing_group = self.get_group_with_id(existing_group_id, default=missing_data)
        if existing_group is missing_data:
            raise Exception("Can't modify group as can't find original group with ID %s" % existing_group_id)

        if existing_group.name == new_group.name:
            pass
        else:
            if self.group_with_name_exists(new_group.name):
                raise Exception("cannot rename %s as group named %s already exists" % (existing_group.name, new_group.name))
        self._modify_sailing_group_without_checks(existing_group_id=existing_group_id, new_group=new_group)

    def _modify_sailing_group_without_checks(
            self, existing_group_id: str, new_group: Group
    ):

        try:

            insertion = "UPDATE %s SET %s='%s', %s='%s', %s='%s', %s='%s'  WHERE %s=%d" % (
                GROUPS_TABLE,

                GROUP_NAME,
                str(new_group.name),
                LOCATION,
                str(new_group.location.name),
                HIDDEN,
                bool2int(new_group.hidden),
                STREAMER,
                str(new_group.streamer),
            GROUP_ID,
            int(existing_group_id))

            self.cursor.execute(insertion)
            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s writing groups data" % str(e1))
        finally:
            self.close()


    def group_with_name_exists(self, group_name: str) -> bool:
        group = self.get_group_with_name(group_name, default=missing_data)
        if group is missing_data:
            return False
        else:
            return True

    def get_group_with_name(
            self, group_name: str, default=arg_not_passed
    ) -> Group:
        if self.table_does_not_exist(GROUPS_TABLE):
            return default

        try:
            cursor = self.cursor
            cursor.execute('''SELECT %s, %s, %s, %s, %s FROM %s  WHERE %s='%s' ''' % (
                GROUP_ID, LOCATION, PROTECTED, HIDDEN, STREAMER,
                GROUPS_TABLE,
                GROUP_NAME,
                str(group_name)
            ))
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading groups" % str(e1))
        finally:
            self.close()

        if len(raw_list) == 0:
            return default
        if len(raw_list) > 1:
            raise MultipleMatches("More than one group has name %s" % group_name)

        raw_group = raw_list[0]
        group = Group(
            name=group_name,
            id=str(raw_group[0]),
            location=GroupLocation[raw_group[1]],
            protected=int2bool(raw_group[2]),
            hidden=int2bool(raw_group[3]),
            streamer=raw_group[4],
        )

        return group

    def get_group_with_id(
            self, group_id: str, default=missing_data
    ) -> Group:
        if self.table_does_not_exist(GROUPS_TABLE):
            return default

        try:
            cursor = self.cursor
            cursor.execute('''SELECT %s, %s, %s, %s, %s FROM %s  WHERE %s=%d ''' % (
                GROUP_NAME, LOCATION, PROTECTED, HIDDEN, STREAMER,
                GROUPS_TABLE,
                GROUP_ID,
                int(group_id)
            ))
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading groups" % str(e1))
        finally:
            self.close()

        if len(raw_list)==0:
            return default
        if len(raw_list)>1:
            raise MultipleMatches("More than one group has ID %s" % group_id)

        raw_group=raw_list[0]
        group = Group(
                name=raw_group[0],
                location=GroupLocation[raw_group[1]],
                protected=int2bool(raw_group[2]),
                hidden=int2bool(raw_group[3]),
                streamer=raw_group[4],
                id=group_id
            )

        return group

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
                self._add_group_without_commit_or_checks(group=group,
                                                         idx=idx,
                                                         )

            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing groups" % str(e1))
        finally:
            self.close()

    def _add_group_without_commit_or_checks(self, group: Group,  idx: int):
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



