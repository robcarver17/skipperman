from copy import copy

from app.data_access.sql.generic_sql_data import GenericSqlData,  int2date, date2int
from app.data_access.sql.shared_column_names import *
from app.objects.cadets import ListOfCadets, Cadet, permanent_skip_cadet_id, permanent_skip_cadet, \
    temporary_skip_cadet_id, temporary_skip_cadet
from app.objects.membership_status import MembershipStatus
from app.objects.utilities.cadet_matching_and_sorting import SORT_BY_SURNAME, SORT_BY_FIRSTNAME, SORT_BY_DOB_ASC, \
    SORT_BY_DOB_DSC
from app.objects.utilities.exceptions import arg_not_passed, missing_data, MultipleMatches, MissingData

### GROUPS
CADETS_TABLE = "cadets_table"
INDEX_NAME_CADETS_TABLE = "cadet_id_index"


class SqlDataListOfCadets(GenericSqlData):
    def delete_cadet(self, cadet: Cadet):
        matching_cadet =self.get_cadet_from_id(cadet.id, default=missing_data)
        if matching_cadet is missing_data:
            raise MissingData("Can't delete cadet %s as doesn't exist" % cadet)

        try:
            insertion = "DELETE FROM %s WHERE %s=?" % (
                CADETS_TABLE,
                 CADET_ID)

            self.cursor.execute(insertion, (int(cadet.id)))

            self.conn.commit()
        except Exception as e1:
            raise Exception("error %s when deleting %s" % (str(e1), cadet))
        finally:
            self.close()

    def add_cadet(self, new_cadet: Cadet):
        if self.does_matching_cadet_exist(new_cadet):
            raise Exception("Cadet exactly matching %s name/dob already exists!" % str(new_cadet))
        try:
            name = new_cadet.first_name
            surname = new_cadet.surname
            dob = date2int(new_cadet.date_of_birth)
            status = new_cadet.membership_status.name
            id = self.next_available_cadet_id()

            insertion = "INSERT INTO %s ( %s, %s, %s, %s, %s) VALUES ( ?,?,?,?,?)" % (
                CADETS_TABLE,
            CADET_FIRST_NAME, CADET_SURNAME, CADET_DOB, CADET_MEMBERSHIP_STATUS, CADET_ID)

            self.cursor.execute(insertion, (name, surname, dob, status, id))

            self.conn.commit()
        except Exception as e1:
            raise Exception("error %s when adding cadet %s to table" % (str(e1), new_cadet))
        finally:
            self.close()

    def next_available_cadet_id(self) ->int:
        return self.last_used_cadet_id()+1

    def last_used_cadet_id(self)-> int:
        try:
            if self.table_does_not_exist(CADETS_TABLE):
                self.create_table()

            cursor = self.cursor
            statement = "SELECT MAX(%s) FROM %s" % (
                CADET_ID,
                CADETS_TABLE,
            )
            cursor.execute(statement)
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s reading cadet data" % str(e1))
        finally:
            self.close()

        if len(raw_list) == 0:
            return -1
        else:
            return int(raw_list[0][0])


    def does_matching_cadet_exist(self, cadet: Cadet):
        try:
            id = self.get_id_of_matching_cadet(cadet, default=missing_data)
            if id is missing_data:
                return False
            else:
                return True
        except MultipleMatches:
            return True
        except Exception as e:
            raise Exception("Couldn't check for matching cadet %s error %s" % (str(cadet), str(e)))

    def get_matching_cadet(self, cadet: Cadet):
        ## matches everything except id
        cadet_id = self.get_id_of_matching_cadet(cadet, default=missing_data)
        if cadet_id is missing_data:
            raise MissingData("Cadet matching %s not found")

        new_cadet= copy(cadet)
        new_cadet.id = cadet_id

        return new_cadet


    def get_id_of_matching_cadet(self, cadet: Cadet, default=missing_data):
        ## matches everything except id
        try:
            if self.table_does_not_exist(CADETS_TABLE):
                self.create_table()

            cursor = self.cursor
            statement = "SELECT %s FROM %s WHERE %s=? AND %s=? AND %s=?" % (
                CADET_ID,
                CADETS_TABLE,
                CADET_FIRST_NAME,
                CADET_SURNAME,
                CADET_DOB
            )
            cursor.execute(statement, (cadet.first_name, cadet.surname, date2int(cadet.date_of_birth)))
            raw_list = cursor.fetchall()

        except Exception as e1:
            raise Exception("Error %s reading cadet data" % str(e1))
        finally:
            self.close()

        if len(raw_list) == 0:
            return default
        elif len(raw_list)>1:
            raise MultipleMatches("More than one cadet matches %s in data!" % str(cadet))
        else:
            return str(raw_list[0][0])

    def get_cadet_from_id(self, cadet_id: str, default = missing_data) -> Cadet:
        if cadet_id == permanent_skip_cadet_id:
            return permanent_skip_cadet
        elif cadet_id == temporary_skip_cadet_id:
            return temporary_skip_cadet
        if self.table_does_not_exist(CADETS_TABLE):
            return missing_data
        try:
            cursor = self.cursor
            statement = "SELECT %s, %s, %s, %s FROM %s WHERE %s=%d" % (
                CADET_FIRST_NAME, CADET_SURNAME, CADET_DOB, CADET_MEMBERSHIP_STATUS,
                CADETS_TABLE, CADET_ID, int(cadet_id)
            )
            cursor.execute(statement)
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s reading cadet data" % str(e1))
        finally:
            self.close()

        if len(raw_list) == 0:
            return default
        elif len(raw_list)>1:
            raise MultipleMatches("More than one cadet matches %s in data!" % cadet_id)

        raw_cadet = raw_list[0]
        cadet= Cadet(
            first_name= str(raw_cadet[0]),
            surname=str(raw_cadet[1]),
            date_of_birth= int2date(raw_cadet[2]),
            membership_status= MembershipStatus[raw_cadet[3]],
            id= cadet_id)

        return cadet

    def read(self, sort_by: str =arg_not_passed, exclude_cadet: Cadet = arg_not_passed) -> ListOfCadets:
        if self.table_does_not_exist(CADETS_TABLE):
            return ListOfCadets([])

        try:
            sort_clause = get_sort_clause(sort_by)
            exclude_clause = get_exclude_clause(exclude_cadet)
            cursor = self.cursor
            statement = "SELECT %s, %s, %s, %s, %s FROM %s %s %s" % (
                CADET_FIRST_NAME, CADET_SURNAME, CADET_DOB, CADET_MEMBERSHIP_STATUS, CADET_ID,
                CADETS_TABLE, sort_clause, exclude_clause
            )
            cursor.execute(statement)
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s reading cadet data" % str(e1))
        finally:
            self.close()

        if len(raw_list) == 0:
            return ListOfCadets.create_empty()

        new_list = []
        for raw_cadet in raw_list:
            cadet= Cadet(
                first_name= str(raw_cadet[0]),
                surname=str(raw_cadet[1]),
                date_of_birth= int2date(raw_cadet[2]),
                membership_status= MembershipStatus[raw_cadet[3]],
                id= str(raw_cadet[4]))

            new_list.append(cadet)

        return ListOfCadets(new_list)

    def modify_cadet(self, existing_cadet: Cadet, new_cadet: Cadet):
        try:
            name = new_cadet.first_name
            surname = new_cadet.surname
            dob = date2int(new_cadet.date_of_birth)
            status = new_cadet.membership_status.name
            id = int(existing_cadet.id)

            update = "UPDATE %s SET %s=?, %s=?, %s=?, %s=? WHERE %s=?" % (
                CADETS_TABLE,
                CADET_FIRST_NAME, CADET_SURNAME, CADET_DOB, CADET_MEMBERSHIP_STATUS, CADET_ID)
            self.cursor.execute(update, (name, surname, dob, status, id))
            self.conn.commit()

        except Exception as e1:
            raise Exception("error %s when modifying cadet" % str(e1))
        finally:
            self.close()


    def write(
            self, list_of_cadets: ListOfCadets
    ):
        try:
            if self.table_does_not_exist(CADETS_TABLE):
                self.create_table()

            ## NEEDS TO DELETE OLD
            ## TEMPORARY UNTIL CAN DO PROPERLY
            self.cursor.execute("DELETE FROM %s" % (CADETS_TABLE))

            for cadet in list_of_cadets:
                name = cadet.first_name
                surname = cadet.surname
                dob = date2int(cadet.date_of_birth)
                status = cadet.membership_status.name
                id = int(cadet.id)

                insertion = "INSERT INTO %s ( %s, %s, %s, %s, %s) VALUES ( ?,?,?,?,?)" % (
                    CADETS_TABLE,
                CADET_FIRST_NAME, CADET_SURNAME, CADET_DOB, CADET_MEMBERSHIP_STATUS, CADET_ID)

                self.cursor.execute(insertion, (name, surname, dob, status, id))

            self.conn.commit()
        except Exception as e1:
            raise Exception("error %s when writing cadets table" % str(e1))
        finally:
            self.close()

    def create_table(self):

        table_creation_query = """
            CREATE TABLE %s (
                %s STR, 
                %s STR,
                %s INTEGER,
                %s STR,
                %s INTEGER
            );
        """ % (CADETS_TABLE,
               CADET_FIRST_NAME, CADET_SURNAME, CADET_DOB, CADET_MEMBERSHIP_STATUS, CADET_ID)

        index_creation_query = "CREATE UNIQUE INDEX %s ON %s (%s)" % (INDEX_NAME_CADETS_TABLE, CADETS_TABLE, CADET_ID)

        try:
            self.cursor.execute(table_creation_query)
            self.cursor.execute(index_creation_query)
            self.conn.commit()
        except Exception as e1:
            raise "Error %s creating cadets table" % str(e1)
        finally:
            self.close()

def get_sort_clause(sort_by: str = arg_not_passed):
    if sort_by == SORT_BY_SURNAME:
        return "ORDER BY %s" % CADET_SURNAME
    elif sort_by == SORT_BY_FIRSTNAME:
        return "ORDER BY %s" % CADET_FIRST_NAME
    elif sort_by == SORT_BY_DOB_ASC:
        return "ORDER BY %s" % CADET_DOB
    elif sort_by == SORT_BY_DOB_DSC:
        return "ORDER BY %s DESC" % CADET_DOB
    else:
        return ""

def get_exclude_clause(exclude_cadet: Cadet = arg_not_passed):
    if exclude_cadet is arg_not_passed:
        return ""
    else:
        return "WHERE %s IS NOT '%d'" % (CADET_ID, int(exclude_cadet.id))

