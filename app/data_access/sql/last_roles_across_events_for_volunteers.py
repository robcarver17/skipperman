from typing import Union

from app.data_access.sql.generic_sql_data import GenericSqlData
from app.data_access.sql.shared_column_names import *
from app.objects.composed.roles_and_teams import DictOfTeamsWithRoles
from app.objects.composed.volunteer_roles import ListOfRolesWithSkills
from app.objects.composed.volunteer_with_group_and_role_at_event import RoleAndGroupAndTeam
from app.objects.composed.volunteers_last_role_across_events import \
    DictOfVolunteersWithMostCommonRoleAndGroupAcrossEvents
from app.objects.groups import ListOfGroups
from app.objects.last_role_for_volunteer import ListOfMostCommonRoleForVolunteersAcrossEventsWithId, MostCommonRoleForVolunteerAcrossEventsWithId
from app.objects.utilities.exceptions import missing_data, MultipleMatches
from app.objects.volunteers import ListOfVolunteers

MOST_COMMON_ROLE_FOR_VOLUNTEER_ACROSS_EVENTS_TABLE = "most_common_role_for_volunteer_at_event"
INDEX_MOST_COMMON_ROLE_FOR_VOLUNTEER_ACROSS_EVENTS_TABLE = "index_most_common_role_for_volunteer_at_event"

class SqlDataListOfLastRolesAcrossEventsForVolunteers( GenericSqlData):

    def delete_volunteer_from_data(
            self, volunteer_id: str
    ):
        try:
            if self.table_does_not_exist(MOST_COMMON_ROLE_FOR_VOLUNTEER_ACROSS_EVENTS_TABLE):
                self.create_table()

            self.cursor.execute("DELETE FROM %s WHERE %s=%d" % (MOST_COMMON_ROLE_FOR_VOLUNTEER_ACROSS_EVENTS_TABLE,
                                                                VOLUNTEER_ID,
                                                                int(volunteer_id)))

            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing volunteers" % str(e1))
        finally:
            self.close()


    def get_most_common_role_and_group_or_none_for_volunteer_at_previous_events(
            self, volunteer_id: str
    ) -> Union[RoleAndGroupAndTeam, None]:
        raw_item = self.read_for_volunteer(volunteer_id=volunteer_id, default=missing_data)
        if raw_item is missing_data:
            return None
        group = self.list_of_groups.group_with_id(raw_item.group_id)
        role_with_skills = self.list_of_roles_with_skills.role_with_id(raw_item.role_id)
        teams_and_index = self.dict_of_teams_and_roles.list_of_teams_and_index_given_role(role_with_skills)
        role_group_team = RoleAndGroupAndTeam(role=role_with_skills,
                                              group=group,
                                              list_of_team_and_index=teams_and_index)

        return role_group_team

    def get_dict_of_volunteers_with_last_role_and_group_across_events(
            self
    ) -> DictOfVolunteersWithMostCommonRoleAndGroupAcrossEvents:
        raw_list = self.read()
        raw_dict ={}
        for raw_item in raw_list:
            volunteer = self.list_of_volunteers.volunteer_with_id(raw_item.volunteer_id)
            group = self.list_of_groups.group_with_id(raw_item.group_id)
            role_with_skills = self.list_of_roles_with_skills.role_with_id(raw_item.role_id)
            teams_and_index = self.dict_of_teams_and_roles.list_of_teams_and_index_given_role(role_with_skills)
            role_group_team = RoleAndGroupAndTeam(role = role_with_skills,
                                                  group=group,
                                                  list_of_team_and_index=teams_and_index)
            raw_dict[volunteer] = role_group_team

        return DictOfVolunteersWithMostCommonRoleAndGroupAcrossEvents(raw_dict)

    @property
    def list_of_groups(self) -> ListOfGroups:
        return self.object_store.get(self.object_store.data_api.data_list_of_groups.read)

    @property
    def list_of_roles_with_skills(self) ->  ListOfRolesWithSkills:
        list_of_roles_with_skills =  self.object_store.get(self.object_store.data_api.data_list_of_roles.read_list_of_roles_with_skills)

        return list_of_roles_with_skills



    @property
    def dict_of_teams_and_roles(self) -> DictOfTeamsWithRoles:
        return self.object_store.get(self.object_store.data_api.data_list_of_teams_and_roles_with_ids.get_dict_of_teams_and_roles)

    @property
    def list_of_volunteers(self) -> ListOfVolunteers:
        return self.object_store.get(
            self.object_store.data_api.data_list_of_volunteers.read)

    def read_for_volunteer(self, volunteer_id:str, default=missing_data) -> MostCommonRoleForVolunteerAcrossEventsWithId:
        if self.table_does_not_exist(MOST_COMMON_ROLE_FOR_VOLUNTEER_ACROSS_EVENTS_TABLE):
            return default

        try:
            cursor = self.cursor
            statement = "SELECT  %s, %s FROM %s WHERE %s=%d " % (
                ROLE_ID,
                GROUP_ID,
                MOST_COMMON_ROLE_FOR_VOLUNTEER_ACROSS_EVENTS_TABLE,
                VOLUNTEER_ID,
                int(volunteer_id)
            )
            cursor.execute(statement)
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s reading volunteer data" % str(e1))
        finally:
            self.close()

        if len(raw_list)==0:
            return default
        if len(raw_list)>1:
            raise MultipleMatches

        raw_item = raw_list[0]
        return    MostCommonRoleForVolunteerAcrossEventsWithId(
                volunteer_id = volunteer_id,
                role_id=str(raw_item[0]),
                group_id=str(raw_item[1])
            )

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

            self.cursor.execute("DELETE FROM %s" % (MOST_COMMON_ROLE_FOR_VOLUNTEER_ACROSS_EVENTS_TABLE))

            for volunteer_with_role in list_of_roles:
                self._add_row_without_checks_or_commits(volunteer_with_role)

            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing volunteers" % str(e1))
        finally:
            self.close()

    def _add_row_without_checks_or_commits(self,  volunteer_with_role: MostCommonRoleForVolunteerAcrossEventsWithId
                                           ):
        volunteer_id = int(volunteer_with_role.volunteer_id)
        role_id = int(volunteer_with_role.role_id)
        group_id = int(volunteer_with_role.group_id)

        insertion = "INSERT INTO %s (%s, %s, %s) VALUES (?,?,?)" % (
            MOST_COMMON_ROLE_FOR_VOLUNTEER_ACROSS_EVENTS_TABLE,
            VOLUNTEER_ID,
            ROLE_ID,
            GROUP_ID)

        self.cursor.execute(insertion, (
            volunteer_id,
            role_id,
            group_id))

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

