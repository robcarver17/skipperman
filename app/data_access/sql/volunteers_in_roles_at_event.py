from typing import Dict

from app.data_access.sql.generic_sql_data import GenericSqlData, bool2int, int2bool
from app.data_access.sql.shared_column_names import *
from app.data_access.sql.roles import SqlDataListOfRoles
from app.data_access.sql.groups import SqlDataListOfGroups
from app.objects.composed.volunteer_with_group_and_role_at_event import RoleAndGroup, DictOfDaysRolesAndGroups
from app.objects.day_selectors import Day
from app.objects.groups import unallocated_group_id
from app.objects.roles_and_teams import no_role_allocated_id, RolesWithSkillIds


from app.objects.volunteer_roles_and_groups_with_id import ListOfVolunteersWithIdInRoleAtEvent, VolunteerWithIdInRoleAtEvent

VOLUNTEERS_IN_ROLES_TABLE = "volunteers_in_roles"
INDEX_VOLUNTEERS_IN_ROLES_TABLE = "index_volunteers_in_roles"




class SqlDataListOfVolunteersInRolesAtEvent(
    GenericSqlData
):
    def get_role_and_groups_for_event_and_volunteer(self, event_id:str,
    volunteer_id:str) -> DictOfDaysRolesAndGroups:
        if self.table_does_not_exist(VOLUNTEERS_IN_ROLES_TABLE):
            return DictOfDaysRolesAndGroups({})

        try:
            cursor = self.cursor
            cursor.execute('''SELECT %s, %s, %s FROM %s WHERE %s='%s' AND %s=%d ''' % (
                 DAY,ROLE_ID, GROUP_ID,
                VOLUNTEERS_IN_ROLES_TABLE,
                EVENT_ID, int(event_id),
                VOLUNTEER_ID, int(volunteer_id)
            ))
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading volunteers in role at event %s" % (str(e1), event_id))
        finally:
            self.close()

        new_dict = dict(
            [
                (
                    Day[raw_data[0]], RoleAndGroup(
                        role=self.sql_roles.object_with_id(str(raw_data[1])),
                        group=self.sql_groups.object_with_id(str(raw_data[2]))
                    ),
                ) for raw_data in raw_list
            ]
        )

        return DictOfDaysRolesAndGroups(new_dict)


    @property
    def sql_groups(self):
        sql_groups = getattr(self,"_sql_groups", None)
        if sql_groups is None:
            self._sql_groups = sql_groups = SqlDataListOfGroups(self.db_connection).read()

        return sql_groups

    @property
    def sql_roles(self):
        sql_roles = getattr(self, "_sql_roles", None)
        if sql_roles is None:
            self._sql_roles = sql_roles = SqlDataListOfRoles(self.db_connection).read()

        return sql_roles


    def read(self, event_id: str) -> ListOfVolunteersWithIdInRoleAtEvent:
        if self.table_does_not_exist(VOLUNTEERS_IN_ROLES_TABLE):
            return ListOfVolunteersWithIdInRoleAtEvent.create_empty()

        try:
            cursor = self.cursor
            cursor.execute('''SELECT %s, %s, %s, %s FROM %s WHERE %s=%d ''' % (
                VOLUNTEER_ID, DAY, GROUP_ID, ROLE_ID, VOLUNTEERS_IN_ROLES_TABLE, EVENT_ID, int(event_id)
            ))
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading volunteers in role at event %s" % (str(e1), event_id))
        finally:
            self.close()

        list_of_volunteers_in_roles = [
            VolunteerWithIdInRoleAtEvent(
                volunteer_id=str(raw_data[0]),
                day = Day[raw_data[1]],
                group_id=str(raw_data[2]),
                role_id=str(raw_data[3])
            )
            for raw_data in raw_list
        ]

        return ListOfVolunteersWithIdInRoleAtEvent(list_of_volunteers_in_roles)

    volunteer_id: str
    day: Day
    group_id: str = unallocated_group_id
    role_id: str = no_role_allocated_id

    def write(
        self,
        list_of_volunteers_in_roles_at_event: ListOfVolunteersWithIdInRoleAtEvent,
        event_id: str,
    ):
        try:
            if self.table_does_not_exist(VOLUNTEERS_IN_ROLES_TABLE):
                self.create_table()

            ## NEEDS TO DELETE OLD
            ## TEMPORARY UNTIL CAN DO PROPERLY
            self.cursor.execute("DELETE FROM %s WHERE %s='%s'" % (VOLUNTEERS_IN_ROLES_TABLE, EVENT_ID, event_id))

            for volunteer_in_role in list_of_volunteers_in_roles_at_event:
                volunteer_id = int(volunteer_in_role.volunteer_id)
                day = volunteer_in_role.day.name
                group_id = int(volunteer_in_role.group_id)
                role_id = int(volunteer_in_role.role_id)
                insertion = "INSERT INTO %s (%s, %s, %s, %s, %s) VALUES (?, ?,?,?, ?)" % (
                    VOLUNTEERS_IN_ROLES_TABLE,
                EVENT_ID,
                VOLUNTEER_ID,
                DAY,
                GROUP_ID,
                ROLE_ID)
                self.cursor.execute(insertion,
                                    (int(event_id), volunteer_id, day, group_id, role_id))


            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing to volunteers in roles at event table event# %s" % (str(e1), event_id))
        finally:
            self.close()

    def create_table(self):
        table_creation_query = """
                CREATE TABLE %s (
                    %s INTEGER, 
                    %s INTEGER, 
                    %s STR,
                                        %s INTEGER,
                    %s INTEGER

                );
            """ % (VOLUNTEERS_IN_ROLES_TABLE,
                   EVENT_ID,
                   VOLUNTEER_ID,
                   DAY,
                   GROUP_ID,
                   ROLE_ID
                   )

        index_creation_query = "CREATE UNIQUE INDEX %s ON %s (%s, %s, %s)" % (INDEX_VOLUNTEERS_IN_ROLES_TABLE,
                                                                          VOLUNTEERS_IN_ROLES_TABLE,
                                                                          EVENT_ID, VOLUNTEER_ID, DAY
                                                                          )

        try:
            self.cursor.execute(table_creation_query)
            self.cursor.execute(index_creation_query)
            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when creating volunteers in roles table" % str(e1))
        finally:
            self.close()
