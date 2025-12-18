from typing import List

from app.data_access.sql.generic_sql_data import GenericSqlData
from app.data_access.sql.shared_column_names import *
from app.objects.composed.roles_and_teams import  DictOfTeamsWithRoles
from app.objects.composed.volunteer_roles import ListOfRolesWithSkills
from app.objects.roles_and_teams import ListOfTeamsAndRolesWithIds, TeamsAndRolesWithIds,   ListOfTeams
from app.data_access.sql.teams import  SqlDataListOfTeams
from app.data_access.sql.roles import SqlDataListOfRoles
from app.objects.utilities.exceptions import arg_not_passed

TEAMS_AND_ROLES_TABLE = "teams_and_roles"
INDEX_TEAMS_AND_ROLES_TABLE = "index_teams_and_roles"

class SqlDataListOfTeamsAndRolesWithIds(GenericSqlData):
    def get_dict_of_teams_and_roles(self) -> DictOfTeamsWithRoles:
        list_of_teams = self.list_of_teams

        new_dict = dict(
            [
                (team,
                self.roles_and_skills_for_team_id(team.id)
                 )
                for team in list_of_teams
            ]
        )
        return DictOfTeamsWithRoles(new_dict)

    def roles_and_skills_for_team_id(self, team_id:str) ->                 ListOfRolesWithSkills:
        list_of_role_ids = self.ordered_role_ids_for_team_id(team_id)
        list_of_roles = self.list_of_roles
        list_of_roles_and_skills = ListOfRolesWithSkills([list_of_roles.role_with_id(role_id, default=arg_not_passed) for role_id in list_of_role_ids])

        return list_of_roles_and_skills

    @property
    def list_of_roles(self) -> ListOfRolesWithSkills:
        list_of_roles = getattr(self, "_list_of_roles", None)
        if list_of_roles is None:
            list_of_roles = self._list_of_roles = SqlDataListOfRoles(self.db_connection).read_list_of_roles_with_skills()

        return list_of_roles

    @property
    def list_of_teams(self) -> ListOfTeams:
        list_of_teams = getattr(self, "_list_of_teams", None)
        if list_of_teams is None:
            list_of_teams = self._list_of_teams = SqlDataListOfTeams(self.db_connection).read()

        return list_of_teams

    def ordered_role_ids_for_team_id(self, team_id:str) -> List[str]:
        try:
            if self.table_does_not_exist(TEAMS_AND_ROLES_TABLE):
                self.create_table()

            cursor = self.cursor
            cursor.execute('''SELECT  %s FROM %s WHERE %s=%d ORDER BY %s''' % (
                ROLE_ID, TEAMS_AND_ROLES_TABLE, TEAM_ID, int(team_id), TEAM_IDX
            ))
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading teams and roles" % str(e1))
        finally:
            self.close()

        return [str(raw_item[0]) for raw_item in raw_list]


    def read(self) -> ListOfTeamsAndRolesWithIds:
        try:
            if self.table_does_not_exist(TEAMS_AND_ROLES_TABLE):
                self.create_table()

            cursor = self.cursor
            cursor.execute('''SELECT %s, %s, %s FROM %s''' % (
                TEAM_ID, ROLE_ID, TEAM_IDX, TEAMS_AND_ROLES_TABLE
            ))
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading teams and roles" % str(e1))
        finally:
            self.close()

        new_list = [TeamsAndRolesWithIds(
            team_id=str(raw_team_and_role[0]),
            role_id=str(raw_team_and_role[1]),
            order_idx=raw_team_and_role[2]
            ) for raw_team_and_role in raw_list]

        return ListOfTeamsAndRolesWithIds(new_list)

    def write(self, list_of_teams_and_roles_with_ids: ListOfTeamsAndRolesWithIds):
        try:
            if self.table_does_not_exist(TEAMS_AND_ROLES_TABLE):
                self.create_table()

            self.cursor.execute("DELETE FROM %s" % (TEAMS_AND_ROLES_TABLE))

            for team_with_role in list_of_teams_and_roles_with_ids:
                team_id = int(team_with_role.team_id)
                role_id = int(team_with_role.role_id)
                team_idx = int(team_with_role.order_idx)

                insertion = "INSERT INTO %s (%s, %s, %s) VALUES (?,?,?)" % (
                    TEAMS_AND_ROLES_TABLE,
                    TEAM_ID,
                    ROLE_ID,
                    TEAM_IDX)

                self.cursor.execute(insertion, (
                    team_id, role_id, team_idx))

            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing teams and roles" % str(e1))
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
                """ % (TEAMS_AND_ROLES_TABLE,
                       TEAM_ID,
                       ROLE_ID,
                       TEAM_IDX)

        index_creation_query = "CREATE UNIQUE INDEX %s ON %s (%s, %s)" % (
            INDEX_TEAMS_AND_ROLES_TABLE, TEAMS_AND_ROLES_TABLE, TEAM_ID, TEAM_IDX)

        try:
            self.cursor.execute(table_creation_query)
            self.cursor.execute(index_creation_query)
            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when creating teams and roles table" % str(e1))
        finally:
            self.close()


