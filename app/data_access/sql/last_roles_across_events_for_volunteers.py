from app.data_access.sql.generic_sql_data import GenericSqlData
from app.data_access.sql.shared_column_names import *
from app.objects.last_role_for_volunteer import ListOfMostCommonRoleForVolunteersAcrossEventsWithId, MostCommonRoleForVolunteerAcrossEventsWithId

MOST_COMMON_ROLE_FOR_VOLUNTEER_ACROSS_EVENTS_TABLE = "most_common_role_for_volunteer_at_event"
INDEX_MOST_COMMON_ROLE_FOR_VOLUNTEER_ACROSS_EVENTS_TABLE = "index_most_common_role_for_volunteer_at_event"

class SqlDataListOfLastRolesAcrossEventsForVolunteers( GenericSqlData):
    def read(self) -> ListOfMostCommonRoleForVolunteersAcrossEventsWithId:
        if self.table_does_not_exist(MOST_COMMON_ROLE_FOR_VOLUNTEER_ACROSS_EVENTS_TABLE):
            return ListOfMostCommonRoleForVolunteersAcrossEventsWithId.create_empty()

        try:
            cursor = self.cursor
            statement = "SELECT %s, %s, %s FROM %s" % (
                VOLUNTEER_ID,
                ROLE_ID,
                GROUP_ID,
                MOST_COMMON_ROLE_FOR_VOLUNTEER_ACROSS_EVENTS_TABLE
            )
            cursor.execute(statement)
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s reading volunteer data" % str(e1))
        finally:
            self.close()

        new_list = [
            MostCommonRoleForVolunteerAcrossEventsWithId(
                volunteer_id = str(raw_item[0]),
                role_id=str(raw_item[1]),
                group_id=str(raw_item[2])
            )
            for raw_item in raw_list
        ]

        return ListOfMostCommonRoleForVolunteersAcrossEventsWithId(new_list)


    def write(self, list_of_roles: ListOfMostCommonRoleForVolunteersAcrossEventsWithId):
        try:
            if self.table_does_not_exist(MOST_COMMON_ROLE_FOR_VOLUNTEER_ACROSS_EVENTS_TABLE):
                self.create_table()

            ## NEEDS TO DELETE OLD
            ## TEMPORARY UNTIL CAN DO PROPERLY
            self.cursor.execute("DELETE FROM %s" % (MOST_COMMON_ROLE_FOR_VOLUNTEER_ACROSS_EVENTS_TABLE))

            for volunteer_with_role in list_of_roles:
                volunteer_id=int(volunteer_with_role.volunteer_id)
                role_id=int(volunteer_with_role.role_id)
                group_id=int(volunteer_with_role.group_id)

                insertion = "INSERT INTO %s (%s, %s, %s) VALUES (?,?,?)" % (
                    MOST_COMMON_ROLE_FOR_VOLUNTEER_ACROSS_EVENTS_TABLE,
                VOLUNTEER_ID,
                ROLE_ID,
                GROUP_ID)

                self.cursor.execute(insertion, (
                    volunteer_id,
                role_id,
                group_id))

            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing volunteers" % str(e1))
        finally:
            self.close()


    def create_table(self):

        table_creation_query = """
                CREATE TABLE %s (
                    %s INTEGER,
                    %s INTEGER,
                    %s INTEGER
                );
            """ % (MOST_COMMON_ROLE_FOR_VOLUNTEER_ACROSS_EVENTS_TABLE,
                   VOLUNTEER_ID,
                   GROUP_ID,
                   ROLE_ID)

        index_creation_query = "CREATE UNIQUE INDEX %s ON %s (%s)" % (
        INDEX_MOST_COMMON_ROLE_FOR_VOLUNTEER_ACROSS_EVENTS_TABLE, MOST_COMMON_ROLE_FOR_VOLUNTEER_ACROSS_EVENTS_TABLE,
        VOLUNTEER_ID)

        try:
            self.cursor.execute(table_creation_query)
            self.cursor.execute(index_creation_query)
            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s creating volunteers table" % str(e1))
        finally:
            self.close()

