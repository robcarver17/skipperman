
from app.data_access.sql.generic_sql_data import GenericSqlData, bool2int, int2bool
from app.objects.roles_and_teams import Team, ListOfTeams, RoleLocation
from app.data_access.sql.shared_column_names import *


TEAMS_TABLE = "teams"
INDEX_TEAMS_TABLE = "index_teams_table"

class SqlDataListOfTeams(GenericSqlData):
    def read(self) -> ListOfTeams:
        try:
            if self.table_does_not_exist(TEAMS_TABLE):
                return ListOfTeams.create_empty()

            cursor = self.cursor
            cursor.execute('''SELECT %s, %s, %s, %s FROM %s ORDER BY %s''' % (
                TEAM_NAME, TEAM_LOCATION, PROTECTED, TEAM_ID, TEAMS_TABLE, TEAM_ORDER
             ))
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading teams" % str(e1))
        finally:
            self.close()

        new_list = [Team(name=raw_team[0],
                         location_for_cadet_warning = RoleLocation[raw_team[1]],
                         protected = int2bool(raw_team[2]),
                         id =str(raw_team[3]),
                         ) for raw_team in raw_list]

        return ListOfTeams(new_list)


    def write(self, list_of_teams: ListOfTeams):

        try:
            if self.table_does_not_exist(TEAMS_TABLE):
                self.create_table()

            ## NEEDS TO DELETE OLD
            ## TEMPORARY UNTIL CAN DO PROPERLY
            self.cursor.execute("DELETE FROM %s" % (TEAMS_TABLE))

            for idx, team in enumerate(list_of_teams):
                name = team.name
                location = team.location_for_cadet_warning.name
                protected = bool2int(team.protected)
                team_id = int(team.id)

                insertion = "INSERT INTO %s (%s, %s, %s, %s, %s) VALUES (?,?,?,?,?)" % (
                    TEAMS_TABLE,
                TEAM_NAME, TEAM_LOCATION, PROTECTED, TEAM_ID, TEAM_ORDER)

                self.cursor.execute(insertion, (
                    name, location, protected, team_id, idx))

            self.conn.commit()

        except Exception as e1:
            raise Exception("Error %s when writing teams" % str(e1))
        finally:
            self.close()

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
            """ % (TEAMS_TABLE,
                   TEAM_NAME, TEAM_LOCATION, PROTECTED, TEAM_ID, TEAM_ORDER)

        index_creation_query = "CREATE UNIQUE INDEX %s ON %s (%s)" % (
        INDEX_TEAMS_TABLE, TEAMS_TABLE, TEAM_ID)

        try:
            self.cursor.execute(table_creation_query)
            self.cursor.execute(index_creation_query)
            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when creating teams table" % str(e1))
        finally:
            self.close()

