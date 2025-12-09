from typing import List

from app.data_access.store.object_store import ObjectStore

from app.objects.volunteers import Volunteer

from app.objects.events import Event
from app.objects.groups import Group, ListOfGroups

from app.backend.volunteers.connected_cadets import (
    get_list_of_cadets_associated_with_volunteer,
)
from app.backend.groups.cadets_with_groups_at_event import (
    get_dict_of_cadets_with_groups_at_event,
)


def list_of_cadet_groups_associated_with_volunteer(
    object_store: ObjectStore,
    event: Event,
    volunteer: Volunteer,
) -> ListOfGroups:
    group_data = get_dict_of_cadets_with_groups_at_event(
        object_store=object_store, event=event
    )
    list_of_cadets = get_list_of_cadets_associated_with_volunteer(
        volunteer=volunteer, object_store=object_store
    )
    list_of_groups = []
    for cadet in list_of_cadets:
        days_and_groups_for_cadet = group_data.get_days_and_groups_for_cadet(cadet)
        list_of_groups_this_cadet = [
            days_and_groups_for_cadet.group_on_day(day, default=None)
            for day in event.days_in_event()
        ]
        list_of_groups_this_cadet = [
            group for group in list_of_groups_this_cadet if group is not None
        ]
        list_of_groups += list_of_groups_this_cadet

    list_of_groups = list(set(list_of_groups))

    return ListOfGroups(list_of_groups)
