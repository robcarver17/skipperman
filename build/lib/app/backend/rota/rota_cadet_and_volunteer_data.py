from typing import List

from app.OLD_backend.volunteers.volunteers import get_dict_of_existing_skills

from app.OLD_backend.data.group_allocations import GroupAllocationsData
from app.data_access.store.DEPRECATE_ad_hoc_cache import AdHocCache
from app.data_access.store.data_layer import DataLayer
from app.objects.events import Event
from app.objects.groups import sorted_locations_REPLACE_WITH_PROPER_SORT_NOT_STR, Group
from app.objects.volunteers import Volunteer
from app.objects_OLD.volunteers_at_event import DEPRECATE_VolunteerAtEvent


def get_cadet_location_string(
        data_layer: DataLayer,
    volunteer_at_event: DEPRECATE_VolunteerAtEvent,
):
    list_of_groups = list_of_cadet_groups_associated_with_volunteer(data_layer,
          volunteer_at_event=volunteer_at_event
    )
    if len(list_of_groups) == 0:
        return "x- no associated cadets -x"  ## trick to get at end of sort

    return str_type_of_group_given_list_of_groups(list_of_groups)



def str_type_of_group_given_list_of_groups(list_of_groups: List[Group]):
    types_of_groups = [group.type_of_group() for group in list_of_groups]
    unique_list_of_group_locations = list(set(types_of_groups))
    sorted_list_of_group_locations = sorted_locations_REPLACE_WITH_PROPER_SORT_NOT_STR(unique_list_of_group_locations)
    return ", ".join(sorted_list_of_group_locations)



def list_of_cadet_groups_associated_with_volunteer(
    data_layer: DataLayer,
    volunteer_at_event: DEPRECATE_VolunteerAtEvent,
) -> List[Group]:
    list_of_cadet_ids = volunteer_at_event.list_of_associated_cadet_id
    list_of_groups = []
    for cadet_id in list_of_cadet_ids:
        list_of_groups+=groups_given_cadet_id(data_layer=data_layer, cadet_id=cadet_id, event=volunteer_at_event.event)


    return list(set(list_of_groups))


def groups_given_cadet_id(data_layer: DataLayer, event: Event, cadet_id: str) -> List[Group]:
    group_data = GroupAllocationsData(data_layer)
    list_of_cadet_ids_with_groups = group_data.groups_given_cadet_id(event=event, cadet_id=cadet_id)

    return list_of_cadet_ids_with_groups



def get_str_dict_skills(
        cache: AdHocCache,
    volunteer: Volunteer
):

    dict_of_skills = cache.get_from_cache(get_dict_of_existing_skills,
                                          volunteer=volunteer)
    if dict_of_skills.empty():
        return "No skills recorded"

    return dict_of_skills.skills_held_as_str()
