from app.data_access.sql.generic_sql_data import GenericSqlData, date2int, bool2int, int2date, int2bool
from app.objects.committee import ListOfCadetsWithIdOnCommittee, CadetWithIdCommitteeMember
from app.data_access.sql.shared_column_names import *

CADETS_ON_COMMITTEE_TABLE ="cadets_on_committee"
INDEX_CADETS_ON_COMMITTEE_TABLE  = "index_cadets_on_committee"

class SqlDataListOfCadetsOnCommitte(GenericSqlData):
    def read(self) -> ListOfCadetsWithIdOnCommittee:
        if self.table_does_not_exist(CADETS_ON_COMMITTEE_TABLE):
            self.create_table()

        try:
            cursor = self.cursor
            cursor.execute('''SELECT %s, %s, %s, %s FROM %s ''' % (
                CADET_ID, COMMITTEE_DATE_STARTS, COMMITTEE_DATE_ENDS, COMMITTEE_DESLECTED, CADETS_ON_COMMITTEE_TABLE
            ))
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise "Error %s reading cadet committee data" % str(e1)
        finally:
            self.close()

        if len(raw_list) == 0:
            return ListOfCadetsWithIdOnCommittee.create_empty()

        new_list = []
        for raw_data in raw_list:
            new_list.append(
                CadetWithIdCommitteeMember(
                    cadet_id=str(raw_data[0]),
                    date_term_starts = int2date(raw_data[1]),
            date_term_ends = int2date(raw_data[2]),
            deselected = int2bool(raw_data[3])
                )
            )

        return ListOfCadetsWithIdOnCommittee(new_list)


    def write(self, list_of_cadets: ListOfCadetsWithIdOnCommittee):
        try:
            if self.table_does_not_exist(CADETS_ON_COMMITTEE_TABLE):
                self.create_table()

            ## NEEDS TO DELETE OLD
            ## TEMPORARY UNTIL CAN DO PROPERLY
            self.cursor.execute("DELETE FROM %s" % CADETS_ON_COMMITTEE_TABLE)

            for cadet_on_committee in list_of_cadets:
                cadet_id = str(cadet_on_committee.cadet_id)
                date_term_starts = date2int(cadet_on_committee.date_term_starts)
                date_term_ends = date2int(cadet_on_committee.date_term_ends)
                deselected = bool2int(cadet_on_committee.deselected)

                insertion = "INSERT INTO %s ( %s, %s, %s, %s) VALUES ( ?,?,?,?)" % (
                CADETS_ON_COMMITTEE_TABLE,
                CADET_ID, COMMITTEE_DATE_STARTS, COMMITTEE_DATE_ENDS, COMMITTEE_DESLECTED)

                self.cursor.execute(insertion, (cadet_id, date_term_starts ,date_term_ends, deselected))

            self.conn.commit()
        except Exception as e1:
            raise Exception("error %s when writing cadets committee table" % str(e1))
        finally:
            self.close()


    def create_table(self):

        table_creation_query = """
                CREATE TABLE %s (
                    %s STR, 
                    %s INTEGER,
                    %s INTEGER,
                    %s INTEGER
                );
            """ % (CADETS_ON_COMMITTEE_TABLE,
                   CADET_ID, COMMITTEE_DATE_STARTS, COMMITTEE_DATE_ENDS, COMMITTEE_DESLECTED
                   )

        index_creation_query = "CREATE UNIQUE INDEX %s ON %s (%s)" % (INDEX_CADETS_ON_COMMITTEE_TABLE, CADETS_ON_COMMITTEE_TABLE,
                                                                      CADET_ID)

        try:
            self.cursor.execute(table_creation_query)
            self.cursor.execute(index_creation_query)
            self.conn.commit()
        except Exception as e1:
            raise "Error %s creating cadets committee table" % str(e1)
        finally:
            self.close()

