from app.backend.data.options import OptionsData

from app.backend.reporting.arrangement.arrange_options import ArrangementOptionsAndGroupOrder
from app.objects.abstract_objects.abstract_interface import abstractInterface


def get_stored_arrangement_and_group_order(interface: abstractInterface, report_type: str) -> ArrangementOptionsAndGroupOrder:
    options_data = OptionsData(interface.data)
    return options_data.get_arrange_group_options(report_name=report_type)


def save_arrangement_and_group_order(
    interface: abstractInterface, arrangement_and_group_options: ArrangementOptionsAndGroupOrder,
        report_type: str
):
    options_data = OptionsData(interface.data)
    options_data.save_arrange_group_options(arrange_group_options=arrangement_and_group_options, report_name=report_type)



