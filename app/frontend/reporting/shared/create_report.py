import os

from app.backend.file_handling import generate_qr_code_for_file_in_public_path
from app.backend.reporting.process_stages.create_column_report_from_df import (
    create_column_report_from_df_and_return_filename,
)
from app.backend.reporting.report_generator import ReportGenerator
from app.frontend.reporting.shared.reporting_options import get_reporting_options
from app.objects.abstract_objects.abstract_form import File
from app.objects.abstract_objects.abstract_interface import abstractInterface

def qr_code_for_report(    interface: abstractInterface, report_generator: ReportGenerator
):
    path_and_filename = create_generic_report_and_return_filename(
        interface, report_generator
    )
    filename = os.path.split(path_and_filename)[-1]
    return generate_qr_code_for_file_in_public_path(filename)

def create_generic_report(
    interface: abstractInterface, report_generator: ReportGenerator
) -> File:

    filename = create_generic_report_and_return_filename(
        interface, report_generator
    )
    return File(filename)



def create_generic_report_and_return_filename(
    interface: abstractInterface, report_generator: ReportGenerator
) -> str:
    print("Creating report")

    specific_parameters_for_type_of_report = (
        report_generator.specific_parameters_for_type_of_report
    )
    dict_of_df = report_generator.get_dict_of_df(interface)

    reporting_options = get_reporting_options(
        interface=interface,
        specific_parameters_for_type_of_report=specific_parameters_for_type_of_report,
        dict_of_df=dict_of_df,
    )

    reporting_options.filter_arrangement_options_in_place_to_remove_non_existent_groups()

    filename = create_column_report_from_df_and_return_filename(
        reporting_options=reporting_options
    )

    return filename