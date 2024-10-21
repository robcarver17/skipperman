from dataclasses import dataclass
from typing import List, Dict

import pandas as pd
from app.objects.cadets import Cadet

from app.backend.groups.cadets_with_groups_at_event import get_group_allocations_for_event_active_cadets_only

from app.data_access.store.object_store import ObjectStore

from app.OLD_backend.data.qualification import QualificationData

from app.OLD_backend.data.ticksheets import TickSheetsData
from app.backend.qualifications_and_ticks.print_ticksheets import \
    get_ticksheet_for_cadets_in_group_at_event_for_qualification
from app.data_access.store.object_definitions import \
    object_definition_for_dict_of_cadet_ids_with_tick_list_items_for_cadet_id, \
    object_definition_for_dict_of_tick_list_items_with_cadet_id_as_key, \
    object_definition_for_dict_of_cadets_with_qualifications_and_ticks
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.composed.ticksheet import DictOfCadetsWithQualificationsAndTicks, \
    DictOfCadetsAndTicksWithinQualification
from app.objects.composed.ticks_for_qualification import DictOfCadetIdAndTicksWithItems
from app.objects.events import Event
from app.objects.groups import Group
from app.OLD_backend.data.group_allocations import GroupAllocationsData
from app.objects.qualifications import Qualification, ListOfQualifications
from app.objects.ticks import (
    ListOfCadetIdsWithTickListItemIds,
    Tick, )
from app.objects.substages import TickSheetItem, ListOfTickSheetItems
from app.objects.composed.labelled_tick_sheet import LabelledTickSheet


def get_ticksheet_data_for_cadets_at_event_in_group_with_qualification(
    object_store: ObjectStore,
    event: Event,
    group: Group,
    qualification: Qualification
) -> DictOfCadetsAndTicksWithinQualification:

    all_group_allocations_at_event = get_group_allocations_for_event_active_cadets_only(object_store=object_store, event=event)
    cadets_in_group = all_group_allocations_at_event.cadets_in_group_during_event(group)
    cadets_in_group = cadets_in_group.sort_by_firstname()
    dict_of_cadets_with_qualifications_and_ticks = get_dict_of_cadets_with_qualifications_and_ticks(object_store=object_store,
                                                                                                    list_of_cadet_ids=cadets_in_group.list_of_ids)

    return dict_of_cadets_with_qualifications_and_ticks.subset_for_qualification(qualification)

def get_dict_of_cadets_with_qualifications_and_ticks(object_store: ObjectStore,
                                                            list_of_cadet_ids: List[str]) -> DictOfCadetsWithQualificationsAndTicks:

    return object_store.get(
        object_definition=object_definition_for_dict_of_cadets_with_qualifications_and_ticks,
        list_of_cadet_ids=list_of_cadet_ids
    )

def update_dict_of_cadets_with_qualifications_and_ticks(object_store: ObjectStore,
                                                        new_dict_of_cadets_with_qualifications_and_ticks:  DictOfCadetsWithQualificationsAndTicks):

    list_of_cadet_ids = new_dict_of_cadets_with_qualifications_and_ticks.list_of_cadets.list_of_ids
    return object_store.update(
        object_definition=object_definition_for_dict_of_cadets_with_qualifications_and_ticks,
        list_of_cadet_ids=list_of_cadet_ids,
        new_object=new_dict_of_cadets_with_qualifications_and_ticks
    )



def get_dict_of_tick_list_items_with_cadet_id_as_key(object_store: ObjectStore,
                                                            list_of_cadet_ids = List[str]) -> DictOfCadetIdAndTicksWithItems:

    return object_store.get(object_definition_for_dict_of_tick_list_items_with_cadet_id_as_key,
                            list_of_cadet_ids=list_of_cadet_ids)


def get_dict_of_cadet_ids_with_tick_list_items_for_cadet_id(object_store: ObjectStore,
                                                            list_of_cadet_ids = List[str]) -> Dict[str, ListOfCadetIdsWithTickListItemIds]:

    return object_store.get(object_definition_for_dict_of_cadet_ids_with_tick_list_items_for_cadet_id, list_of_cadet_ids=list_of_cadet_ids)


### OLD CODE BELOW WILL PROBABLY REUSE

def align_center(x):
    return ["text-align: center" for _ in x]


def write_ticksheet_to_excel(
    labelled_ticksheet: LabelledTickSheet, filename: str
):
    title = labelled_ticksheet.qualification_name
    if len(title) == 0:
        title = " "
    df = labelled_ticksheet.df
    with pd.ExcelWriter(filename, engine="xlsxwriter") as writer:
        df.style.apply(align_center, axis=0).to_excel(
            writer, merge_cells=True, sheet_name=title
        )


@dataclass
class TickSheetDataWithExtraInfo:
    tick_sheet: ListOfCadetIdsWithTickListItemIds
    qualification: Qualification
    list_of_substage_names: List[str]
    list_of_tick_sheet_items_for_this_qualification: ListOfTickSheetItems
    list_of_cadet_ids_with_qualification: List[str]




def cadet_is_already_qualified(
    ticksheet_data: TickSheetDataWithExtraInfo, cadet_id: str
) -> bool:
    already_qualified = cadet_id in ticksheet_data.list_of_cadet_ids_with_qualification

    return already_qualified


def save_ticksheet_edits_for_specific_tick(
    object_store: ObjectStore, new_tick: Tick, cadet: Cadet,
        tick_item: TickSheetItem

):
    dict_of_cadets_with_qualifications_and_ticks = get_dict_of_cadets_with_qualifications_and_ticks(object_store=object_store,
                                                                                                    list_of_cadet_ids=[cadet.id])
    dict_of_cadets_with_qualifications_and_ticks.update_tick(
        cadet=cadet,
        tick_item=tick_item,
        new_tick=new_tick
    )
    update_dict_of_cadets_with_qualifications_and_ticks(
        new_dict_of_cadets_with_qualifications_and_ticks=dict_of_cadets_with_qualifications_and_ticks,
        object_store=object_store
    )

