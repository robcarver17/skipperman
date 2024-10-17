from app.objects.composed.volunteers_at_event_with_patrol_boats import DictOfVolunteersAtEventWithPatrolBoatsByDay
from app.objects.events import Event

from app.data_access.store.object_store import ObjectStore

from app.data_access.store.object_definitions import \
    object_definition_for_dict_of_patrol_boats_by_day_for_volunteer_at_event


def get_dict_of_patrol_boats_by_day_for_volunteer_at_event(object_store: ObjectStore, event: Event) -> DictOfVolunteersAtEventWithPatrolBoatsByDay:
    return object_store.get(
        object_definition=object_definition_for_dict_of_patrol_boats_by_day_for_volunteer_at_event,
        event_id = event.id
    )