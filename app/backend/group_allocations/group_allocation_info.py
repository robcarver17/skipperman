from dataclasses import dataclass
from typing import Dict


from app.data_access.configuration.field_list_groups import GROUP_ALLOCATION_FIELDS, GROUP_ALLOCATION_FIELDS_HIDE
from app.objects.cadet_at_event import ListOfCadetsAtEvent
from app.objects.cadets import Cadet

@dataclass
class GroupAllocationInfo:
    dict_of_dicts: Dict[str, Dict[str,str]]

    @property
    def visible_field_names(self) -> list:
        fields = [field for field in self.field_names if field not in GROUP_ALLOCATION_FIELDS_HIDE]

        return fields

    @property
    def field_names(self)-> list:
        return list(self.dict_of_dicts.keys())

    def dict_for_field_name(self, field_name: str)-> Dict[str,str]:
        info_dict_for_key = self.dict_of_dicts.get(field_name, None)
        if info_dict_for_key is None:
            raise Exception("Group allocation info not found for %s" % field_name)

        return info_dict_for_key

    def get_allocation_info_for_cadet(self, cadet: Cadet) -> dict:
        field_names = self.field_names
        return dict(
            [
                (field_name, _cadet_key_from_info_dict(self, cadet_id=cadet.id, field_name=field_name))
                for field_name in field_names
            ]
        )

    def remove_empty_fields(self):
        dict_of_dicts = self.dict_of_dicts
        ## in place
        for field_name in list(self.field_names):
            if all_empty(self.dict_for_field_name(field_name)):
                dict_of_dicts.pop(field_name)



def _cadet_key_from_info_dict(group_allocation_info:GroupAllocationInfo, cadet_id: str, field_name:str):
    info_dict_for_key = group_allocation_info.dict_for_field_name(field_name)

    cadet_value = info_dict_for_key.get(cadet_id, None)
    if cadet_value is None:
        raise Exception("Group allocation info not found for cadet %s" % cadet_id)

    return cadet_value


def all_empty(some_dict: dict):
    all_values = list(some_dict.values())
    return all([len(value)==0 for value in all_values])


def get_group_allocation_info(cadets_at_event: ListOfCadetsAtEvent)-> GroupAllocationInfo:
    dict_of_dicts = get_dict_of_dicts_of_group_allocation_fields(cadets_at_event)

    group_allocation_info = GroupAllocationInfo(dict_of_dicts=dict_of_dicts)
    group_allocation_info.remove_empty_fields()

    return group_allocation_info


def get_dict_of_dicts_of_group_allocation_fields(cadets_at_event: ListOfCadetsAtEvent) -> Dict[str, Dict[str, str]]:
    dict_of_dicts = dict(
        [
            (field_key, get_dict_of_value_by_cadet_id(cadets_at_event=cadets_at_event, field_key=field_key))
            for field_key in GROUP_ALLOCATION_FIELDS
        ]
    )

    return dict_of_dicts


def get_dict_of_value_by_cadet_id(cadets_at_event: ListOfCadetsAtEvent, field_key: str) -> Dict[str, str]:
    list_of_ids = cadets_at_event.list_of_cadet_ids()
    dict_of_cadet_id_and_values = dict(
        [
            (id, get_value_for_cadet_id_in_event(cadets_at_event=cadets_at_event, field_key=field_key, id=id))
            for id in list_of_ids
        ]
    )

    return dict_of_cadet_id_and_values


def get_value_for_cadet_id_in_event(cadets_at_event: ListOfCadetsAtEvent, field_key: str, id: str):
    cadet_at_event = cadets_at_event.cadet_at_event_or_missing_data(id)
    return cadet_at_event.data_in_row.get(field_key, "")
