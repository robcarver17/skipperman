
from app.data_access.sql.generic_sql_data import GenericSqlData
from app.data_access.sql.shared_column_names import *

from app.objects.qualifications import (
    ListOfQualifications, Qualification,
)
from app.objects.utilities.exceptions import arg_not_passed, MissingData, MultipleMatches, missing_data

QUALIFICATION_TABLE = "qualifications_table"
INDEX_NAME_QUALIFICATION_TABLE = "qual_id"

class SqlDataListOfQualifications(GenericSqlData):

    def add_qualification(
           self, qualification_name: str
    ):
        if self.does_qualification_with_name_exist(qualification_name):
            raise Exception("Can't add %s as already exists" % qualification_name)

        new_qualification = Qualification(name=qualification_name, id=str(self.next_available_id()))
        next_idx = self.next_available_order()
        try:
            if self.table_does_not_exist(QUALIFICATION_TABLE):
                self.create_table()

            self.add_qualification_without_check_or_commit(qualification=new_qualification, idx=next_idx)

            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing data" % str(e1))
        finally:
            self.close()

    def modify_qualification(
            self, existing_qualification_id: str, updated_qualification: Qualification
    ):
        existing_item = self.get_qualification_with_id(existing_qualification_id, default=missing_data)
        if existing_item is missing_data:
            raise Exception("Can't modify non existent item with id %s" % existing_qualification_id)

        if existing_item==updated_qualification:
            return

        if self.does_qualification_with_name_exist(updated_qualification.name):
            raise Exception("Cannot change name from %s to %s as an item with that name already exists for this qualification" % (existing_item.name, updated_qualification.name))

        self._modify_qualification_without_checks(existing_qualification_id=existing_qualification_id, updated_qualification=updated_qualification)


    def _modify_qualification_without_checks(
            self,
            existing_qualification_id: str, updated_qualification: Qualification
    ):
        try:
            if self.table_does_not_exist(QUALIFICATION_TABLE):
                self.create_table()

            insertion = "UPDATE %s SET %s='%s' WHERE %s='%s' " % (
                    QUALIFICATION_TABLE,
                QUALIFICATION_NAME,
                updated_qualification.name,
                QUALIFICATION_ID,
                int(existing_qualification_id)
                    )

            self.cursor.execute(insertion)

            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing data" % str(e1))
        finally:
            self.close()

    def get_qualification_with_id(self, qualification_id: str, default=arg_not_passed):
        try:
            if self.table_does_not_exist(QUALIFICATION_TABLE):
                if default is arg_not_passed:
                    raise MissingData("%s not found" % qualification_id)
                else:
                    return default

            cursor = self.cursor
            cursor.execute('''SELECT  %s FROM %s WHERE %s='%s' ''' % (
                QUALIFICATION_NAME, QUALIFICATION_TABLE, QUALIFICATION_ID,
                 int(qualification_id)
            ))

            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading data" % str(e1))
        finally:
            self.close()

        if len(raw_list)==0:
            if default is arg_not_passed:
                raise MissingData("%s not found" % qualification_id)
            else:
                return default
        elif len(raw_list)>1:
            raise MultipleMatches("More than one %s matches" % qualification_id)

        raw_item = raw_list[0]

        return Qualification(name=str(raw_item[0]), id=qualification_id)

    def does_qualification_with_name_exist(self, qualification_name: str):
        try:
            if self.table_does_not_exist(QUALIFICATION_TABLE):
                return False
            cursor = self.cursor
            cursor.execute('''SELECT * FROM %s WHERE %s='%s' ''' % (
                QUALIFICATION_TABLE,
                QUALIFICATION_NAME,
                str(qualification_name)
            ))

            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading" % str(e1))
        finally:
            self.close()

        return len(raw_list)>0

    def next_available_id(self) ->int:
        return self.last_used_id()+1

    def last_used_id(self)-> int:
        try:
            if self.table_does_not_exist(QUALIFICATION_TABLE):
                self.create_table()

            cursor = self.cursor
            statement = "SELECT MAX(%s) FROM %s" % (
                QUALIFICATION_ID,
                QUALIFICATION_TABLE
            )
            cursor.execute(statement)
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s reading data" % str(e1))
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
            if self.table_does_not_exist(QUALIFICATION_TABLE):
                self.create_table()

            cursor = self.cursor
            statement = "SELECT MAX(%s) FROM %s" % (
                QUALIFICATION_ORDER,
                QUALIFICATION_TABLE
            )
            cursor.execute(statement)
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s reading dinghy data" % str(e1))
        finally:
            self.close()

        if len(raw_list) == 0:
            return -1
        else:
            return int(raw_list[0][0])


    def read(self) -> ListOfQualifications:
        if self.table_does_not_exist(QUALIFICATION_TABLE):
            return ListOfQualifications.create_empty()

        try:

            cursor = self.cursor
            cursor.execute('''SELECT %s, %s FROM %s ORDER BY %s''' % (
                QUALIFICATION_NAME, QUALIFICATION_ID, QUALIFICATION_TABLE, QUALIFICATION_ORDER
            ))
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading qualifications" % str(e1))
        finally:
            self.close()

        new_list = [
            Qualification(
                name =raw_qualification[0],
                id=str(raw_qualification[1])
            ) for raw_qualification in raw_list
        ]

        return ListOfQualifications(new_list)

    def delete_table(self):
        self.conn.execute("DROP TABLE %s" % QUALIFICATION_TABLE)
        self.conn.commit()
        self.close()


    def write(self, list_of_qualifications: ListOfQualifications):
        try:
            if self.table_does_not_exist(QUALIFICATION_TABLE):
                self.create_table()

            ## NEEDS TO DELETE OLD
            ## TEMPORARY UNTIL CAN DO PROPERLY
            self.cursor.execute("DELETE FROM %s" % (QUALIFICATION_TABLE))

            for idx, qualification in enumerate(list_of_qualifications):
                self.add_qualification_without_check_or_commit(
                    qualification=qualification,
                    idx=idx
                )

            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing qualifications" % str(e1))
        finally:
            self.close()

    def add_qualification_without_check_or_commit(self, qualification: Qualification, idx: int):
        name = qualification.name
        id = int(qualification.id)

        insertion = "INSERT INTO %s (%s, %s, %s) VALUES (?,?,?)" % (
            QUALIFICATION_TABLE,
            QUALIFICATION_NAME, QUALIFICATION_ID, QUALIFICATION_ORDER)

        self.cursor.execute(insertion, (
            name, id, idx))

    def create_table(self):

        table_creation_query = """
            CREATE TABLE %s (
                %s STR, 
                %s INTEGER,
                %s INTEGER
            );
        """ % (QUALIFICATION_TABLE, QUALIFICATION_NAME, QUALIFICATION_ID, QUALIFICATION_ORDER
                )

        index_creation_query = "CREATE UNIQUE INDEX %s ON %s (%s)" % (INDEX_NAME_QUALIFICATION_TABLE, QUALIFICATION_TABLE, QUALIFICATION_ID)

        try:
            self.cursor.execute(table_creation_query)
            self.cursor.execute(index_creation_query)
            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when creating qualifications table" % str(e1))
        finally:
            self.close()
