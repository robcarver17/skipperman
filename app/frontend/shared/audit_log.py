from app.backend.security.audit_logs import get_list_of_audit_logs_for_event_newest_first, get_list_of_audit_logs_for_all_events_newest_first
from app.frontend.shared.events_state import get_event_from_state
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_tables import PandasDFTable

def get_audit_log_to_display_for_event(interface: abstractInterface):
    event = get_event_from_state(interface)
    audit_log = (
        get_list_of_audit_logs_for_event_newest_first(object_store=interface.object_store, event=event))
    audit_log_as_df = audit_log.as_pd_df()

    return PandasDFTable(audit_log_as_df)

def get_audit_log_to_display_for_all_events(interface: abstractInterface):
    audit_log = get_list_of_audit_logs_for_all_events_newest_first(object_store=interface.object_store)
    audit_log_as_df = audit_log.as_pd_df()

    return PandasDFTable(audit_log_as_df)
