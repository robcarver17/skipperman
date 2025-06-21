from dataclasses import dataclass
from typing import Dict

from app.data_access.configuration.field_list_groups import (
    GROUP_ALLOCATION_FIELDS,
    GROUP_ALLOCATION_FIELDS_HIDE,
)
from app.objects.cadets import Cadet
from app.objects.composed.cadets_with_all_event_info import (
    DictOfAllEventInfoForCadets,
    AllEventInfoForCadet,
)


@dataclass
class GroupAllocationInfo:
    dict_of_dicts: Dict[str, Dict[Cadet, str]]

    @property
    def visible_field_names(self) -> list:
        fields = [
            field
            for field in self.field_names
            if field not in GROUP_ALLOCATION_FIELDS_HIDE
        ]

        return fields

    @property
    def field_names(self) -> list:
        return list(self.dict_of_dicts.keys())

    def dict_for_field_name(self, field_name: str) -> Dict[Cadet, str]:
        info_dict_for_key = self.dict_of_dicts.get(field_name, None)
        if info_dict_for_key is None:
            raise Exception("Group allocation info not found for %s" % field_name)

        return info_dict_for_key

    def group_info_dict_for_cadet_as_ordered_list(self, cadet: Cadet):
        info_dict = self.get_allocation_info_for_cadet(cadet)

        return [
            info_dict.get(field_name, "") for field_name in self.visible_field_names
        ]

    def get_allocation_info_for_cadet(self, cadet: Cadet) -> dict:
        field_names = self.field_names
        info_dict = dict(
            [
                (
                    field_name,
                    cadet_info_from_info_dict(self, cadet=cadet, field_name=field_name),
                )
                for field_name in field_names
            ]
        )

        return info_dict

    def remove_empty_fields(self):
        dict_of_dicts = self.dict_of_dicts
        ## in place
        for field_name in list(self.field_names):
            if all_empty(self.dict_for_field_name(field_name)):
                dict_of_dicts.pop(field_name)


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


def cadet_info_from_info_dict(
    group_allocation_info: GroupAllocationInfo, cadet: Cadet, field_name: str
):
    info_dict_for_key = group_allocation_info.dict_for_field_name(field_name)

    cadet_value = info_dict_for_key.get(cadet, None)
    if cadet_value is None:
        raise Exception("Group allocation info not found for cadet %s" % cadet)

    return cadet_value


def all_empty(some_dict: dict):
    all_values = list(some_dict.values())
    all_values_as_str = [str(x) for x in all_values]
    return all([len(value) == 0 for value in all_values_as_str])
