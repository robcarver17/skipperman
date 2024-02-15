from app.backend.reporting.options_and_parameters.print_options import PrintOptions
from app.data_access.csv.generic_csv_data import GenericCsvData
from app.data_access.classes.print_options import DataListOfPrintOptions
from app.data_access.csv.resolve_csv_paths_and_filenames import PRINT_OPTIONS_FILE_ID


class csvDataListOfPrintOptions(DataListOfPrintOptions, GenericCsvData):
    def read_for_report(self, report_name: str) -> PrintOptions:
        print_options = self.read_and_return_object_of_type(PrintOptions, file_identifier=PRINT_OPTIONS_FILE_ID,
                                                            additional_file_identifiers=report_name)
        return print_options

    def write_for_report(self, report_name: str, print_options: PrintOptions):
        self.write_object(print_options, file_identifier=PRINT_OPTIONS_FILE_ID,
                          additional_file_identifiers=report_name)

