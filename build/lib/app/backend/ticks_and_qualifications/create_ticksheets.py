from app.OLD_backend.data.ticksheets import TickSheetsData
from app.OLD_backend.data.group_allocations import GroupAllocationsData
from app.OLD_backend.data.cadets import CadetData
from app.OLD_backend.data.qualification import QualificationData

from app.objects.groups import Group

from app.objects.events import Event

from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.ticks import (
    ListOfCadetIdsWithTickListItemIds,
)
from app.objects.composed.labelled_tick_sheet import LabelledTickSheet


def get_labelled_ticksheet_df_for_group_at_event(
    interface: abstractInterface,
    event: Event,
    group: Group,
    qualification_stage_id: str,
    include_attendance_columns: bool = True,
    add_header: bool = True,
    sailors_in_columns: bool = True,
    asterix_club_boats: bool = True,
    medical_notes: bool = True,
) -> LabelledTickSheet:
    ticksheets_data = TickSheetsData(interface.data)

    labelled_ticksheet = (
        get_labelled_ticksheet_df_for_cadets_in_group_at_event_for_qualification(
            interface=interface,
            event=event,
            qualification_stage_id=qualification_stage_id,
            group=group,
        )
    )

    if add_header:
        labelled_ticksheet = labelled_ticksheet.add_qualification_and_group_header()
    if include_attendance_columns:
        labelled_ticksheet = ticksheets_data.add_attendance_data(
            event=event, group=group, labelled_ticksheet=labelled_ticksheet
        )
    if asterix_club_boats:
        labelled_ticksheet = ticksheets_data.add_club_boats(
            event=event, labelled_ticksheet=labelled_ticksheet
        )
    if medical_notes:
        labelled_ticksheet = ticksheets_data.add_medical_notes(
            event=event, labelled_ticksheet=labelled_ticksheet
        )

    if sailors_in_columns:
        labelled_ticksheet = labelled_ticksheet.transpose()

    return labelled_ticksheet


def get_labelled_ticksheet_df_for_cadets_in_group_at_event_for_qualification(
    interface: abstractInterface,
    event: Event,
    group: Group,
    qualification_stage_id: str,
) -> LabelledTickSheet:
    ticksheets_data = TickSheetsData(interface.data)
    cadet_data = CadetData(interface.data)
    qualification_data = QualificationData(interface.data)

    tick_sheet = get_ticksheet_for_cadets_in_group_at_event_for_qualification(
        interface=interface,
        event=event,
        group=group,
        qualification_stage_id=qualification_stage_id,
    )

    ordered_list_of_cadet_ids = tick_sheet.list_of_cadet_ids

    list_of_cadet_names_for_subset = (
        cadet_data.get_list_of_cadet_names_given_list_of_cadet_ids(
            ordered_list_of_cadet_ids
        )
    )

    list_of_tick_sheet_items_for_this_qualification = (
        ticksheets_data.list_of_tick_sheet_items_for_this_qualification(
            qualification_stage_id
        )
    )
    list_of_tick_item_names = (
        list_of_tick_sheet_items_for_this_qualification.list_of_item_names()
    )
    list_of_substage_names = (
        ticksheets_data.list_of_substage_names_give_list_of_tick_sheet_items(
            list_of_tick_sheet_items_for_this_qualification
        )
    )

    list_of_qualifications = qualification_data.load_list_of_qualifications()
    qualification_name = list_of_qualifications.name_given_id(qualification_stage_id)
    group_name = group.name

    labelled_ticksheet = tick_sheet.df_replacing_id_with_ordered_label_list(
        list_of_cadet_names=list_of_cadet_names_for_subset,
        list_of_tick_item_names=list_of_tick_item_names,
        list_of_substage_names=list_of_substage_names,
        qualification_name=qualification_name,
        group_name=group_name,
    )

    return labelled_ticksheet


def get_ticksheet_for_cadets_in_group_at_event_for_qualification(
    interface: abstractInterface,
    event: Event,
    group: Group,
    qualification_stage_id: str,
) -> ListOfCadetIdsWithTickListItemIds:
    ticksheets_data = TickSheetsData(interface.data)
    group_allocation_data = GroupAllocationsData(interface.data)
    cadet_data = CadetData(interface.data)

    list_of_cadet_ids = group_allocation_data.list_of_cadet_ids_in_a_specific_group_if_cadet_active_at_event(
        event=event, group=group
    )

    full_tick_sheet = (
        ticksheets_data.get_list_of_cadets_with_tick_list_items_for_list_of_cadets(
            list_of_cadet_ids=list_of_cadet_ids
        )
    )
    list_of_tick_sheet_items_for_this_qualification = (
        ticksheets_data.list_of_tick_sheet_items_for_this_qualification(
            qualification_stage_id
        )
    )
    ordered_list_of_cadet_ids = cadet_data.reorder_list_of_cadet_ids_by_cadet_name(
        list_of_cadet_ids
    )

    ## Will generate empty ticksheet row for missing cadet
    tick_sheet = full_tick_sheet.subset_from_list_of_cadet_ids(
        ordered_list_of_cadet_ids, generate_empty_row_if_missing=True
    )
    tick_sheet = tick_sheet.subset_and_order_from_list_of_tick_sheet_items(
        list_of_tick_sheet_items_for_this_qualification
    )
    tick_sheet = ticksheets_data.add_full_rows_where_cadet_has_qualifications(
        tick_sheet, qualification_stage_id=qualification_stage_id
    )

    return tick_sheet
