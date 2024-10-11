from app.data_access.store.object_definitions import object_definition_for_list_of_events
from app.objects.abstract_objects.abstract_buttons import ButtonBar, Button
from app.objects.events import ListOfEvents, SORT_BY_START_DSC, SORT_BY_START_ASC, SORT_BY_NAME, Event

from app.data_access.store.object_store import ObjectStore

def get_event_from_list_of_events_given_event_description(
    object_store: ObjectStore, event_description: str
) -> Event:
    list_of_events = get_list_of_events(object_store)

    return list_of_events.event_with_description(event_description)

def get_sorted_list_of_events(object_store: ObjectStore,  sort_by=SORT_BY_START_DSC
) -> ListOfEvents:
    list_of_events = get_list_of_events(object_store)
    list_of_events = list_of_events.sort_by(sort_by)

    return list_of_events


def get_list_of_events(object_store: ObjectStore) -> ListOfEvents:
    return object_store.get(object_definition_for_list_of_events)

def update_list_of_evcents(object_store: ObjectStore, updated_list_of_events:ListOfEvents):
    object_store.update(new_object=updated_list_of_events, object_definition=object_definition_for_list_of_events)


all_sort_types_for_event_list = [SORT_BY_START_ASC, SORT_BY_START_DSC, SORT_BY_NAME]
sort_buttons_for_event_list = ButtonBar(
    [Button(sortby, nav_button=True) for sortby in all_sort_types_for_event_list]
)
