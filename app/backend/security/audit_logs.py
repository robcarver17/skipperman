import datetime

from app.backend.security.logged_in_user import get_logged_in_skipperman_user
from app.backend.volunteers.list_of_volunteers import get_list_of_volunteers
from app.data_access.store.object_store import ObjectStore
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.audit_log import (
    ListOfAuditLogUpdatesWithIds,
    AuditLogUpdateWithIds,
    ListOfAuditLogUpdatesWithEvents,
)
from app.objects.events import Event


def get_list_of_audit_logs_for_all_events_newest_first(
    object_store: ObjectStore,
) -> ListOfAuditLogUpdatesWithEvents:
    return object_store.get(
        object_store.data_api.data_list_of_audit_updates.read_for_all_events
    )


def get_list_of_audit_logs_for_event_newest_first(
    object_store: ObjectStore, event: Event
) -> ListOfAuditLogUpdatesWithIds:
    return object_store.get(
        object_store.data_api.data_list_of_audit_updates.read, event_id=event.id
    )


def add_audit_log(interface: abstractInterface, event: Event):
    user = get_logged_in_skipperman_user(interface)
    list_of_volunteers = get_list_of_volunteers(interface.object_store)
    volunteer = list_of_volunteers.volunteer_with_id(user.volunteer_id)
    audit_log = AuditLogUpdateWithIds(
        username=user.username,
        volunteer_name=volunteer.name,
        event_id=event.id,
        datetime_of_update=datetime.datetime.now(),
    )

    interface.update(
        interface.object_store.data_api.data_list_of_audit_updates.add_audit_log,
        audit_log=audit_log,
    )
