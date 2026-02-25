from app.backend.boat_classes.cadets_with_boat_classes_at_event import \
    get_dict_of_cadets_and_boat_classes_and_partners_at_events
from app.backend.boat_classes.from_boat_update_with_str_to_update import \
    convert_list_of_inputs_to_list_of_cadet_at_event_objects
from app.backend.cadets_at_event.dict_of_all_cadet_at_event_data import get_dict_of_all_event_info_for_cadets
from app.backend.club_boats.cadets_with_club_dinghies_at_event import get_dict_of_cadets_and_club_dinghies_at_event
from app.backend.groups.cadets_with_groups_at_event import get_dict_of_cadets_with_groups_at_event
from app.backend.cadets_at_event.cadet_availability import get_attendance_matrix_for_cadets_at_event
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.boat_classes import BoatClass
from app.objects.composed.cadets_at_event_with_boat_classes_and_partners import DictOfCadetsAndBoatClassAndPartners
from app.objects.composed.cadets_at_event_with_boat_classes_groups_club_dnghies_and_partners import (
    CadetBoatClassClubDinghyGroupAndPartnerAtEventOnDay,
    ListOfCadetBoatClassClubDinghyGroupAndPartnerAtEventOnDay, CadetWithDinghySailNumberBoatClassAndPartner,
    compare_list_of_cadets_with_dinghies_and_return_list_with_changed_values, )
from app.objects.composed.cadets_at_event_with_groups import DictOfCadetsWithDaysAndGroupsAtEvent
from app.objects.composed.cadets_with_all_event_info_functions import RequiredDictForAllocation, \
    update_boat_info_for_updated_cadet_at_event_and_return_affected_cadets
from app.objects.composed.people_at_event_with_club_dinghies import DictOfPeopleAndClubDinghiesAtEvent
from app.objects.partners import (
    no_cadet_partner_required,
)

from typing import List, Union

from app.objects.cadets import Cadet, ListOfCadets
from app.objects.day_selectors import Day
from app.objects.events import Event
from app.objects.utilities.exceptions import missing_data

def update_boat_class_sail_number_group_club_dinghy_and_partner_for_cadets_at_event(
    interface: abstractInterface,
    event: Event,
    list_of_updates: List[CadetWithDinghySailNumberBoatClassAndPartner],
    day: Day,

) -> List[str]:
    object_store = interface.object_store
    dict_of_all_event_info_for_cadets = get_dict_of_all_event_info_for_cadets(object_store=object_store, event=event)
    list_of_existing_cadets_boats_groups_club_dinghies_and_partners = dict_of_all_event_info_for_cadets.list_of_cadets_boat_classes_groups_sail_numbers_and_partners_at_event_on_day(
        day
    )

    list_of_potentially_updated_cadets_boats_groups_club_dinghies_and_partners = (
        convert_list_of_inputs_to_list_of_cadet_at_event_objects(
            list_of_updates=list_of_updates,
            object_store=object_store,
            day=day,
            dict_of_all_event_info_for_cadets=dict_of_all_event_info_for_cadets,
        )
    )

    list_of_updated_cadets_boats_groups_club_dinghies_and_partners = compare_list_of_cadets_with_dinghies_and_return_list_with_changed_values(
        new_list=list_of_potentially_updated_cadets_boats_groups_club_dinghies_and_partners,
        existing_list=list_of_existing_cadets_boats_groups_club_dinghies_and_partners,
    )
    messages = update_boat_info_for_updated_cadets_at_event(
        interface=interface,
        event=event,
        list_of_updated_cadets_boats_groups_club_dinghies_and_partners=list_of_updated_cadets_boats_groups_club_dinghies_and_partners,

    )

    return messages


def update_boat_info_for_updated_cadets_at_event(
    interface: abstractInterface,
    event: Event,
    list_of_updated_cadets_boats_groups_club_dinghies_and_partners: ListOfCadetBoatClassClubDinghyGroupAndPartnerAtEventOnDay,

) -> List[str]:
    messages = []
    required_dict_for_allocation = RequiredDictForAllocation(
        dict_of_cadets_and_boat_class_and_partners=get_dict_of_cadets_and_boat_classes_and_partners_at_events(object_store=interface.object_store, event=event),
        dict_of_cadets_and_club_dinghies_at_event=get_dict_of_cadets_and_club_dinghies_at_event(object_store=interface.object_store, event=event),
        dict_of_cadets_with_days_and_groups=get_dict_of_cadets_with_groups_at_event(object_store=interface.object_store, event=event),
        availability_dict=get_attendance_matrix_for_cadets_at_event(object_store=interface.object_store, event=event),
    )

    for (
        cadet_boat_class_group_club_dinghy_and_partner_on_day
    ) in list_of_updated_cadets_boats_groups_club_dinghies_and_partners:
        warning_or_none = do_a_single_update_of_boat_info_for_updated_cadets_at_event(
            interface=interface,event=event,
            required_dict_for_allocation=required_dict_for_allocation,
            cadet_boat_class_group_club_dinghy_and_partner_on_day=cadet_boat_class_group_club_dinghy_and_partner_on_day
        )
        if warning_or_none is not None:
            messages.append(warning_or_none)

    return messages

