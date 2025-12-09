from app.backend.reporting.arrangement.arrange_options import (
    ArrangementOptionsAndGroupOrder,
)
from app.data_access.store.object_definitions import (
    object_definition_for_report_arrangement_and_group_order_options,
)
from app.data_access.store.object_store import ObjectStore
from app.backend.reporting.report_generator import ReportGenerator


def get_stored_arrangement_and_group_order(
    object_store: ObjectStore, report_type: str
) -> ArrangementOptionsAndGroupOrder:
    return object_store.get(
        object_definition=object_definition_for_report_arrangement_and_group_order_options,
        report_name=report_type,
    )


def update_arrangement_and_group_order(
    object_store: ObjectStore,
    arrangement_and_group_options: ArrangementOptionsAndGroupOrder,
    report_type: str,
):
    object_store.update(
        object_definition=object_definition_for_report_arrangement_and_group_order_options,
        report_name=report_type,
        new_object=arrangement_and_group_options,
    )


def reset_arrangement_report_options(
    object_store: ObjectStore, report_generator: ReportGenerator
):
    update_arrangement_and_group_order(
        object_store=object_store,
        report_type=report_generator.report_type,
        arrangement_and_group_options=ArrangementOptionsAndGroupOrder.create_empty(),
    )
