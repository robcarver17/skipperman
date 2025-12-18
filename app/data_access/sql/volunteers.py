from copy import copy

from app.data_access.sql.generic_sql_data import GenericSqlData
from app.data_access.sql.shared_column_names import *
from app.objects.utilities.exceptions import arg_not_passed, MissingData, MultipleMatches, missing_data
from app.objects.volunteers import ListOfVolunteers, Volunteer, SORT_BY_SURNAME, SORT_BY_FIRSTNAME

VOLUNTEERS_TABLE = "volunteers"
INDEX_VOLUNTEERS_TABLE = "index_volunteers_table"

class SqlDataListOfVolunteers(GenericSqlData):
    def delete_volunteer(
            self,
            volunteer: Volunteer,
    ):
        if self.table_does_not_exist(VOLUNTEERS_TABLE):
            return

        try:
            self.cursor.execute("DELETE FROM %s WHERE %s=%d" % (VOLUNTEERS_TABLE,
                                                                VOLUNTEER_ID,
                                                                int(volunteer.id)))
            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing volunteers" % str(e1))
        finally:
            self.close()



    def modify_volunteer(
            self,
            existing_volunteer: Volunteer,
            updated_volunteer: Volunteer,
    ):
        if self.does_matching_volunteer_exist(updated_volunteer):
            if not existing_volunteer.name == updated_volunteer.name:
                raise Exception("Volunteer %s with identical name already exists!" % str(updated_volunteer))
        try:
            first_name = updated_volunteer.first_name
            surname = updated_volunteer.surname
            existing_id = int(existing_volunteer.id)

            update = "UPDATE %s SET %s='%s', %s='%s' WHERE %s=%d" % (
                VOLUNTEERS_TABLE,
                VOLUNTEER_FIRST_NAME,first_name,
                VOLUNTEER_SURNAME,surname,
                VOLUNTEER_ID, existing_id)

            self.cursor.execute(update)

            self.conn.commit()

        except Exception as e1:
            raise e1
        finally:
            self.close()

    def add_new_volunteer(self, volunteer: Volunteer):
        if self.does_matching_volunteer_exist(volunteer):
            raise Exception("Volunteer %s with identical name already exists!" % str(volunteer))
        try:
            first_name = volunteer.first_name
            surname = volunteer.surname
            id = self.next_available_volunteer_id()

            insertion = "INSERT INTO %s ( %s, %s, %s) VALUES ( ?,?,?)" % (
VOLUNTEERS_TABLE, VOLUNTEER_FIRST_NAME, VOLUNTEER_SURNAME, VOLUNTEER_ID)

            self.cursor.execute(insertion, (first_name, surname, id))

            self.conn.commit()
        except Exception as e1:
            raise Exception("error %s when adding volunteer %s to table" % (str(e1), volunteer))
        finally:
            self.close()

    def next_available_volunteer_id(self) ->int:
        return self.last_used_volunteer_id()+1

    def last_used_volunteer_id(self)-> int:
        try:
            if self.table_does_not_exist(VOLUNTEERS_TABLE):
                self.create_table()

            cursor = self.cursor
            statement = "SELECT MAX(%s) FROM %s" % (
                VOLUNTEER_ID,
                VOLUNTEERS_TABLE,
            )
            cursor.execute(statement)
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s reading volunteer data" % str(e1))
        finally:
            self.close()

        if len(raw_list) == 0:
            return -1
        else:
            return int(raw_list[0][0])


    def does_matching_volunteer_exist(self, volunteer: Volunteer):
        try:
            id = self.get_id_of_matching_volunteer(volunteer, default=missing_data)
            if id is missing_data:
                return False
            else:
                return True
        except MultipleMatches:
            return True
        except Exception as e:
            raise Exception("Couldn't check for matching volunteer %s error %s" % (str(volunteer), str(e)))

    def get_matching_volunteer(self, volunteer: Volunteer, default=missing_data):
        ## matches everything except id
        volunteer_id = self.get_id_of_matching_volunteer(volunteer, default=missing_data)
        if volunteer_id is missing_data:
            return volunteer_id

        new_volunteer= copy(volunteer)
        new_volunteer.id = volunteer_id

        return new_volunteer


    def get_id_of_matching_volunteer(self, volunteer: Volunteer, default=missing_data):
        ## matches everything except id
        try:
            if self.table_does_not_exist(VOLUNTEERS_TABLE):
                return default

            cursor = self.cursor
            statement = "SELECT %s FROM %s WHERE %s=? AND %s=?" % (
                VOLUNTEER_ID,
                VOLUNTEERS_TABLE,
                VOLUNTEER_FIRST_NAME,
                VOLUNTEER_SURNAME
            )
            cursor.execute(statement, (volunteer.first_name, volunteer.surname))
            raw_list = cursor.fetchall()

        except Exception as e1:
            raise Exception("Error %s reading volunteer data" % str(e1))
        finally:
            self.close()

        if len(raw_list) == 0:
            return default
        elif len(raw_list)>1:
            raise MultipleMatches("More than one volunteer matches %s in data!" % str(volunteer))
        else:
            return str(raw_list[0][0])


    def get_volunteer_from_id(self, volunteer_id: str) -> Volunteer:
        if self.table_does_not_exist(VOLUNTEERS_TABLE):
            raise MissingData("No volunteer matches %s" % volunteer_id)

        try:
            cursor = self.cursor
            statement = "SELECT %s, %s FROM %s WHERE %s=%d" % (
                VOLUNTEER_FIRST_NAME, VOLUNTEER_SURNAME,
                VOLUNTEERS_TABLE,
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
            raise MissingData("No volunteer matches %s" % volunteer_id)
        elif len(raw_list)>1:
            raise MultipleMatches("More than one volunteer has id %s" % volunteer_id)

        raw_volunteer = raw_list[0]
        volunteer = Volunteer(
            first_name= str(raw_volunteer[0]),
            surname=str(raw_volunteer[1]),
            id= volunteer_id)

        return volunteer

    def read(self, sort_by: str = arg_not_passed, exclude_volunteer: Volunteer = arg_not_passed) -> ListOfVolunteers:
        if self.table_does_not_exist(VOLUNTEERS_TABLE):
            return ListOfVolunteers.create_empty()

        try:
            sort_clause = get_sort_clause(sort_by)
            exclude_clause = get_exclude_clause(exclude_volunteer)
            cursor = self.cursor
            statement = "SELECT %s, %s, %s FROM %s %s %s" % (
                VOLUNTEER_FIRST_NAME, VOLUNTEER_SURNAME, VOLUNTEER_ID,
                VOLUNTEERS_TABLE,
                sort_clause, exclude_clause
            )
            cursor.execute(statement)
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s reading volunteer data" % str(e1))
        finally:
            self.close()

        new_list = []
        for raw_volunteer in raw_list:
            volunteer = Volunteer(
                first_name= str(raw_volunteer[0]),
                surname=str(raw_volunteer[1]),
                id= str(raw_volunteer[2]))

            new_list.append(volunteer)

        return ListOfVolunteers(new_list)

    def write(self, list_of_volunteers: ListOfVolunteers):
        try:
            if self.table_does_not_exist(VOLUNTEERS_TABLE):
                self.create_table()

            ## NEEDS TO DELETE OLD
            ## TEMPORARY UNTIL CAN DO PROPERLY
            self.cursor.execute("DELETE FROM %s" % (VOLUNTEERS_TABLE))

            for volunteer in list_of_volunteers:
                first_name = volunteer.first_name
                surname = volunteer.surname
                id = int(volunteer.id)
                insertion = "INSERT INTO %s (%s, %s, %s) VALUES (?,?,?)" % (
                    VOLUNTEERS_TABLE,
                VOLUNTEER_FIRST_NAME, VOLUNTEER_SURNAME, VOLUNTEER_ID)

                self.cursor.execute(insertion, (
                    first_name, surname, id))

            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing volunteers" % str(e1))
        finally:
            self.close()

    def create_table(self):

        table_creation_query = """
            CREATE TABLE %s (
                %s STR, 
                %s STR,
                %s INTEGER
            );
        """ % (VOLUNTEERS_TABLE,
               VOLUNTEER_FIRST_NAME, VOLUNTEER_SURNAME, VOLUNTEER_ID)

        index_creation_query = "CREATE UNIQUE INDEX %s ON %s (%s)" % (INDEX_VOLUNTEERS_TABLE, VOLUNTEERS_TABLE, VOLUNTEER_ID)

        try:
            self.cursor.execute(table_creation_query)
            self.cursor.execute(index_creation_query)
            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s creating volunteers table" % str(e1))
        finally:
            self.close()



def get_sort_clause(sort_by: str):
    if sort_by == SORT_BY_SURNAME:
        return "ORDER BY %s" % VOLUNTEER_SURNAME
    elif sort_by == SORT_BY_FIRSTNAME:
        return "ORDER BY %s" % VOLUNTEER_FIRST_NAME
    else:
        return ""

def get_exclude_clause(exclude_volunteer: Volunteer = arg_not_passed):
    if exclude_volunteer is arg_not_passed:
        return ""
    else:
        return "WHERE %s IS NOT '%d'" % (VOLUNTEER_ID, int(exclude_volunteer.id))

