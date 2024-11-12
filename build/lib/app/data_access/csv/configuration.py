from app.OLD_backend.reporting.arrangement.arrange_options import (
    ArrangeGroupsOptions,
    ArrangementOptionsAndGroupOrder,
)

from app.OLD_backend.reporting.options_and_parameters.print_options import PrintOptions
from app.data_access.csv.generic_csv_data import GenericCsvData
from app.data_access.classes.configuration import (
    DataListOfPrintOptions,
    DataListOfArrangementAndGroupOrderOptions,
)
from app.data_access.csv.resolve_csv_paths_and_filenames import (
    PRINT_OPTIONS_FILE_ID,
    ARRANGEMENT_OPTIONS_FILE_ID,
    GROUPS_FILE_ID,
)

from app.data_access.classes.configuration import DataListOfGroups
from app.objects.groups import ListOfGroups


class csvDataListOfGroups(DataListOfGroups, GenericCsvData):
    def read(self) -> ListOfGroups:
        return self.read_and_return_object_of_type(
            ListOfGroups, file_identifier=GROUPS_FILE_ID
        )

    def write(self, list_of_groups: ListOfGroups):
        self.write_object(object=list_of_groups, file_identifier=GROUPS_FILE_ID)


class csvDataListOfPrintOptions(DataListOfPrintOptions, GenericCsvData):
    def read_for_report(self, report_name: str) -> PrintOptions:
        print_options = self.read_and_return_object_of_type(
            PrintOptions,
            file_identifier=PRINT_OPTIONS_FILE_ID,
            additional_file_identifiers=report_name,
        )
        return print_options

    def write_for_report(self, print_options: PrintOptions, report_name: str):
        self.write_object(
            print_options,
            file_identifier=PRINT_OPTIONS_FILE_ID,
            additional_file_identifiers=report_name,
        )


class csvDataListOfArrangementOptions(
    DataListOfArrangementAndGroupOrderOptions, GenericCsvData
):
    def read_for_report(self, report_name: str) -> ArrangementOptionsAndGroupOrder:
        arrange_options = self.read_and_return_object_of_type(
            ArrangementOptionsAndGroupOrder,
            file_identifier=ARRANGEMENT_OPTIONS_FILE_ID,
            additional_file_identifiers=report_name,
        )
        return arrange_options

    def write_for_report(
        self, arrange_options: ArrangementOptionsAndGroupOrder, report_name: str
    ):
        self.write_object(
            arrange_options,
            file_identifier=ARRANGEMENT_OPTIONS_FILE_ID,
            additional_file_identifiers=report_name,
        )
