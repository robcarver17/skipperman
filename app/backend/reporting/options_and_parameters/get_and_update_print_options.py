from app.backend.reporting.options_and_parameters.print_options import PrintOptions
from app.data_access.store.object_store import ObjectStore
from app.objects.abstract_objects.abstract_interface import abstractInterface


def get_default_print_options(
    object_store: ObjectStore, report_name: str
) -> PrintOptions:
    return object_store.data_api.data_print_options.read("%s_default" % report_name)


def get_print_options(
    object_store: ObjectStore,
    report_name: str,
    ignore_stored_values_and_use_default: bool,
) -> PrintOptions:
    if ignore_stored_values_and_use_default:
        return get_default_print_options(
            object_store=object_store, report_name=report_name
        )

    return object_store.data_api.data_print_options.read("%s_default" % report_name)



def reset_print_options_to_default(interface: abstractInterface, report_name: str):
    print_options = get_default_print_options(
        object_store=interface.object_store, report_name=report_name
    )
    update_print_options(
        interface=interface, report_name=report_name, print_options=print_options
    )


def update_print_options(
    interface: abstractInterface, report_name: str, print_options: PrintOptions
):
    interface.update(
        interface.object_store.data_api.data_print_options.write,
        print_options=print_options
    )