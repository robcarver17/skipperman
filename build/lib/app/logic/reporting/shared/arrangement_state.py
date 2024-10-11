from app.OLD_backend.data.options import OptionsData

from app.OLD_backend.reporting.arrangement.arrange_options import (
    ArrangementOptionsAndGroupOrder,
)
from app.frontend.reporting.shared.report_generator import ReportGenerator
from app.objects.abstract_objects.abstract_interface import abstractInterface


def get_stored_arrangement_and_group_order(
    interface: abstractInterface, report_type: str
) -> ArrangementOptionsAndGroupOrder:
    options_data = OptionsData(interface.data)
    arrangement_options_and_group_order = options_data.get_arrange_group_options(
        report_name=report_type
    )
    return arrangement_options_and_group_order


def save_arrangement_and_group_order(
    interface: abstractInterface,
    arrangement_and_group_options: ArrangementOptionsAndGroupOrder,
    report_type: str,
):
    options_data = OptionsData(interface.data)
    options_data.save_arrange_group_options(
        arrange_group_options=arrangement_and_group_options, report_name=report_type
    )


def reset_arrangement_report_options(
    interface: abstractInterface, report_generator: ReportGenerator
):
    options_data = OptionsData(interface.data)
    options_data.reset_arrangement_options_to_default(report_name=report_generator.name)
