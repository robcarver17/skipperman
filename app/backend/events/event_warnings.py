from typing import List

from app.data_access.store.object_definitions import object_definition_for_list_of_event_warnings
from app.data_access.store.object_store import ObjectStore
from app.objects.event_warnings import ListOfEventWarnings
from app.objects.events import Event



def get_list_of_event_warnings(object_store: ObjectStore, event: Event)-> ListOfEventWarnings:
    return object_store.get(
        object_definition_for_list_of_event_warnings,
        event_id=event.id
    )

def update_list_of_event_warnings(object_store: ObjectStore, event: Event, list_of_event_warnings: ListOfEventWarnings):
   object_store.update(list_of_event_warnings, object_definition=object_definition_for_list_of_event_warnings, event_id=event.id)

def add_list_of_event_warnings(object_store: ObjectStore, event: Event, new_list_of_warnings: ListOfEventWarnings):
    existing_list_of_warnings = get_list_of_event_warnings(object_store=object_store, event=event)
    for warning in new_list_of_warnings:
        existing_list_of_warnings. add_new_event_warning_checking_for_duplicate(warning)

    update_list_of_event_warnings(list_of_event_warnings=existing_list_of_warnings, event=event, object_store=object_store)

def add_new_event_warning_checking_for_duplicate(object_store: ObjectStore, event: Event, warning:str, category: str, priority: str, auto_refreshed: bool):
    list_of_warnings = get_list_of_event_warnings(object_store=object_store, event=event)
    list_of_warnings.add_new_event_warning_checking_for_duplicate_from_components(warning=warning, category=category, priority=priority, auto_refreshed=auto_refreshed)
    update_list_of_event_warnings(list_of_event_warnings=list_of_warnings, event=event, object_store=object_store)

def add_or_update_list_of_new_event_warnings_clearing_any_missing(object_store: ObjectStore, event: Event, new_list_of_warnings: List[str], category: str, priority: str):
    list_of_warnings = get_list_of_event_warnings(object_store=object_store, event=event)
    list_of_warnings.add_or_update_list_of_new_event_warnings_clearing_any_missing(list_of_warnings=new_list_of_warnings, category=category, priority=priority)
    update_list_of_event_warnings(list_of_event_warnings=list_of_warnings, event=event, object_store=object_store)


def mark_event_warning_with_id_as_ignore(object_store: ObjectStore, event: Event, warning_id:str):
    list_of_warnings = get_list_of_event_warnings(object_store=object_store, event=event)
    list_of_warnings.mark_event_warning_with_id_as_ignored(warning_id)
    update_list_of_event_warnings(list_of_event_warnings=list_of_warnings, event=event, object_store=object_store)


def mark_event_warning_with_id_as_unignore(object_store: ObjectStore, event: Event, warning_id:str):
    list_of_warnings = get_list_of_event_warnings(object_store=object_store, event=event)
    list_of_warnings.mark_event_warning_with_id_as_unignored(warning_id)
    update_list_of_event_warnings(list_of_event_warnings=list_of_warnings, event=event, object_store=object_store)

def get_list_of_warnings_at_event_for_categories_sorted_by_category_and_priority(object_store: ObjectStore, event: Event, list_of_categories: List[str]) -> ListOfEventWarnings:
    list_of_warnings = get_list_of_event_warnings(object_store=object_store, event=event)
    return list_of_warnings.get_list_of_warnings_at_event_for_categories_sorted_by_priority_and_category(list_of_categories=list_of_categories)


def get_list_of_all_warning_ids_at_event(object_store: ObjectStore, event: Event) -> List[str]:
    list_of_warnings = get_list_of_event_warnings(object_store=object_store, event=event)
    return list_of_warnings.list_of_ids



def mark_all_active_event_warnings_with_priority_and_category_as_ignored(object_store: ObjectStore, event: Event, category: str, priority: str):
    list_of_warnings = get_list_of_event_warnings(object_store=object_store, event=event)
    list_of_warnings.mark_all_active_event_warnings_with_priority_and_category_as_ignored(category=category, priority=priority)
    update_list_of_event_warnings(list_of_event_warnings=list_of_warnings, event=event, object_store=object_store)


def mark_all_ignored_event_warnings_with_priority_and_category_as_unignored(object_store: ObjectStore, event: Event,  category: str, priority: str):
    list_of_warnings = get_list_of_event_warnings(object_store=object_store, event=event)
    list_of_warnings.mark_all_ignored_event_warnings_with_priority_and_category_as_unignored(category=category, priority=priority)
    update_list_of_event_warnings(list_of_event_warnings=list_of_warnings, event=event, object_store=object_store)
