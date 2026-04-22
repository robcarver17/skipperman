from typing import List

from app.data_access.store.object_store import ObjectStore
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.day_selectors import Day
from app.objects.events import Event
from app.objects.patrol_boats import PatrolBoat, ListOfPatrolBoatLabelsAtEvents
from app.objects.utilities.exceptions import missing_data


def get_patrol_boat_label_at_event_on_day(
    object_store: ObjectStore,
    event: Event,
    day: Day,
    patrol_boat: PatrolBoat,
    default="",
) -> str:
    list_of_labels = get_list_of_patrol_boat_labels_at_events(object_store)
    label = list_of_labels.get_patrol_boat_label(
        event_id=event.id, day=day, boat_id=patrol_boat.id, default=missing_data
    )
    if label is missing_data:
        return default
    else:
        return label.label


def get_list_of_unique_labels(object_store: ObjectStore) -> List[str]:
    return object_store.get(
        object_store.data_api.data_list_of_patrol_boat_labels.get_list_of_unique_labels
    )


def get_list_of_patrol_boat_labels_at_events(
    object_store: ObjectStore,
) -> ListOfPatrolBoatLabelsAtEvents:
    return object_store.get(object_store.data_api.data_list_of_patrol_boat_labels.read)


def update_list_of_patrol_boat_labels_at_events(
    interface: abstractInterface,
    list_of_patrol_boat_labels: ListOfPatrolBoatLabelsAtEvents,
):
    interface.update(
        interface.object_store.data_api.data_list_of_patrol_boat_labels.write,
        list_of_patrol_boat_labels=list_of_patrol_boat_labels,
    )


def add_patrol_boat_label_at_event(interface: abstractInterface,
                                   event: Event,
                                   patrol_boat: PatrolBoat,
                                   day: Day,
                                   label: str, ):
    interface.update(
        interface.object_store.data_api.data_list_of_patrol_boat_labels.add_patrol_boat_label_at_event_not_checking_for_existing_label,
        event_id=event.id,
        patrol_boat_id=patrol_boat.id,
        label=label,
        day=day,
    )

def update_existing_patrol_boat_label_at_event(
    interface: abstractInterface,
    event: Event,
    patrol_boat: PatrolBoat,
    day: Day,
    label: str,
):
    interface.update(
        interface.object_store.data_api.data_list_of_patrol_boat_labels.update_existing_patrol_boat_label_at_event,
        event_id=event.id,
        patrol_boat_id=patrol_boat.id,
        label=label,
        day=day,
    )
    interface.clear()


def copy_patrol_boat_labels_across_event(
    interface: abstractInterface, event: Event, overwrite: bool = False
):
    list_of_labels = get_list_of_patrol_boat_labels_at_events(interface.object_store)
    list_of_labels.copy_patrol_boat_labels_across_event(
        event_id=event.id, days_in_event=event.days_in_event(), overwrite=overwrite
    )
    update_list_of_patrol_boat_labels_at_events(
        interface=interface, list_of_patrol_boat_labels=list_of_labels
    )
