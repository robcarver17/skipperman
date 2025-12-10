from app.data_access.csv.generic_csv_data import GenericCsvData

from app.data_access.csv.resolve_paths_and_filenames import (
    LIST_OF_DINGHIES_FILE_ID,
    LIST_OF_CADETS_WITH_DINGHIES_AT_EVENT_FILE_ID,
)
from app.objects.boat_classes import ListOfBoatClasses
from app.objects.cadet_at_event_with_boat_class_and_partners_with_ids import (
    ListOfCadetAtEventWithBoatClassAndPartnerWithIds,
)
from app.data_access.sql.generic_sql_data import GenericSqlData
from app.data_access.sql.shared_column_names import *

DINGHIES_TABLE = "dinghies_table"
INDEX_NAME_DINGHIES_TABLE = "dinghies_table_index"

class SqlDataListOfDinghies(GenericSqlData):


    def read(self) -> ListOfBoatClasses:
        pass

    def write(self, list_of_boats: ListOfBoatClasses):
        pass

    def create_table(self):

        #name: str
        #hidden: bool
        #id: str = arg_not_passed

        table_creation_query = """
            CREATE TABLE %s (
                %s STR, 
                %s INTEGER,
                %s STR,
                %s INTEGER
            );
        """ % (DINGHIES_TABLE,
                DINGHY_NAME, HIDDEN, DINGHY_ID, DINGHY_ORDER)

        index_creation_query = "CREATE UNIQUE INDEX %s ON %s (%s)" % (INDEX_NAME_DINGHIES_TABLE, DINGHIES_TABLE, DINGHY_ID)

        try:
            self.cursor.execute(table_creation_query)
            self.cursor.execute(index_creation_query)
            self.conn.commit()
        except Exception as e1:
            raise Exception("Error %s when creating groups table" % str(e1))
        finally:
            self.close()


"""
CADETS AT EVENT WITH DINGHIES
"""

CADETS_AND_DINGHIES_TABLE = "cadets_and_dinghies_table"
INDEX_NAME_CADETS_AND_DINGHIES_TABLE = "cadets_and_dinghies_table_index"

class SqlDataListOfCadetAtEventWithDinghies(
    GenericSqlData
):
    def read(self, event_id: str) -> ListOfCadetAtEventWithBoatClassAndPartnerWithIds:
        pass

    def write(
        self,
        people_and_boats: ListOfCadetAtEventWithBoatClassAndPartnerWithIds,
        event_id: str,
    ):
        pass

