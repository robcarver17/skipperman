from typing import List

from app.objects.cadets import Cadet

from app.backend.groups.cadets_with_groups_at_event import (
    get_group_allocations_for_event_active_cadets_only,
)

from app.data_access.store.object_store import ObjectStore

from app.data_access.store.object_definitions import (
    object_definition_for_dict_of_cadets_with_qualifications_and_ticks,
)
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


def save_ticksheet_edits_for_specific_tick(
    object_store: ObjectStore, new_tick: Tick, cadet: Cadet, tick_item: TickSheetItem
):
    dict_of_cadets_with_qualifications_and_ticks = (
        get_dict_of_cadets_with_qualifications_and_ticks(
            object_store=object_store, list_of_cadet_ids=[cadet.id]
        )
    )
    dict_of_cadets_with_qualifications_and_ticks.update_tick(
        cadet=cadet, tick_item=tick_item, new_tick=new_tick
    )
    update_dict_of_cadets_with_qualifications_and_ticks(
        new_dict_of_cadets_with_qualifications_and_ticks=dict_of_cadets_with_qualifications_and_ticks,
        object_store=object_store,
    )


def get_ticksheet_data_for_cadets_at_event_in_group_with_qualification(
    object_store: ObjectStore, event: Event, group: Group, qualification: Qualification
) -> DictOfCadetsAndTicksWithinQualification:
    all_group_allocations_at_event = get_group_allocations_for_event_active_cadets_only(
        object_store=object_store, event=event
    )
    cadets_in_group = all_group_allocations_at_event.cadets_in_group_during_event(group)
    cadets_in_group = cadets_in_group.sort_by_firstname()
    dict_of_cadets_with_qualifications_and_ticks = (
        get_dict_of_cadets_with_qualifications_and_ticks(
            object_store=object_store, list_of_cadet_ids=cadets_in_group.list_of_ids
        )
    )

    return dict_of_cadets_with_qualifications_and_ticks.subset_for_qualification(
        qualification
    )


def get_dict_of_cadets_with_qualifications_and_ticks(
    object_store: ObjectStore, list_of_cadet_ids: List[str]
) -> DictOfCadetsWithQualificationsAndTicks:
    return object_store.get(
        object_definition=object_definition_for_dict_of_cadets_with_qualifications_and_ticks,
        list_of_cadet_ids=list_of_cadet_ids,
    )


def update_dict_of_cadets_with_qualifications_and_ticks(
    object_store: ObjectStore,
    new_dict_of_cadets_with_qualifications_and_ticks: DictOfCadetsWithQualificationsAndTicks,
):
    list_of_cadet_ids = (
        new_dict_of_cadets_with_qualifications_and_ticks.list_of_cadets.list_of_ids
    )
    return object_store.update(
        object_definition=object_definition_for_dict_of_cadets_with_qualifications_and_ticks,
        list_of_cadet_ids=list_of_cadet_ids,
        new_object=new_dict_of_cadets_with_qualifications_and_ticks,
    )
