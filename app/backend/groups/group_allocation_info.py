from typing import Dict

from app.data_access.configuration.field_list_groups import (
    GROUP_ALLOCATION_FIELDS,
)
from app.objects.cadets import Cadet
from app.objects.composed.cadets_at_event_with_groups import GroupAllocationInfo
from app.objects.composed.cadets_with_all_event_info import (
    DictOfAllEventInfoForCadets,
    AllEventInfoForCadet,
)


def get_group_allocation_info(
    dict_of_all_event_data: DictOfAllEventInfoForCadets,
) -> GroupAllocationInfo:
    dict_of_dicts = get_dict_of_dicts_of_group_allocation_fields(dict_of_all_event_data)

    group_allocation_info = GroupAllocationInfo(dict_of_dicts=dict_of_dicts)
    group_allocation_info.remove_empty_fields()

    return group_allocation_info


def get_dict_of_dicts_of_group_allocation_fields(
    dict_of_all_event_data: DictOfAllEventInfoForCadets,
) -> Dict[str, Dict[Cadet, str]]:
    dict_of_dicts = dict(
        [
            (
                field_key,
                get_dict_of_value_by_cadet(
                    dict_of_all_event_data=dict_of_all_event_data, field_key=field_key
                ),
            )
            for field_key in GROUP_ALLOCATION_FIELDS
        ]
    )

    return dict_of_dicts


def get_dict_of_value_by_cadet(
    dict_of_all_event_data: DictOfAllEventInfoForCadets, field_key: str
) -> Dict[Cadet, str]:
    dict_of_cadet_id_and_values = dict(
        [
            (
                cadet,
                get_value_for_cadet_at_event(
                    event_data_for_cadet=event_data_for_cadet, field_key=field_key
                ),
            )
            for cadet, event_data_for_cadet in dict_of_all_event_data.items()
        ]
    )

    return dict_of_cadet_id_and_values


def get_value_for_cadet_at_event(
    event_data_for_cadet: AllEventInfoForCadet, field_key: str
) -> str:
    return event_data_for_cadet.registration_data.data_in_row.get(field_key, "")


