from dataclasses import dataclass
from typing import List

import pandas as pd

from app.backend.data.cadets import CadetData
from app.backend.data.cadets_at_event import CadetsAtEventData
from app.backend.data.group_allocations import GroupAllocationsData
from app.backend.data.qualification import QualificationData

from app.backend.data.security import SUPERUSER
from app.backend.data.ticksheets import TickSheetsData
from app.backend.data.volunteer_rota import VolunteerRotaData
from app.backend.events import get_sorted_list_of_events
from app.backend.ticks_and_qualifications.create_ticksheets import \
    get_ticksheet_for_cadets_in_group_at_event_for_qualification
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.events import Event, ListOfEvents
from app.objects.groups import Group
from app.backend.data.group_allocations import GroupAllocationsData
from app.objects.qualifications import Qualification, ListOfQualifications
from app.objects.ticks import LabelledTickSheetWithCadetIds, ListOfCadetsWithTickListItems, ListOfTickSheetItems, Tick


def get_list_of_groups_volunteer_id_can_see(interface: abstractInterface, event: Event, volunteer_id: str) -> List[Group]:
    can_see_all_groups = can_see_all_groups_and_award_qualifications(interface=interface, event=event, volunteer_id=volunteer_id)

    if can_see_all_groups:
        return get_list_of_all_groups_at_event(interface=interface, event=event)

    ## instructors
    volunteer_rota_data = VolunteerRotaData(interface.data)
    return volunteer_rota_data.get_list_of_groups_volunteer_is_instructor_for(event=event, volunteer_id=volunteer_id)

def can_see_all_groups_and_award_qualifications(interface: abstractInterface, event: Event, volunteer_id: str) -> bool:
    volunteer_rota_data = VolunteerRotaData(interface.data)
    is_senior_instructor_at_event = volunteer_rota_data.is_senior_instructor(event=event, volunteer_id=volunteer_id)
    is_superuser = volunteer_id == SUPERUSER

    return is_superuser or is_senior_instructor_at_event


def get_list_of_all_groups_at_event(interface: abstractInterface, event: Event) -> List[Group]:
    group_allocations_data = GroupAllocationsData(interface.data)
    return group_allocations_data.get_list_of_groups_at_event(event=event)

def get_list_of_events_entitled_to_see(interface: abstractInterface, volunteer_id: str, sort_by: str):
    all_events = get_sorted_list_of_events(interface, sort_by=sort_by)
    all_events = ListOfEvents([event for event in all_events if can_volunteer_id_see_event(interface=interface,
                                                                                           event=event,
                                                                                           volunteer_id=volunteer_id)])

    return all_events


def can_volunteer_id_see_event(interface: abstractInterface, event: Event, volunteer_id: str):
    if volunteer_id==SUPERUSER:
        return True

    list_of_groups = get_list_of_groups_volunteer_id_can_see(interface=interface, event=event, volunteer_id=volunteer_id)
    print("LIST FOR %s is %s" % (str(event), str(list_of_groups)) )
    return len(list_of_groups)>0


def align_center(x):
    return ['text-align: center' for _ in x]


def write_ticksheet_to_excel(labelled_ticksheet:LabelledTickSheetWithCadetIds, filename: str):
    title = labelled_ticksheet.qualification_name
    if len(title)==0:
        title = ' '
    df = labelled_ticksheet.df
    with pd.ExcelWriter(filename, engine='xlsxwriter') as writer:
        df.style.apply(align_center, axis=0).to_excel(
            writer,
            merge_cells=True,
            sheet_name=title
        )


def get_ticksheet_data(interface: abstractInterface, event: Event, group: Group, qualification: Qualification):
    tick_sheet_data = TickSheetsData(interface.data)
    qualifications_data = QualificationData(interface.data)

    tick_sheet = get_ticksheet_for_cadets_in_group_at_event_for_qualification(interface=interface, event=event, group=group, qualification_stage_id=qualification.id)

    list_of_tick_sheet_items_for_this_qualification = tick_sheet_data.list_of_tick_sheet_items_for_this_qualification(
        qualification.id)
    list_of_substage_names = tick_sheet_data.list_of_substage_names_give_list_of_tick_sheet_items(
        list_of_tick_sheet_items_for_this_qualification)

    list_of_cadet_ids_with_qualification = qualifications_data.list_of_cadet_ids_with_qualification(qualification)

    return TickSheetDataWithExtraInfo(
        tick_sheet=tick_sheet,
        qualification=qualification,
        list_of_substage_names=list_of_substage_names,
        list_of_tick_sheet_items_for_this_qualification=list_of_tick_sheet_items_for_this_qualification,
        list_of_cadet_ids_with_qualification=list_of_cadet_ids_with_qualification,
    )