def get_expected_qualifications_for_cadets_at_event(
    interface: abstractInterface, event: Event
) -> pd.DataFrame:
    groups_data = GroupAllocationsData(interface.data)
    list_of_groups = groups_data.get_list_of_groups_at_event(event)
    list_of_cadets_at_event = groups_data.CONSIDER_USING_ACTIVE_FILTER_get_list_of_cadet_ids_with_groups_at_event(
        event
    )

    qualification_data = QualificationData(interface.data)
    list_of_qualifications = qualification_data.load_list_of_qualifications()

    list_of_expected_qualifications = []
    for group in list_of_groups:
        cadet_ids_this_group = []
        for day in event.weekdays_in_event():
            cadet_ids_this_group += (
                list_of_cadets_at_event.list_of_cadet_ids_in_group_on_day(
                    group=group, day=day
                )
            )

        cadet_ids_this_group = list(set(cadet_ids_this_group))

        list_of_expected_qualifications_for_group = [
            get_expected_qualifications_for_single_cadet_with_group(
                interface=interface,
                cadet_id=cadet_id,
                group=group,
                list_of_qualifications=list_of_qualifications,
            )
            for cadet_id in cadet_ids_this_group
        ]

        list_of_expected_qualifications += list_of_expected_qualifications_for_group

    df = pd.DataFrame(list_of_expected_qualifications)
    df.columns = ["Name", "Group"] + list_of_qualifications.list_of_names()

    return df


def get_qualification_status_for_single_cadet_as_list_of_str(
    interface: abstractInterface, cadet_id: str
) -> List[str]:
    qualification_status_for_single_cadet_as_dict = (
        get_qualification_status_for_single_cadet_as_dict(
            interface=interface, cadet_id=cadet_id
        )
    )

    list_of_qualificaitons = [
        report_on_status(qualification_name, percentage_str)
        for qualification_name, percentage_str in qualification_status_for_single_cadet_as_dict.items()
    ]
    list_of_qualificaitons = [
        item for item in list_of_qualificaitons if not no_progress(item)
    ]  ## exclude empty

    return list_of_qualificaitons


def no_progress(status_str):
    return len(status_str) == 0


def report_on_status(qualification_name: str, percentage: str) -> str:
    if percentage == QUALIFIED:
        return qualification_name
    elif percentage == EMPTY:
        return ""
    else:
        return "%s: %s" % (qualification_name, percentage)


def get_qualification_status_for_single_cadet_as_dict(
    interface: abstractInterface, cadet_id: str
) -> Dict[str, str]:
    qualification_data = QualificationData(interface.data)
    list_of_qualifications = qualification_data.load_list_of_qualifications()

    percentage_list = get_percentage_qualifications_for_single_cadet(
        interface=interface,
        cadet_id=cadet_id,
        list_of_qualifications=list_of_qualifications,
    )

    return dict(
        [
            (qualification.name, percentage_str)
            for qualification, percentage_str in zip(
                list_of_qualifications, percentage_list
            )
        ]
    )


from app.OLD_backend.cadets import cadet_name_from_id


def get_expected_qualifications_for_single_cadet_with_group(
    interface: abstractInterface,
    group: Group,
    cadet_id: str,
    list_of_qualifications: ListOfQualifications,
) -> List[str]:
    percentage_list = get_percentage_qualifications_for_single_cadet(
        interface=interface,
        cadet_id=cadet_id,
        list_of_qualifications=list_of_qualifications,
    )

    return [
        cadet_name_from_id(data_layer=interface.data, cadet_id=cadet_id),
        group.name,
    ] + percentage_list


def get_percentage_qualifications_for_single_cadet(
    interface: abstractInterface,
    cadet_id: str,
    list_of_qualifications: ListOfQualifications,
) -> List[str]:
    percentage_list = [
        percentage_qualification_for_cadet_id_and_qualification_id(
            interface=interface, cadet_id=cadet_id, qualification_id=qualification_id
        )
        for qualification_id in list_of_qualifications.list_of_ids
    ]

    return percentage_list


QUALIFIED = "Qualified"
EMPTY = "0%"


def percentage_qualification_for_cadet_id_and_qualification_id(
    interface: abstractInterface, cadet_id: str, qualification_id: str
) -> str:
    qualification_data = QualificationData(interface.data)
    list_of_cadets_with_qualification = (
        qualification_data.get_list_of_cadets_with_qualifications()
    )

    qualifications_this_cadet = (
        list_of_cadets_with_qualification.list_of_qualification_ids_for_cadet(cadet_id)
    )

    if qualification_id in qualifications_this_cadet:
        return QUALIFIED

    tick_sheet_data = TickSheetsData(interface.data)
    tick_list = tick_sheet_data.get_list_of_cadets_with_tick_list_items_for_cadet_id(
        cadet_id
    )
    if len(tick_list) == 0:
        return EMPTY
    relevant_ids = tick_sheet_data.list_of_tick_sheet_items_for_this_qualification(
        qualification_id
    ).list_of_ids
    tick_list_for_qualification = tick_list.subset_and_order_from_list_of_item_ids(
        relevant_ids
    )
    percentage_ticks_completed = tick_list_for_qualification[
        0
    ].dict_of_ticks_with_items.percentage_complete()
    percentage_ticks_completed_as_number = int(100 * percentage_ticks_completed)

    return "%d%%" % percentage_ticks_completed_as_number


