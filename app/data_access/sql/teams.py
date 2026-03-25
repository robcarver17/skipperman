from app.data_access.sql.generic_sql_data import GenericSqlData
from app.objects.utilities.transform_data import bool2int, int2bool
from app.objects.roles_and_teams import Team, ListOfTeams, RoleLocation
from app.data_access.sql.shared_column_names import *


TEAMS_TABLE = "teams"
INDEX_TEAMS_TABLE = "index_teams_table"


class SqlDataListOfTeams(GenericSqlData):
    def add_new_team(self, new_team: Team):
        if self.does_team_with_name_exist(new_team.name):
            raise Exception("Team with name %s already exists" % new_team.name)

        self._add_new_team_without_checks(new_team)

    def _add_new_team_without_checks(self, new_team: Team):
        idx = self.next_available_idx()

        new_team.id = str(self.next_available_id())
        try:
            if self.table_does_not_exist(TEAMS_TABLE):
                self.create_table()

            self._add_row_without_checks_or_commits(idx=idx, team=new_team)

            self.conn.commit()

        except Exception as e1:
            raise Exception("Error %s when writing teams" % str(e1))
        finally:
            self.close()

    def modify_team(self, original_team: Team, new_team: Team):
        if original_team.name == new_team.name:
            pass
        else:
            if self.does_team_with_name_exist(new_team.name):
                raise Exception("Team with name %s already exists" % new_team.name)

        self._modify_team_without_checks(original_team=original_team, new_team=new_team)

    def _modify_team_without_checks(self, original_team: Team, new_team: Team):
        team_id = int(original_team.id)
        name = new_team.name
        location = new_team.location_for_cadet_warning.name
        protected = bool2int(new_team.protected)

        try:
            if self.table_does_not_exist(TEAMS_TABLE):
                self.create_table()
            self.cursor.execute(
                "UPDATE %s SET %s=?, %s=?, %s=? WHERE %s=%d"
                % (
                    TEAMS_TABLE,
                    TEAM_NAME,
                    TEAM_LOCATION,
                    PROTECTED,
                    TEAM_ID,
                    team_id,
                ),
                (name, location, protected),
            )

            self.conn.commit()

        except Exception as e1:
            raise Exception("Error %s when writing teams" % str(e1))
        finally:
            self.close()

    def does_team_with_name_exist(self, team_name: str):
        try:
            if self.table_does_not_exist(TEAMS_TABLE):
                return False

            cursor = self.cursor
            cursor.execute(
                """SELECT * FROM %s WHERE %s='%s' """
                % (TEAMS_TABLE, TEAM_NAME, str(team_name))
            )
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading teams" % str(e1))
        finally:
            self.close()

        return len(raw_list) > 0

    def next_available_idx(self) -> int:
        return self.last_used_idx() + 1

    def last_used_idx(self) -> int:
        try:
            if self.table_does_not_exist(TEAMS_TABLE):
                self.create_table()

            cursor = self.cursor
            statement = "SELECT MAX(%s) FROM %s" % (
                TEAM_ORDER,
                TEAMS_TABLE,
            )
            cursor.execute(statement)
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s reading teams data" % str(e1))
        finally:
            self.close()

        if len(raw_list) == 0:
            return -1
        else:
            return int(raw_list[0][0])

    def next_available_id(self) -> int:
        return self.last_used_id() + 1

    def last_used_id(self) -> int:
        try:
            if self.table_does_not_exist(TEAMS_TABLE):
                self.create_table()

            cursor = self.cursor
            statement = "SELECT MAX(%s) FROM %s" % (
                TEAM_ID,
                TEAMS_TABLE,
            )
            cursor.execute(statement)
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s reading teams data" % str(e1))
        finally:
            self.close()

        if len(raw_list) == 0:
            return -1
        else:
            return int(raw_list[0][0])

    def read(self) -> ListOfTeams:
        try:
            if self.table_does_not_exist(TEAMS_TABLE):
                return ListOfTeams.create_empty()

            cursor = self.cursor
            cursor.execute(
                """SELECT %s, %s, %s, %s FROM %s ORDER BY %s"""
                % (
                    TEAM_NAME,
                    TEAM_LOCATION,
                    PROTECTED,
                    TEAM_ID,
                    TEAMS_TABLE,
                    TEAM_ORDER,
                )
            )
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading teams" % str(e1))
        finally:
            self.close()

        new_list = [
            Team(
                name=raw_team[0],
                location_for_cadet_warning=RoleLocation[raw_team[1]],
                protected=int2bool(raw_team[2]),
                id=str(raw_team[3]),
            )
            for raw_team in raw_list
        ]

        return ListOfTeams(new_list)

    def write(self, list_of_teams: ListOfTeams):
        try:
            if self.table_does_not_exist(TEAMS_TABLE):
                self.create_table()

            self.cursor.execute("DELETE FROM %s" % (TEAMS_TABLE))

            for idx, team in enumerate(list_of_teams):
                self._add_row_without_checks_or_commits(idx=idx, team=team)

            self.conn.commit()

        except Exception as e1:
            raise Exception("Error %s when writing teams" % str(e1))
        finally:
            self.close()

    def _add_row_without_checks_or_commits(self, idx: int, team: Team):
        name = team.name
        location = team.location_for_cadet_warning.name
        protected = bool2int(team.protected)
        team_id = int(team.id)

        insertion = "INSERT INTO %s (%s, %s, %s, %s, %s) VALUES (?,?,?,?,?)" % (
            TEAMS_TABLE,
            TEAM_NAME,
            TEAM_LOCATION,
            PROTECTED,
            TEAM_ID,
            TEAM_ORDER,
        )

        self.cursor.execute(insertion, (name, location, protected, team_id, idx))

    def create_table(self):
        # name: str
        # hidden: bool
        # id: str = arg_not_passed

        table_creation_query = """
                CREATE TABLE %s (
                    %s STR, 
                    %s STR, 
                    %s INTEGER,
                    %s INTEGER,
                    %s INTEGER
                );
            """ % (
            TEAMS_TABLE,
            TEAM_NAME,
            TEAM_LOCATION,
            PROTECTED,
            TEAM_ID,
            TEAM_ORDER,
        )

        index_creation_query = "CREATE UNIQUE INDEX %s ON %s (%s)" % (
            INDEX_TEAMS_TABLE,
            TEAMS_TABLE,
            TEAM_ID,
        )

        try:
            self.cursor.execute(table_creation_query)
            self.cursor.execute(index_creation_query)
            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when creating teams table" % str(e1))
        finally:
            self.close()
