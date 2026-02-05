from typing import List

from app.data_access.store.object_store import ObjectStore
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.event_warnings import ListOfEventWarnings, EventWarningLog
from app.objects.events import Event


def get_list_of_event_warnings(
    object_store: ObjectStore, event: Event
) -> ListOfEventWarnings:
    return object_store.get(
        object_store.data_api.data_event_warnings.read, event_id=event.id
    )



def add_list_of_event_warnings(
    interface: abstractInterface, event: Event, new_list_of_warnings: ListOfEventWarnings
):
    for warning_log in new_list_of_warnings:
        add_new_event_warning_checking_for_duplicate(interface=interface,
                                                                      event=event,
                                                    warning_log=warning_log)


def add_new_event_warning_given_components_checking_for_duplicate(
    interface: abstractInterface,
    event: Event,
    warning: str,
    category: str,
    priority: str,
    auto_refreshed: bool,
):
    warning_log = EventWarningLog(
        warning=warning,
        category=category,
        priority=priority,
        auto_refreshed=auto_refreshed
    )
    add_new_event_warning_checking_for_duplicate(interface=interface,
                                                 warning_log=warning_log,
                                                 event=event)


def add_new_event_warning_checking_for_duplicate(
    interface: abstractInterface,
    event: Event,
    warning_log: EventWarningLog
):
    interface.update(
        interface.object_store.data_api.data_event_warnings.add_new_event_warning_checking_for_duplicate,
        event_id=event.id,
        warning_log=warning_log
    )




def mark_event_warning_with_id_as_ignore(
    interface: abstractInterface, event: Event, warning_id: str
):
    interface.update(
        interface.object_store.data_api.data_event_warnings.mark_event_warning_with_id_with_ignore_flag,
        event_id=event.id,
        warning_id=warning_id,
        ignore_flag=True
    )

def mark_event_warning_with_id_as_unignore(
    interface: abstractInterface, event: Event, warning_id: str
):
    interface.update(
        interface.object_store.data_api.data_event_warnings.mark_event_warning_with_id_with_ignore_flag,
        event_id=event.id,
        warning_id=warning_id,
        ignore_flag=False
    )


def get_list_of_warnings_at_event_for_categories_sorted_by_category_and_priority(
    object_store: ObjectStore, event: Event, list_of_categories: List[str]
) -> ListOfEventWarnings:
    list_of_warnings = get_list_of_event_warnings(
        object_store=object_store, event=event
    )
    return list_of_warnings.get_list_of_warnings_at_event_for_categories_sorted_by_priority_and_category(
        list_of_categories=list_of_categories
    )


def get_list_of_all_warning_ids_at_event(
    object_store: ObjectStore, event: Event
) -> List[str]:
    list_of_warnings = get_list_of_event_warnings(
        object_store=object_store, event=event
    )
    return list_of_warnings.list_of_ids


def mark_all_active_event_warnings_with_priority_and_category_as_ignored(
    interface: abstractInterface, event: Event, category: str, priority: str
):
    interface.update(
        interface.object_store.data_api.data_event_warnings.reverse_ignore_on_active_event_warnings_with_priority_and_category,
        event_id=event.id,
        category=category,
        priority=priority,
        set_active_to_ignored=True
    )


def mark_all_ignored_event_warnings_with_priority_and_category_as_unignored(
    interface: abstractInterface, event: Event, category: str, priority: str
):
    interface.update(
        interface.object_store.data_api.data_event_warnings.reverse_ignore_on_active_event_warnings_with_priority_and_category,
        event_id=event.id,
        category=category,
        priority=priority,
        set_active_to_ignored=False
    )

def process_list_of_warnings_which_auto_clear(
    interface: abstractInterface,
    event: Event,
    list_of_warnings: List[str],
    priority: str,
    category: str,
):
    interface.update(
        interface.object_store.data_api.data_event_warnings.add_or_update_list_of_autorefreshed_event_warnings_clearing_any_missing,
            new_list_of_warnings=list_of_warnings,
            category=category,
            priority=priority,
            event_id= event.id
        )

