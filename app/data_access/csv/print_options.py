import pandas as pd

from app.reporting.options_and_parameters.print_options import PrintOptions
from app.data_access.csv.generic_csv_data import GenericCsvData
from app.data_access.classes.print_options import DataListOfPrintOptions


class csvDataListOfPrintOptions(DataListOfPrintOptions, GenericCsvData):
    def read_for_report(self, report_name: str) -> PrintOptions:
        path_and_filename = self.path_and_filename_for_report_name(report_name)
        try:
            print_options_as_df = pd.read_csv(path_and_filename)
        except:
            print("No options found using default")
            return PrintOptions(
                title_str=report_name, filename=report_name
            )  ## all defaults

        return PrintOptions.from_df(print_options_as_df)

    def write_for_report(self, report_name: str, print_options: PrintOptions):
        print_options_as_df = print_options.as_df()
        path_and_filename = self.path_and_filename_for_report_name(report_name)
        print_options_as_df.to_csv(path_and_filename, index=False)

    def path_and_filename_for_report_name(self, report_name: str):
        report_name_as_filename = report_name.replace(" ", "_")
        return self.get_path_and_filename_for_named_csv_file(
            "print_options", additional_file_identifiers=report_name_as_filename
        )
