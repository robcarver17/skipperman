from datetime import datetime

from app.data_access.sql.generic_sql_data import GenericSqlData, date2int, bool2int, int2date, int2bool
from app.objects.cadets import Cadet
from app.objects.committee import ListOfCadetsWithIdOnCommittee, CadetWithIdCommitteeMember
from app.data_access.sql.shared_column_names import *
from app.data_access.sql.cadets import CADETS_TABLE
from app.objects.composed.committee import ListOfCadetsOnCommittee, CadetOnCommittee
from app.objects.membership_status import MembershipStatus
from app.objects.utilities.exceptions import missing_data, MultipleMatches

CADETS_ON_COMMITTEE_TABLE ="cadets_on_committee"
INDEX_CADETS_ON_COMMITTEE_TABLE  = "index_cadets_on_committee"

class SqlDataListOfCadetsOnCommitte(GenericSqlData):

    def toggle_selection_for_cadet_committee_member(
            self, cadet_id: str
    ):

        try:
            currently_selected = self.is_cadet_selected(cadet_id)
            if currently_selected is missing_data:
                raise Exception("Can't toggle selection as not on committee")

            new_selection = not currently_selected
            insertion = "UPDATE %s SET %s=? WHERE %s=?" % (
                CADETS_ON_COMMITTEE_TABLE,
                COMMITTEE_DESLECTED,
                CADET_ID
            )

            self.cursor.execute(insertion, ( bool2int(new_selection),  int(cadet_id)))

            self.conn.commit()
        except Exception as e1:
            raise Exception(str(e1))

        finally:
            self.close()


    def add_new_cadet_to_committee(
            self,
            cadet_id: str,
            date_term_starts: datetime.date,
            date_term_ends: datetime.date,
            deselected: bool = False
    ):
        try:
            cadet_id = int(cadet_id)
            date_term_starts = date2int(date_term_starts)
            date_term_ends = date2int(date_term_ends)
            deselected = bool2int(deselected)

            insertion = "INSERT INTO %s ( %s, %s, %s, %s) VALUES ( ?,?,?,?)" % (
                CADETS_ON_COMMITTEE_TABLE,
                CADET_ID, COMMITTEE_DATE_STARTS, COMMITTEE_DATE_ENDS, COMMITTEE_DESLECTED)

            self.cursor.execute(insertion, (cadet_id, date_term_starts, date_term_ends, deselected))

            self.conn.commit()
        except Exception as e1:
            raise Exception(str(e1))

        finally:
            self.close()

    def  get_list_of_cadets_on_committee(self) -> ListOfCadetsOnCommittee:
        if self.table_does_not_exist(CADETS_ON_COMMITTEE_TABLE):
            self.create_table()

        try:
            cursor = self.cursor
            cursor.execute('''SELECT %s.%s, %s.%s, %s.%s, %s.%s, %s.%s, %s.%s, %s.%s, %s.%s FROM %s JOIN %s ON %s.%s=%s.%s''' % (
                CADETS_TABLE, CADET_FIRST_NAME,
                CADETS_TABLE, CADET_SURNAME,
                CADETS_TABLE, CADET_DOB,
                CADETS_TABLE, CADET_ID,
                CADETS_TABLE, CADET_MEMBERSHIP_STATUS,
                CADETS_ON_COMMITTEE_TABLE, COMMITTEE_DATE_STARTS,
                CADETS_ON_COMMITTEE_TABLE, COMMITTEE_DATE_ENDS,
                CADETS_ON_COMMITTEE_TABLE,COMMITTEE_DESLECTED,
                CADETS_ON_COMMITTEE_TABLE,
                CADETS_TABLE,
                CADETS_ON_COMMITTEE_TABLE, CADET_ID,
                CADETS_TABLE, CADET_ID

            ))
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s reading cadet committee data" % str(e1))
        finally:
            self.close()


        new_list = []
        id_list = []
        for raw_data in raw_list:
            cadet = Cadet(
                first_name=raw_data[0],
                surname=raw_data[1],
                date_of_birth=int2date(raw_data[2]),
                id=str(raw_data[3]),
                membership_status=MembershipStatus[raw_data[4]]
            )
            cadet_with_id_on_committee=                    CadetWithIdCommitteeMember(
                    cadet_id=str(raw_data[3]),
                    date_term_starts = int2date(raw_data[5]),
            date_term_ends = int2date(raw_data[6]),
            deselected = int2bool(raw_data[7]))

            new_list.append(
                CadetOnCommittee(
                    cadet=cadet,
                    cadet_with_id_on_committee=cadet_with_id_on_committee


                    )
                )
            id_list.append(cadet_with_id_on_committee)

        return ListOfCadetsOnCommittee(new_list, list_of_cadets_with_id_on_commitee=ListOfCadetsWithIdOnCommittee(id_list))

    def is_cadet_selected(self, cadet_id:str):
        if self.table_does_not_exist(CADETS_ON_COMMITTEE_TABLE):
            return missing_data

        try:
            cursor = self.cursor
            cursor.execute("SELECT %s FROM %s WHERE %s=%d" % (
                COMMITTEE_DESLECTED, CADETS_ON_COMMITTEE_TABLE,
                CADET_ID, int(cadet_id)
            ))
            raw_list = cursor.fetchall()
        except Exception as e1:
            raise Exception("Error %s reading cadet committee data" % str(e1))
        finally:
            self.close()

        if len(raw_list)==0:
            return missing_data
        elif len(raw_list)>1:
            raise MultipleMatches("More than one cadet with id %s on committee" % cadet_id)

        selected = int2bool(raw_list[0][0])

        return selected

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
                cadet_id = int(cadet_on_committee.cadet_id)
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
                    %s INTEGER,
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

