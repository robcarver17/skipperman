from app.backend.reporting.options_and_parameters.print_options import PrintOptions
from app.data_access.store.object_definitions import object_definition_for_print_options
from app.data_access.store.object_store import ObjectStore


def get_print_options(object_store: ObjectStore, report_name: str) -> PrintOptions:
    return object_store.get(
        object_definition_for_print_options, report_name=report_name
    )


def reset_print_options_to_default(object_store: ObjectStore, report_name: str):
    update_print_options(
        object_store=object_store, report_name=report_name, print_options=PrintOptions()
    )


def update_print_options(
    object_store: ObjectStore, report_name: str, print_options: PrintOptions
):
    object_store.update(
        object_definition=object_definition_for_print_options,
        report_name=report_name,
        new_object=print_options,
    )
