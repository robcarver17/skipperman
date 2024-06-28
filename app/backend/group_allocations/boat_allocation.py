import pandas as pd
from dataclasses import dataclass
from typing import List, Dict

from app.backend.cadets import DEPRECATE_load_list_of_all_cadets

from app.objects.abstract_objects.abstract_interface import abstractInterface

from app.backend.data.dinghies import DinghiesData
from app.backend.forms.summarys import summarise_generic_counts_for_event_over_days
from app.objects.abstract_objects.abstract_tables import PandasDFTable
from app.objects.day_selectors import DaySelector, Day
from app.objects.events import Event
from app.backend.data.cadets_at_event_id_level import CadetsAtEventIdLevelData
from app.objects.dinghies import (
    no_partnership,
    CadetAtEventWithDinghy,
    ListOfCadetAtEventWithDinghies,
    compare_list_of_cadets_with_dinghies_and_return_list_with_changed_values,
)
from app.objects.club_dinghies import ListOfCadetAtEventWithClubDinghies


def update_club_boat_allocation_for_cadet_at_event_on_day_if_cadet_available(
    interface: abstractInterface, boat_name: str, cadet_id: str, event: Event, day: Day
):
    dinghy_data = DinghiesData(interface.data)
    dinghy_data.update_club_boat_allocation_for_cadet_at_event_on_day_if_cadet_available(
        event=event, day=day, cadet_id=cadet_id, boat_name=boat_name
    )


@dataclass
class CadetWithDinghyInputs:
    cadet_id: str
    sail_number: str
    boat_class_name: str
    two_handed_partner_name: str


def update_boat_info_for_cadets_at_event(
    interface: abstractInterface,
    event: Event,
    list_of_updates: List[CadetWithDinghyInputs],
    day: Day,
):
    list_of_existing_cadets_at_event_with_dinghies = (
        load_list_of_cadets_at_event_with_dinghies(interface=interface, event=event)
    )

    list_of_potentially_updated_cadets_at_event = (
        convert_list_of_inputs_to_list_of_cadet_at_event_objects(
            list_of_updates=list_of_updates, interface=interface, day=day
        )
    )

    list_of_updated_cadets = (
        compare_list_of_cadets_with_dinghies_and_return_list_with_changed_values(
            new_list=list_of_potentially_updated_cadets_at_event,
            existing_list=list_of_existing_cadets_at_event_with_dinghies,
        )
    )

    update_boat_info_for_updated_cadets_at_event(
        event=event, list_of_updated_cadets=list_of_updated_cadets, interface=interface
    )


def update_boat_info_for_updated_cadets_at_event(
    interface: abstractInterface,
    event: Event,
    list_of_updated_cadets: ListOfCadetAtEventWithDinghies,
):
    dinghies_data = DinghiesData(interface.data)
    dinghies_data.update_boat_info_for_updated_cadets_at_event_where_cadets_available(
        event=event, list_of_updated_cadets=list_of_updated_cadets
    )


def convert_list_of_inputs_to_list_of_cadet_at_event_objects(
    interface: abstractInterface, list_of_updates: List[CadetWithDinghyInputs], day: Day
) -> ListOfCadetAtEventWithDinghies:
    return ListOfCadetAtEventWithDinghies(
        [
            convert_single_input_to_cadet_at_event(
                update=update, interface=interface, day=day
            )
            for update in list_of_updates
        ]
    )


def convert_single_input_to_cadet_at_event(
    interface: abstractInterface, update: CadetWithDinghyInputs, day: Day
) -> CadetAtEventWithDinghy:
    boat_class_id = get_boat_class_id_from_name(
        interface=interface, boat_class_name=update.boat_class_name
    )
    two_handed_partner_id = get_two_handed_partner_id_from_name(
        interface=interface, two_handed_partner_name=update.two_handed_partner_name
    )

    return CadetAtEventWithDinghy(
        cadet_id=update.cadet_id,
        boat_class_id=boat_class_id,
        partner_cadet_id=two_handed_partner_id,
        sail_number=update.sail_number,
        day=day,
    )


def get_two_handed_partner_id_from_name(
    interface: abstractInterface, two_handed_partner_name: str
):
    if no_partnership(two_handed_partner_name):
        return two_handed_partner_name

    list_of_cadets = DEPRECATE_load_list_of_all_cadets(interface)
    two_handed_partner_id = list_of_cadets.id_given_name(two_handed_partner_name)

    return two_handed_partner_id


