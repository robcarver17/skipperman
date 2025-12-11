import pandas as pd

from app.data_access.sql.generic_sql_data import GenericSqlData, date2int, int2date
from app.data_access.sql.shared_column_names import *

from app.objects.qualifications import (
    ListOfQualifications,
    ListOfCadetsWithIdsAndQualifications,
)

QUALIFICATION_TABLE = "qualifications_table"
INDEX_NAME_QUALIFICATION_TABLE = "qual_id"

class SqlDataListOfQualifications(GenericSqlData):
    def read(self) -> ListOfQualifications:
        try:
            if self.table_does_not_exist(QUALIFICATION_TABLE):
                self.create_table()

            cursor = self.cursor
            cursor.execute('''SELECT %s, %s FROM %s ORDER BY %s''' % (
                QUALIFICATION_NAME, QUALIFICATION_ID, QUALIFICATION_TABLE, QUALIFICATION_ORDER
            ))
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading qualifications" % str(e1))
        finally:
            self.close()

        if len(raw_list) == 0:
            return ListOfQualifications.create_empty()

        raw_dict = {
            'name': [ans[0] for ans in raw_list],
            'id': [str(ans[1]) for ans in raw_list],
        }

        df = pd.DataFrame(raw_dict)

        return ListOfQualifications.from_df_of_str(df)

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
                id = str(qualification.id)

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
                %s STR,
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

"""
class Qualification(GenericSkipperManObjectWithIds):
    name: str
    id: str = arg_not_passed
"""

CADETS_WITH_QUALIFICATION_TABLE = "cadets_with_qualifications_table"
INDEX_NAME_CADETS_WITH_QUALIFICATION_TABLE = "cadets_with_qualifications_id"

class SqlListOfCadetsWithQualifications(
    GenericSqlData
):
    def read(self) -> ListOfCadetsWithIdsAndQualifications:
        if self.table_does_not_exist(CADETS_WITH_QUALIFICATION_TABLE):
            self.create_table()

        try:
            cursor = self.cursor
            cursor.execute('''SELECT %s, %s, %s, %s FROM %s  ''' % (
                CADET_ID, QUALIFICATION_ID, QUALIFICATION_DATE, AWARDED_BY, CADETS_WITH_QUALIFICATION_TABLE
            ))
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s when reading cadets with qualifications" % str(e1))
        finally:
            self.close()

        if len(raw_list)==0:
            return ListOfCadetsWithIdsAndQualifications.create_empty()

        raw_dict = {
            'cadet_id': [str(ans[0]) for ans in raw_list],
            'qualification_id': [str(ans[1]) for ans in raw_list],
            'date': [int2date(ans[2]) for ans in raw_list],
            'awarded_by': [str(ans[3]) for ans in raw_list],
        }

        df = pd.DataFrame(raw_dict)

        return ListOfCadetsWithIdsAndQualifications.from_df_of_str(df)

    def delete_table(self):
        self.conn.execute("DROP TABLE %s" % CADETS_WITH_QUALIFICATION_TABLE)
        self.conn.commit()
        self.close()

    def write(
        self, list_of_cadets_with_qualifications: ListOfCadetsWithIdsAndQualifications
    ):
        try:
            if self.table_does_not_exist(CADETS_WITH_QUALIFICATION_TABLE):
                self.create_table()

            ## NEEDS TO DELETE OLD
            ## TEMPORARY UNTIL CAN DO PROPERLY
            self.cursor.execute("DELETE FROM %s" % (CADETS_WITH_QUALIFICATION_TABLE))

            for cadet_with_qualifications in list_of_cadets_with_qualifications:
                cadet_id = str(cadet_with_qualifications.cadet_id)
                qualification_id =str(cadet_with_qualifications.qualification_id)
                qualification_date = date2int(cadet_with_qualifications.date)
                awarded_by = str(cadet_with_qualifications.awarded_by)

                insertion = "INSERT INTO %s (%s, %s, %s, %s) VALUES (?, ?,?,?)" % (
                    CADETS_WITH_QUALIFICATION_TABLE,
                    CADET_ID, QUALIFICATION_ID, QUALIFICATION_DATE, AWARDED_BY
                )
                self.cursor.execute(insertion,
                                    (cadet_id, qualification_id, qualification_date, awarded_by))

            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when writing to cadet with qualifications table" % str(e1))
        finally:
            self.close()

    def create_table(self):
        table_creation_query = """
            CREATE TABLE %s (
                %s STR, 
                %s STR,
                %s INTEGER,
                %s STR
            );
        """ % (CADETS_WITH_QUALIFICATION_TABLE, CADET_ID, QUALIFICATION_ID, QUALIFICATION_DATE, AWARDED_BY)

        index_creation_query = "CREATE UNIQUE INDEX %s ON %s (%s, %s)" % (INDEX_NAME_CADETS_WITH_QUALIFICATION_TABLE,
                                                                              CADETS_WITH_QUALIFICATION_TABLE,
                                                                              CADET_ID, QUALIFICATION_ID)
        try:
            self.cursor.execute(table_creation_query)
            self.cursor.execute(index_creation_query)
            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when creating cadets with qualification table" % str(e1))