@dataclass
class TickSheetDataWithExtraInfo:
    tick_sheet: ListOfCadetsWithTickListItems
    qualification: Qualification
    list_of_substage_names: List[str]
    list_of_tick_sheet_items_for_this_qualification: ListOfTickSheetItems
    list_of_cadet_ids_with_qualification: List[str]


def cadet_is_already_qualified(ticksheet_data: TickSheetDataWithExtraInfo,
                                   cadet_id: str) -> bool:

    already_qualified = cadet_id in ticksheet_data.list_of_cadet_ids_with_qualification

    return already_qualified


def save_ticksheet_edits_for_specific_tick(interface: abstractInterface, new_tick: Tick, cadet_id: str, item_id: str):
    ticksheet_data = TickSheetsData(interface.data)
    ticksheet_data.add_or_modify_specific_tick(cadet_id=cadet_id, item_id=item_id, new_tick=new_tick)


def get_expected_qualifications_for_cadets_at_event(interface: abstractInterface,
                                                    event: Event) -> pd.DataFrame:
    groups_data = GroupAllocationsData(interface.data)
    list_of_groups = groups_data.get_list_of_groups_at_event(event)
    list_of_cadets_at_event = groups_data.get_list_of_cadet_ids_with_groups_at_event(event)

    qualification_data = QualificationData(interface.data)
    list_of_qualifications = qualification_data.load_list_of_qualifications()


    list_of_expected_qualifications = []
    for group in list_of_groups:
        cadet_ids_this_group = []
        for day in event.weekdays_in_event():
            cadet_ids_this_group+=list_of_cadets_at_event.list_of_cadet_ids_in_group_on_day(group=group, day=day)

        cadet_ids_this_group = list(set(cadet_ids_this_group))

        list_of_expected_qualifications_for_group = [
            get_expected_qualifications_for_single_cadet(interface=interface,
                                                         cadet_id=cadet_id,
                                                         group=group,
                                                         list_of_qualifications=list_of_qualifications)

            for cadet_id in cadet_ids_this_group
            ]

        list_of_expected_qualifications+=list_of_expected_qualifications_for_group

    df= pd.DataFrame(list_of_expected_qualifications)
    df.columns = ['Name', 'Group']+list_of_qualifications.list_of_names()

    return df


def get_expected_qualifications_for_single_cadet(interface: abstractInterface, group: Group, cadet_id: str, list_of_qualifications: ListOfQualifications) -> list:

    cadet_data = CadetData(interface.data)

    list_of_cadets = cadet_data.get_list_of_cadets()

    cadet = list_of_cadets.cadet_with_id(cadet_id)
    tick_sheet_data = TickSheetsData(interface.data)
    tick_sheet_data.get_list_of_cadets_with_tick_list_items_for_cadet_id(cadet_id)

    percentage_list = [percentage_qualification_for_cadet_id_and_qualification_id(interface=interface,
                                                                                  cadet_id=cadet_id,
                                                                                  qualification_id=qualification_id)
                       for qualification_id in list_of_qualifications.list_of_ids]


    return [cadet.name, group.group_name]+ percentage_list

def percentage_qualification_for_cadet_id_and_qualification_id(interface: abstractInterface, cadet_id:str, qualification_id: str) -> str:
    qualification_data = QualificationData(interface.data)
    list_of_cadets_with_qualification = qualification_data.get_list_of_cadets_with_qualifications()

    qualifications_this_cadet = list_of_cadets_with_qualification.list_of_qualification_ids_for_cadet(cadet_id)

    if qualification_id in qualifications_this_cadet:
        return 'Qualified'

    tick_sheet_data = TickSheetsData(interface.data)
    tick_list = tick_sheet_data.get_list_of_cadets_with_tick_list_items_for_cadet_id(cadet_id)
    if len(tick_list)==0:
        return "0%"
    relevant_ids = tick_sheet_data.list_of_tick_sheet_items_for_this_qualification(qualification_id).list_of_ids
    tick_list_for_qualification = tick_list.subset_and_order_from_list_of_item_ids(relevant_ids)
    percentage_ticks_completed = tick_list_for_qualification[0].dict_of_ticks_with_items.percentage_complete()
    percentage_ticks_completed_as_number = int(100*percentage_ticks_completed)

    return "%d%%" % percentage_ticks_completed_as_number