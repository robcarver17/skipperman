from app.data_access.data import data
from app.backend.data.mapped_events import load_master_event
from app.backend.group_allocations import get_list_of_cadets
from app.objects.cadets import ListOfCadets
from app.objects.events import Event
from app.objects.groups import ListOfCadetIdsWithGroups

def get_list_of_cadets_in_master_event(
    event: Event,
    exclude_deleted: bool = True,
    exclude_cancelled: bool = True,
    exclude_active: bool = False,
) -> ListOfCadets:
    list_of_cadet_ids = get_list_of_cadet_ids_in_mapped_wa_event(
        event=event,
        exclude_active=exclude_active,
        exclude_deleted=exclude_deleted,
        exclude_cancelled=exclude_cancelled,
    )
    list_of_cadets = get_list_of_cadets_given_list_of_ids(
        list_of_cadet_ids=list_of_cadet_ids
    )

    return list_of_cadets


def get_list_of_cadets_given_list_of_ids(
    list_of_cadet_ids: list
) -> ListOfCadets:
    master_list_of_cadets = get_list_of_cadets()
    list_of_cadets = ListOfCadets.subset_from_list_of_ids(
        master_list_of_cadets, list_of_ids=list_of_cadet_ids
    )

    return list_of_cadets


def get_list_of_cadet_ids_in_mapped_wa_event(
    event: Event,
    exclude_deleted: bool = True,
    exclude_cancelled: bool = True,
    exclude_active: bool = False,
) -> list:
    master_event = load_master_event(event)
    list_of_cadet_ids = (
        master_event.list_of_cadet_ids_with_given_status(
            exclude_cancelled=exclude_cancelled,
            exclude_deleted=exclude_deleted,
            exclude_active=exclude_active,
        )
    )

    return list_of_cadet_ids

def get_current_allocations(event: Event) -> ListOfCadetIdsWithGroups:
    return data.data_list_of_cadets_with_groups.read_groups_for_event(event_id=event.id)

def get_previous_allocations() -> ListOfCadetIdsWithGroups:
    return data.data_list_of_cadets_with_groups.read_last_groups()

def save_current_allocations_for_event(event: Event, list_of_cadets_with_groups: ListOfCadetIdsWithGroups):
    data.data_list_of_cadets_with_groups.write_groups_for_event(event_id=event.id, list_of_cadets_with_groups=list_of_cadets_with_groups)

def update_previous_allocations(list_of_cadets_with_groups: ListOfCadetIdsWithGroups):
    data.data_list_of_cadets_with_groups.write_last_groups(
                                                                list_of_cadets_with_groups)
