from typing import List

from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.cadets import Cadet

from app.backend.groups.cadets_with_groups_at_event import get_group_allocations_for_event_active_cadets_only

from app.data_access.store.object_store import ObjectStore

from app.objects.composed.ticksheet import (
    DictOfCadetsWithQualificationsAndTicks,
    DictOfCadetsAndTicksWithinQualification,
)
from app.objects.events import Event
from app.objects.groups import Group
from app.objects.qualifications import Qualification
from app.objects.ticks import (
    Tick,
)
from app.objects.substages import TickSheetItem


def get_ticksheet_data_for_cadets_at_event_in_group_with_qualification(
    object_store: ObjectStore, event: Event, group: Group, qualification: Qualification
) -> DictOfCadetsAndTicksWithinQualification:

    all_group_allocations_at_event = get_group_allocations_for_event_active_cadets_only(
        object_store=object_store, event=event
    )
    cadets_in_group = all_group_allocations_at_event.cadets_in_group_during_event(group)
    cadets_in_group = cadets_in_group.sort_by_name()
    dict_of_cadets_with_qualifications_and_ticks = (
        get_dict_of_cadets_with_qualifications_and_ticks(
            object_store=object_store, list_of_cadet_ids=cadets_in_group.list_of_ids
        )
    )

    return dict_of_cadets_with_qualifications_and_ticks.subset_for_qualification(
        qualification
    )




def delete_ticks_for_cadet(
    interface: abstractInterface, cadet: Cadet, areyousure: bool = False
):
    if not areyousure:
        return

    interface.update(
        interface.object_store.data_api.data_list_of_cadets_with_tick_list_items.delete_ticks_for_cadet,
        cadet_id=cadet.id,
    )

def save_ticksheet_edits_for_specific_tick(
    interface: abstractInterface, new_tick: Tick, cadet: Cadet, tick_item: TickSheetItem
):
    interface.update(
        interface.object_store.data_api.data_list_of_cadets_with_tick_list_items.save_ticksheet_edits_for_specific_tick,
        cadet_id=cadet.id,
        tick_item_id=tick_item.id,
        new_tick=new_tick
    )



def get_dict_of_cadets_with_qualifications_and_ticks(
    object_store: ObjectStore, list_of_cadet_ids: List[str]
) -> DictOfCadetsWithQualificationsAndTicks:
    return object_store.get(
        object_store.data_api.data_list_of_cadets_with_tick_list_items.get_dict_of_cadets_with_qualifications_and_ticks,
        list_of_cadet_ids=list_of_cadet_ids
    )


