from app.data_access.classes.cadets import DataAttendanceAtEventsForSpecificCadet
from app.data_access.parquet.generic_parquet_data import GenericParquetData
from app.data_access.csv.resolve_paths_and_filenames import (
    ATTENDANCE_FILE_FOR_SPECIFIC_CADET,
)
from app.objects.attendance import ListOfRawAttendanceItemsForSpecificCadet


class ParquetDataAttendanceAtEventsForSpecificCadet(
    DataAttendanceAtEventsForSpecificCadet, GenericParquetData
):
    def read_attendance_for_cadet_id(
        self, cadet_id: str
    ) -> ListOfRawAttendanceItemsForSpecificCadet:
        return self.read_and_return_object_of_type(
            ListOfRawAttendanceItemsForSpecificCadet,
            file_identifier=ATTENDANCE_FILE_FOR_SPECIFIC_CADET,
            additional_file_identifiers=cadet_id,
        )

    def write_attendance_for_cadet_id(
        self,
        list_of_attendance: ListOfRawAttendanceItemsForSpecificCadet,
        cadet_id: str,
    ):
        self.write_object(
            list_of_attendance,
            file_identifier=ATTENDANCE_FILE_FOR_SPECIFIC_CADET,
            additional_file_identifiers=cadet_id,
        )
