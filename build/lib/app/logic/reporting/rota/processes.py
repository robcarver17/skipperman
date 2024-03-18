from app.backend.reporting.rota_report import AdditionalParametersForVolunteerReport, \
    get_df_for_reporting_volunteers_with_flags
from app.logic.events.events_in_state import get_event_from_state
from app.objects.abstract_objects.abstract_interface import abstractInterface


def get_df_for_reporting_allocations(interface: abstractInterface) -> pd.DataFrame:
    event = get_event_from_state(interface)
    additional_parameters = load_additional_parameters_for_rota_report(interface)
    df =  get_df_for_reporting_volunteers_with_flags(
        event=event
    )

    return df


def load_additional_parameters_for_rota_report(
    interface: abstractInterface,
) -> AdditionalParametersForVolunteerReport:
    display_full_names = interface.get_persistent_value('FIXME1', False)
    include_unallocated_cadets = interface.get_persistent_value(
        'FIXME1', False
    )

    return AdditionalParametersForVolunteerReport(
        days_to_show='',
        include_unallocated_cadets=include_unallocated_cadets,
    )


