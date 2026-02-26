from app.backend.reporting.arrangement.arrange_options import (
    ArrangementOptionsAndGroupOrder,
)
from app.data_access.store.object_store import ObjectStore
from app.backend.reporting.report_generator import ReportGenerator
from app.objects.abstract_objects.abstract_interface import abstractInterface


def get_stored_arrangement_and_group_order(
    object_store: ObjectStore, report_type: str
) -> ArrangementOptionsAndGroupOrder:
    return object_store.get(
        object_store.data_api.data_arrangement_and_group_order_options.read,
        report_name=report_type,
    )


def update_arrangement_and_group_order(
    interface: abstractInterface,
    arrangement_and_group_options: ArrangementOptionsAndGroupOrder,
    report_type: str,
):
    interface.update(
        interface.object_store.data_api.data_arrangement_and_group_order_options.write,
        report_name=report_type,
        arrange_options=arrangement_and_group_options,
    )


def reset_arrangement_report_options(
    interface: abstractInterface, report_generator: ReportGenerator
):
    update_arrangement_and_group_order(
        interface=interface,
        report_type=report_generator.report_type,
        arrangement_and_group_options=ArrangementOptionsAndGroupOrder.create_empty(),
    )
