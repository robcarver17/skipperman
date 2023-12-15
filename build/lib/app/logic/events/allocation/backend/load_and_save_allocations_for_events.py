from app.logic.cadets.view_cadets import cadet_name_from_id
from app.objects.events import Event
from app.objects.groups import ListOfCadetIdsWithGroups
from app.data_access.data import data


def load_allocation_for_event(event: Event) -> ListOfCadetIdsWithGroups:
    event_id = event.id

    list_of_cadets_with_groups = (
        data.data_list_of_cadets_with_groups.read_groups_for_event(event_id)
    )

    return list_of_cadets_with_groups


def save_allocation_for_event(
    list_of_cadets_with_groups: ListOfCadetIdsWithGroups,
    event: Event,
):
    event_id = event.id

    data.data_list_of_cadets_with_groups.write_groups_for_event(
        event_id=event_id, list_of_cadets_with_groups=list_of_cadets_with_groups
    )
