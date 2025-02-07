from dataclasses import dataclass
from typing import List

from app.data_access.store.data_access import DataLayer


from app.objects.abstract_objects.abstract_interface import abstractInterface

from app.OLD_backend.data.dinghies import DinghiesData
from app.objects.day_selectors import Day
from app.objects.events import Event
from app.objects.cadet_at_event_with_boat_class_and_partners_with_ids import (
    CadetAtEventWithBoatClassAndPartnerWithIds,
    ListOfCadetAtEventWithBoatClassAndPartnerWithIds,
)
from app.objects.partners import no_partnership_given_partner_id_or_str
from app.backend.boat_classes.update_boat_information import \
    compare_list_of_cadets_with_dinghies_and_return_list_with_changed_values


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
    two_handed_partner_cadet_as_str: str


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
    list_of_updated_cadets: ListOfCadetAtEventWithBoatClassAndPartnerWithIds,
):
    dinghies_data = DinghiesData(interface.data)
    dinghies_data.update_boat_info_for_updated_cadets_at_event_where_cadets_available(
        event=event, list_of_updated_cadets=list_of_updated_cadets
    )


def convert_list_of_inputs_to_list_of_cadet_at_event_objects(
    interface: abstractInterface, list_of_updates: List[CadetWithDinghyInputs], day: Day
) -> ListOfCadetAtEventWithBoatClassAndPartnerWithIds:
    return ListOfCadetAtEventWithBoatClassAndPartnerWithIds(
        [
            convert_single_input_to_cadet_at_event(
                update=update, interface=interface, day=day
            )
            for update in list_of_updates
        ]
    )


def convert_single_input_to_cadet_at_event(
    interface: abstractInterface, update: CadetWithDinghyInputs, day: Day
) -> CadetAtEventWithBoatClassAndPartnerWithIds:
    boat_class_id = get_boat_class_id_from_name(
        interface=interface, boat_class_name=update.boat_class_name
    )

    two_handed_partner_id = get_two_handed_partner_id_from_str(
        data_layer=interface.data,
        two_handed_partner_cadet_as_str=update.two_handed_partner_cadet_as_str,
    )

    return CadetAtEventWithBoatClassAndPartnerWithIds(
        cadet_id=update.cadet_id,
        boat_class_id=boat_class_id,
        partner_cadet_id=two_handed_partner_id,
        sail_number=update.sail_number,
        day=day,
    )


def get_two_handed_partner_id_from_str(
    data_layer: DataLayer, two_handed_partner_cadet_as_str: str
):
    if no_partnership_given_partner_id_or_str(two_handed_partner_cadet_as_str):
        return two_handed_partner_cadet_as_str

    two_handed_partner = get_cadet_given_cadet_as_str(
        data_layer=data_layer, cadet_as_str=two_handed_partner_cadet_as_str
    )

    return two_handed_partner.id


from app.OLD_backend.cadets import get_cadet_given_cadet_as_str


def get_boat_class_id_from_name(interface: abstractInterface, boat_class_name: str):
    dinghy_data = DinghiesData(interface.data)
    list_of_boats = dinghy_data.get_list_of_boat_classes()
    boat_class_id = list_of_boats.id_given_name(boat_class_name)

    return boat_class_id


def load_list_of_cadets_at_event_with_dinghies(
    interface: abstractInterface, event: Event
) -> ListOfCadetAtEventWithBoatClassAndPartnerWithIds:
    dinghies_data = DinghiesData(interface.data)
    return dinghies_data.get_list_of_cadets_at_event_with_dinghies(event)
