import pandas as pd

from app.data_access.sql.generic_sql_data import GenericSqlData, bool2int, int2bool, int2date, date2int
from app.data_access.sql.shared_column_names import *
from app.objects.cadets import ListOfCadets, Cadet

### GROUPS
CADETS_TABLE = "cadets_table"
INDEX_NAME_CADETS_TABLE = "cadet_id_index"


class SqlDataListOfCadets(GenericSqlData):
    def read(self) -> ListOfCadets:
        if self.table_does_not_exist(CADETS_TABLE):
            self.create_table()

        try:
            cursor = self.cursor
            cursor.execute('''SELECT %s, %s, %s, %s, %s FROM %s ''' % (
                CADET_FIRST_NAME, CADET_SURNAME, CADET_DOB, CADET_MEMBERSHIP_STATUS, CADET_ID,
                CADETS_TABLE
            ))
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise "Error %s reading cadet data" % str(e1)
        finally:
            self.close()

        if len(raw_list) == 0:
            return ListOfCadets.create_empty()

        raw_dict = {
            'first_name': [ans[0] for ans in raw_list],
            'surname': [ans[1] for ans in raw_list],
            'date_of_birth': [int2date(ans[2]) for ans in raw_list],
            'membership_status': [ans[3] for ans in raw_list],
            'id': [ans[4] for ans in raw_list],
        }

        df = pd.DataFrame(raw_dict)

        return ListOfCadets.from_df_of_str(df)

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
                id = cadet.id

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
                %s STR
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