def do_a_single_update_of_boat_info_for_updated_cadets_at_event(
    interface: abstractInterface,
required_dict_for_allocation: RequiredDictForAllocation,
    event: Event,
    cadet_boat_class_group_club_dinghy_and_partner_on_day: CadetBoatClassClubDinghyGroupAndPartnerAtEventOnDay,

) -> Union[str, None]:
    ## UPDATES CLUB DINGHIES, GROUPS AND CLASSES
    ## UPDATES PARTNERS WHERE AVAILABILITY ALIGNS

    required_dict_for_allocation = update_boat_info_for_updated_cadet_at_event_and_return_affected_cadets(
        cadet_boat_class_group_club_dinghy_and_partner_on_day=cadet_boat_class_group_club_dinghy_and_partner_on_day,
        required_dict_for_allocation=required_dict_for_allocation,

    )
    affected_cadets = required_dict_for_allocation.affected_cadets
    messages = required_dict_for_allocation.get_messages_or_none_and_clear()

    propagate_changes_to_list_of_cadets_in_underlying_data(
        interface=interface,
        event=event,
        day=cadet_boat_class_group_club_dinghy_and_partner_on_day.day,
        list_of_cadets=affected_cadets,
        required_dict_for_allocation=required_dict_for_allocation,

    )

    return messages

def propagate_changes_to_list_of_cadets_in_underlying_data(
    interface: abstractInterface, event: Event,
        day: Day,
        required_dict_for_allocation: RequiredDictForAllocation,
        list_of_cadets: ListOfCadets
):
    [
        propagate_changes_to_cadet_in_underlying_data(interface=interface, event=event,day=day,
                                                      required_dict_for_allocation=required_dict_for_allocation,
                                                      cadet=cadet)
        for cadet in list_of_cadets
    ]


def propagate_changes_to_cadet_in_underlying_data(interface: abstractInterface, event: Event,
                                                  day: Day,
                                                  cadet: Cadet,
                                                  required_dict_for_allocation: RequiredDictForAllocation):

    propagate_changes_to_club_dinghies_for_cadet_in_underlying_data(
        interface=interface,
        event=event,
        day=day,
        cadet=cadet,
        dict_of_cadets_and_club_dinghies_at_event=required_dict_for_allocation.dict_of_cadets_and_club_dinghies_at_event
    )
    propagate_changes_to_boat_class_and_partners_for_cadet_in_underlying_data(        interface=interface,
        event=event,
        day=day,
        cadet=cadet,
        dict_of_cadets_and_boat_class_and_partners=required_dict_for_allocation.dict_of_cadets_and_boat_class_and_partners
    )
    propagate_changes_to_days_and_groups_for_cadet_in_underlying_data(        interface=interface,
        event=event,
        day=day,
        cadet=cadet,
        dict_of_cadets_with_days_and_groups=required_dict_for_allocation.dict_of_cadets_with_days_and_groups
    )

def propagate_changes_to_club_dinghies_for_cadet_in_underlying_data(interface: abstractInterface, event: Event,
                                                  day: Day,
                                                  cadet: Cadet,
                                                  dict_of_cadets_and_club_dinghies_at_event: DictOfPeopleAndClubDinghiesAtEvent):

    club_dinghy = dict_of_cadets_and_club_dinghies_at_event.club_dinghys_for_person(cadet).dinghy_on_day(day)
    interface.update(
        interface.object_store.data_api.data_list_of_cadets_at_event_with_club_dinghies.update_or_add_cadet_with_club_dinghy_on_day,
        event_id=event.id,
        day=day,
        cadet_id=cadet.id,
        club_dinghy_id = club_dinghy

    )


def propagate_changes_to_boat_class_and_partners_for_cadet_in_underlying_data(interface: abstractInterface, event: Event,
                                                  day: Day,
                                                  cadet: Cadet,
                                                  dict_of_cadets_and_boat_class_and_partners: DictOfCadetsAndBoatClassAndPartners):

    boat_class_and_partner_on_day = dict_of_cadets_and_boat_class_and_partners.boat_classes_and_partner_for_cadet(cadet).boat_class_and_partner_on_day(day, default=missing_data)

    interface.update(
        interface.object_store.data_api.data_list_of_cadets_with_dinghies_at_event.update_or_add_boat_classes_and_partner_for_cadet,
        event_id = event.id,
        cadet_id = cadet.id,
        day=day,
        boat_class_id = boat_class_and_partner_on_day.boat_class.id,
        sail_number = boat_class_and_partner_on_day.sail_number,
        partner_id = boat_class_and_partner_on_day.partner_cadet.id
    )

class BoatClassAndPartnerAtEventOnDay:
    boat_class: BoatClass
    sail_number: str
    partner_cadet: Cadet = no_cadet_partner_required


def propagate_changes_to_days_and_groups_for_cadet_in_underlying_data(interface: abstractInterface, event: Event,
                                                  day: Day,
                                                  cadet: Cadet,
                                                  dict_of_cadets_with_days_and_groups: DictOfCadetsWithDaysAndGroupsAtEvent):

    group = dict_of_cadets_with_days_and_groups.days_and_groups_for_cadet(cadet).group_on_day(day)

    interface.update(
        interface.object_store.data_api.data_list_of_cadets_with_groups.update_or_add_cadet_in_group_on_day,
        event_id=event.id,
        cadet_id=cadet.id,
         day=day,
    group_id= group.id)


