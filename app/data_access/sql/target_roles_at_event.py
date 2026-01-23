from app.data_access.sql.generic_sql_data import GenericSqlData
from app.objects.volunteer_role_targets import ListOfTargetForRoleWithIdAtEvent, TargetForRoleWithIdAtEvent
from app.data_access.sql.shared_column_names import *

VOLUNTEER_TARGETS_AT_EVENT_TABLE = "volunteer_targets_at_event"
INDEX_VOLUNTEER_TARGETS_AT_EVENT_TABLE = "index_volunteer_targets_at_event"

class SqlDataListOfTargetForRoleAtEvent(GenericSqlData):
    def read(self, event_id: str) -> ListOfTargetForRoleWithIdAtEvent:
        if self.table_does_not_exist(VOLUNTEER_TARGETS_AT_EVENT_TABLE):
            return ListOfTargetForRoleWithIdAtEvent.create_empty()

        try:
            cursor = self.cursor
            cursor.execute('''SELECT %s, %s  FROM %s WHERE %s='%s' ''' % (
                ROLE_ID, VOLUNTEER_TARGET_NUMBER,
                VOLUNTEER_TARGETS_AT_EVENT_TABLE,
                EVENT_ID, int(event_id)))

            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading volunteer targets at event" % str(e1))
        finally:
            self.close()

        new_list = [
            TargetForRoleWithIdAtEvent(
                role_id=str(item[0]),
                target=int(item[1])
            )
            for item in raw_list
        ]

        return ListOfTargetForRoleWithIdAtEvent(new_list)


    def write(
        self,
        list_of_targets_for_roles_at_event: ListOfTargetForRoleWithIdAtEvent,
        event_id: str,
    ):
        try:
            if self.table_does_not_exist(VOLUNTEER_TARGETS_AT_EVENT_TABLE):
                self.create_table()

            ## NEEDS TO DELETE OLD
            ## TEMPORARY UNTIL CAN DO PROPERLY
            self.cursor.execute("DELETE FROM %s WHERE %s='%s'" % (VOLUNTEER_TARGETS_AT_EVENT_TABLE,
                                                                  EVENT_ID,
                                                                  int(event_id)))

            for people_with_target in list_of_targets_for_roles_at_event:
                role_id = int(people_with_target.role_id)
                target = int(people_with_target.target)

                insertion = "INSERT INTO %s (%s, %s, %s) VALUES (?,?,?)" % (
                    VOLUNTEER_TARGETS_AT_EVENT_TABLE,
                    EVENT_ID,
                ROLE_ID,
                VOLUNTEER_TARGET_NUMBER)

                self.cursor.execute(insertion, (
                    int(event_id), role_id, target))

            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing volunteer targets at event" % str(e1))
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
                    %s INTEGER
                );
            """ % (VOLUNTEER_TARGETS_AT_EVENT_TABLE,
                   EVENT_ID,
                   ROLE_ID, VOLUNTEER_TARGET_NUMBER)

        index_creation_query = "CREATE UNIQUE INDEX %s ON %s (%s, %s)" % (INDEX_VOLUNTEER_TARGETS_AT_EVENT_TABLE,
                                                                      VOLUNTEER_TARGETS_AT_EVENT_TABLE,
                                                                      EVENT_ID,
                                                                      ROLE_ID)

        try:
            self.cursor.execute(table_creation_query)
            self.cursor.execute(index_creation_query)
            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when creating volunteer target table" % str(e1))
        finally:
            self.close()


