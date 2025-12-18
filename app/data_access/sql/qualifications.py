import pandas as pd

from app.data_access.sql.generic_sql_data import GenericSqlData
from app.data_access.sql.shared_column_names import *
from app.objects.cadets import Cadet
from app.objects.composed.cadets_with_qualifications import QualificationsForCadet, QualificationAndDate

from app.objects.qualifications import (
    ListOfQualifications, Qualification,
)

QUALIFICATION_TABLE = "qualifications_table"
INDEX_NAME_QUALIFICATION_TABLE = "qual_id"

class SqlDataListOfQualifications(GenericSqlData):


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
                name = qualification.name
                id = int(qualification.id)

                insertion = "INSERT INTO %s (%s, %s, %s) VALUES (?,?,?)" % (
                    QUALIFICATION_TABLE,
                    QUALIFICATION_NAME, QUALIFICATION_ID, QUALIFICATION_ORDER)

                self.cursor.execute(insertion, (
                    name, id, idx))

            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing qualifications" % str(e1))
        finally:
            self.close()

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
