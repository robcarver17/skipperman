from app.data_access.csv.generic_csv_data import GenericCsvData

from app.data_access.classes.resources import *
from app.data_access.resolve_paths_and_filenames import (
    CLUB_BOAT_LIMIT,
)


class ParquetDataListOfClubDinghyLimits(GenericCsvData,  DataListOfClubDinghyLimits):
    def read(self) -> ListOfClubDinghyLimits:
        list_of_boats = self.read_and_return_object_of_type(
            ListOfClubDinghyLimits, file_identifier=CLUB_BOAT_LIMIT
        )

        return list_of_boats

    def write(self, list_of_boats: ListOfClubDinghyLimits):
        self.write_object(list_of_boats, file_identifier=CLUB_BOAT_LIMIT)
