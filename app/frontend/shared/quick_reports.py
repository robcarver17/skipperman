from app.frontend.reporting.rota.report_rota import rota_report_generator
from app.frontend.reporting.shared.create_report import create_generic_report
from app.frontend.shared.events_state import get_event_from_state
from app.objects.abstract_objects.abstract_form import File
from app.objects.abstract_objects.abstract_interface import abstractInterface


def create_quick_rota_report(interface: abstractInterface) -> File:
    report_generator_with_specific_parameters = (
        rota_report_generator.add_specific_parameters_for_type_of_report(
            interface.object_store, event=get_event_from_state(interface)
        )
    )
    interface.log_error(
        "Quick reports are generated with current report parameters: do not get published to web. To publish or change parameters to go Reporting menu option."
    )
    return create_generic_report(
        report_generator=report_generator_with_specific_parameters,
        interface=interface,
        override_print_options=dict(publish_to_public=False),
        ignore_stored_print_option_values_and_use_default=True,
    )
