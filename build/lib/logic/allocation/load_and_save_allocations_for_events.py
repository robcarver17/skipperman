from objects.events import Event
from objects.groups import ListOfCadetIdsWithGroups
from logic.data_and_interface import DataAndInterface


def load_allocation_for_event(
    event: Event, data_and_interface: DataAndInterface
) -> ListOfCadetIdsWithGroups:
    data = data_and_interface.data
    event_id = event.id

    list_of_cadets_with_groups = data.data_list_of_cadets_with_groups.read(event_id)

    return list_of_cadets_with_groups


def save_allocation_for_event(
    list_of_cadets_with_groups: ListOfCadetIdsWithGroups,
    event: Event,
    data_and_interface: DataAndInterface,
):
    data = data_and_interface.data
    event_id = event.id

    data.data_list_of_cadets_with_groups.write(
        event_id=event_id, list_of_cadets_with_groups=list_of_cadets_with_groups
    )
