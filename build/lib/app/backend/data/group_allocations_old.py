from app.data_access.data import DEPRECATED_data
from app.objects.events import Event
from app.objects.groups import ListOfCadetIdsWithGroups


def load_list_of_cadets_with_allocated_groups_at_event(event: Event) -> ListOfCadetIdsWithGroups:
    event_id = event.id

    list_of_cadets_with_groups = (
        DEPRECATED_data.data_list_of_cadets_with_groups.read_groups_for_event(event_id)
    )

    return list_of_cadets_with_groups


def save_list_of_cadets_with_allocated_groups_for_event(
    event: Event, list_of_cadets_with_groups: ListOfCadetIdsWithGroups
):
    DEPRECATED_data.data_list_of_cadets_with_groups.write_groups_for_event(
        event_id=event.id, list_of_cadets_with_groups=list_of_cadets_with_groups
    )
