from app.data_access.classes.resources import *
from app.data_access.parquet.generic_parquet_data import GenericParquetData
from app.data_access.csv.resolve_paths_and_filenames import (
    CLUB_BOAT_LIMIT,
)


class ParquetDataListOfClubDinghyLimits(GenericParquetData, DataListOfClubDinghyLimits):
    def read(self) -> ListOfClubDinghyLimits:
        list_of_boats = self.read_and_return_object_of_type(
            ListOfClubDinghyLimits, file_identifier=CLUB_BOAT_LIMIT
        )

        return list_of_boats

    def write(self, list_of_boats: ListOfClubDinghyLimits):
        self.write_object(list_of_boats, file_identifier=CLUB_BOAT_LIMIT)