def get_boat_class_id_from_name(interface: abstractInterface, boat_class_name: str):
    dinghy_data = DinghiesData(interface.data)
    list_of_boats = dinghy_data.get_list_of_boat_classes()
    boat_class_id = list_of_boats.id_given_name(boat_class_name)

    return boat_class_id


def summarise_club_boat_allocations_for_event(
    interface: abstractInterface, event: Event
) -> PandasDFTable:
    dinghies_data = DinghiesData(interface.data)
    cadets_at_event_data = CadetsAtEventIdLevelData(interface.data)

    cadets_with_club_dinghies_at_event = (
        dinghies_data.get_list_of_cadets_at_event_with_club_dinghies(event)
    )
    list_of_dinghy_ids = dinghies_data.unique_sorted_list_of_allocated_club_dinghy_ids_allocated_at_event(
        event
    )
    row_names = dinghies_data.sorted_list_of_names_of_allocated_club_dinghies(event)
    availability_dict = (
        cadets_at_event_data.get_availability_dict_for_active_cadet_ids_at_event(event)
    )

    table = summarise_generic_counts_for_event_over_days(
        get_id_function=get_relevant_cadet_ids_for_club_dinghy_id,
        event=event,
        groups=list_of_dinghy_ids,
        group_labels=row_names,
        availability_dict=availability_dict,
        list_of_ids_with_groups=cadets_with_club_dinghies_at_event,
    )

    return table


def get_relevant_cadet_ids_for_club_dinghy_id(
    group: str,
    event: Event,
    list_of_ids_with_groups: ListOfCadetAtEventWithClubDinghies,
) -> Dict[Day, List[str]]:
    ## map from generic to specific var names. Event is not used
    dinghy_id = group
    cadets_with_club_dinghies_at_event = list_of_ids_with_groups

    result_dict = {}
    for day in event.weekdays_in_event():
        result_dict[day] = [
            cadet_id
            for cadet_id in cadets_with_club_dinghies_at_event.list_of_unique_cadet_ids()
            if cadets_with_club_dinghies_at_event.dinghy_for_cadet_id_on_day(
                cadet_id=cadet_id, day=day
            )
            == dinghy_id
        ]

    return result_dict


def summarise_class_attendance_for_event(
    interface: abstractInterface, event: Event
) -> PandasDFTable:
    dinghies_data = DinghiesData(interface.data)
    cadets_at_event_data = CadetsAtEventIdLevelData(interface.data)

    cadets_with_dinghies_at_event = (
        dinghies_data.get_list_of_cadets_at_event_with_dinghies(event)
    )

    list_of_boat_class_ids = (
        dinghies_data.unique_sorted_list_of_boat_class_ids_at_event(event)
    )
    row_names = dinghies_data.sorted_list_of_names_of_dinghies_at_event(event)
    availability_dict = (
        cadets_at_event_data.get_availability_dict_for_active_cadet_ids_at_event(event)
    )

    table = summarise_generic_counts_for_event_over_days(
        get_id_function=get_relevant_cadet_ids_for_boat_class_id,
        event=event,
        groups=list_of_boat_class_ids,
        group_labels=row_names,
        availability_dict=availability_dict,
        list_of_ids_with_groups=cadets_with_dinghies_at_event,
    )

    return table


def get_relevant_cadet_ids_for_boat_class_id(
    group: str, event: Event, list_of_ids_with_groups: ListOfCadetAtEventWithDinghies
) -> Dict[Day, List[str]]:
    ## map from generic to specific var names. Event is not used
    boat_class_id = group
    cadets_with_dinghies_at_event = list_of_ids_with_groups

    result_dict = {}
    for day in event.weekdays_in_event():
        result_dict[day] = [
            cadet_id
            for cadet_id in cadets_with_dinghies_at_event.unique_list_of_cadet_ids()
            if cadets_with_dinghies_at_event.dinghy_id_for_cadet_id_on_day(
                cadet_id=cadet_id, day=day
            )
            == boat_class_id
        ]

    return result_dict


def load_list_of_cadets_at_event_with_dinghies(
    interface: abstractInterface, event: Event
) -> ListOfCadetAtEventWithDinghies:
    dinghies_data = DinghiesData(interface.data)
    return dinghies_data.get_list_of_cadets_at_event_with_dinghies(event)
