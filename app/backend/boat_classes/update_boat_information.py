from app.backend.boat_classes.from_boat_update_with_str_to_update import (
    convert_list_of_inputs_to_list_of_cadet_at_event_objects,
)
from app.backend.cadets_at_event.cadet_availability import (
    is_cadet_available_on_day_loading_all_event_data,
)
from app.backend.cadets_at_event.dict_of_all_cadet_at_event_data import (
    get_dict_of_all_event_info_for_cadets,
)
from app.backend.club_boats.cadets_with_club_dinghies_at_event import (
    add_club_dinghy_for_cadet_on_day,
)
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.composed.cadets_at_event_with_boat_classes_groups_club_dnghies_and_partners import (
    CadetBoatClassClubDinghyGroupAndPartnerAtEventOnDay,
    ListOfCadetBoatClassClubDinghyGroupAndPartnerAtEventOnDay,
    CadetWithDinghySailNumberBoatClassAndPartner,
    compare_list_of_cadets_with_dinghies_and_return_list_with_changed_values,
)
from app.objects.partners import (
    valid_partnership_given_partner_id_or_str,
    valid_partnership_given_partner_cadet,
)

from typing import List, Union

from app.objects.cadets import Cadet
from app.objects.day_selectors import Day
from app.objects.events import Event
from app.objects.utilities.utils import SimpleTimer


def update_boat_class_sail_number_group_club_dinghy_and_partner_for_cadets_at_event(
    interface: abstractInterface,
    event: Event,
    list_of_updates: List[CadetWithDinghySailNumberBoatClassAndPartner],
    day: Day,
) -> List[str]:
    object_store = interface.object_store
    st = SimpleTimer()
    dict_of_all_event_info_for_cadets = get_dict_of_all_event_info_for_cadets(
        object_store=object_store, event=event
    )
    st.elapsed("4: save get dict of all event info")
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
    st.elapsed("4: get list of potential updates")

    list_of_updated_cadets_boats_groups_club_dinghies_and_partners = compare_list_of_cadets_with_dinghies_and_return_list_with_changed_values(
        new_list=list_of_potentially_updated_cadets_boats_groups_club_dinghies_and_partners,
        existing_list=list_of_existing_cadets_boats_groups_club_dinghies_and_partners,
    )
    st.elapsed("4: do comparision")
    messages = update_boat_info_for_updated_cadets_at_event(
        interface=interface,
        event=event,
        list_of_updated_cadets_boats_groups_club_dinghies_and_partners=list_of_updated_cadets_boats_groups_club_dinghies_and_partners,
    )
    st.elapsed("4: do updates")

    return messages


def update_boat_info_for_updated_cadets_at_event(
    interface: abstractInterface,
    event: Event,
    list_of_updated_cadets_boats_groups_club_dinghies_and_partners: ListOfCadetBoatClassClubDinghyGroupAndPartnerAtEventOnDay,
) -> List[str]:
    messages = []

    for (
        cadet_boat_class_group_club_dinghy_and_partner_on_day
    ) in list_of_updated_cadets_boats_groups_club_dinghies_and_partners:
        warning_or_none = do_a_single_update_of_boat_info_for_updated_cadets_at_event(
            interface=interface,
            event=event,
            cadet_boat_class_group_club_dinghy_and_partner_on_day=cadet_boat_class_group_club_dinghy_and_partner_on_day,
        )
        if warning_or_none is not None:
            messages.append(warning_or_none)

    return messages


def do_a_single_update_of_boat_info_for_updated_cadets_at_event(
    interface: abstractInterface,
    event: Event,
    cadet_boat_class_group_club_dinghy_and_partner_on_day: CadetBoatClassClubDinghyGroupAndPartnerAtEventOnDay,
) -> Union[str, None]:
    if not is_primary_cadet_available_on_day(
        interface=interface,
        event=event,
        cadet_boat_class_group_club_dinghy_and_partner_on_day=cadet_boat_class_group_club_dinghy_and_partner_on_day,
    ):
        print("Primary cadet not available this day not changing")
        return

    print("")
    print(
        "Single update %s" % str(cadet_boat_class_group_club_dinghy_and_partner_on_day)
    )
    if existing_partnership(
        interface=interface,
        event=event,
        cadet_boat_class_group_club_dinghy_and_partner_on_day=cadet_boat_class_group_club_dinghy_and_partner_on_day,
    ):
        write_changes_to_cadets_in_existing_partnership(
            interface=interface,
            event=event,
            cadet_boat_class_group_club_dinghy_and_partner_on_day=cadet_boat_class_group_club_dinghy_and_partner_on_day,
        )

    elif valid_partnership_given_partner_cadet(
        cadet_boat_class_group_club_dinghy_and_partner_on_day.partner_cadet
    ):
        ## Must be new partnership since not existing
        link_two_cadets_in_new_partnership_return_message_if_fails(
            interface=interface,
            event=event,
            cadet_boat_class_group_club_dinghy_and_partner_on_day=cadet_boat_class_group_club_dinghy_and_partner_on_day,
        )

    else:
        write_changes_to_single_cadet(
            interface=interface,
            event=event,
            cadet_boat_class_group_club_dinghy_and_partner_on_day=cadet_boat_class_group_club_dinghy_and_partner_on_day,
        )

    return None


def link_two_cadets_in_new_partnership_return_message_if_fails(
    interface: abstractInterface,
    event: Event,
    cadet_boat_class_group_club_dinghy_and_partner_on_day: CadetBoatClassClubDinghyGroupAndPartnerAtEventOnDay,
):
    print(
        "New partnership %s"
        % str(cadet_boat_class_group_club_dinghy_and_partner_on_day)
    )

    if not both_cadets_available_on_this_day(
        interface,
        event=event,
        cadet_boat_class_group_club_dinghy_and_partner_on_day=cadet_boat_class_group_club_dinghy_and_partner_on_day,
    ):
        return (
            "Can't link %s and %s on %s as one or both sailors unavailable that day"
            % (
                cadet_boat_class_group_club_dinghy_and_partner_on_day.partner_cadet,
                cadet_boat_class_group_club_dinghy_and_partner_on_day.cadet,
                cadet_boat_class_group_club_dinghy_and_partner_on_day.day.name,
            )
        )

    ## so copy works when we create the partnership
    print("writing first cadet")
    write_changes_to_single_cadet(
        interface=interface,
        event=event,
        cadet_boat_class_group_club_dinghy_and_partner_on_day=cadet_boat_class_group_club_dinghy_and_partner_on_day,
    )
    join_two_cadets_in_new_partnership_after_making_changes(
        interface=interface,
        event=event,
        day=cadet_boat_class_group_club_dinghy_and_partner_on_day.day,
        cadet=cadet_boat_class_group_club_dinghy_and_partner_on_day.cadet,
        partner_cadet=cadet_boat_class_group_club_dinghy_and_partner_on_day.partner_cadet,
    )
    print(
        "writing second cadet %s"
        % cadet_boat_class_group_club_dinghy_and_partner_on_day.switch_partner()
    )
    write_changes_to_single_cadet(
        interface=interface,
        event=event,
        cadet_boat_class_group_club_dinghy_and_partner_on_day=cadet_boat_class_group_club_dinghy_and_partner_on_day.switch_partner(),
    )

    return ""


def both_cadets_available_on_this_day(
    interface: abstractInterface,
    event: Event,
    cadet_boat_class_group_club_dinghy_and_partner_on_day: CadetBoatClassClubDinghyGroupAndPartnerAtEventOnDay,
):
    cadet = cadet_boat_class_group_club_dinghy_and_partner_on_day.cadet
    partner_cadet = cadet_boat_class_group_club_dinghy_and_partner_on_day.partner_cadet
    day = cadet_boat_class_group_club_dinghy_and_partner_on_day.day

    av_first = is_cadet_available_on_day_loading_all_event_data(
        object_store=interface.object_store, event=event, cadet=cadet, day=day
    )
    av_second = is_cadet_available_on_day_loading_all_event_data(
        object_store=interface.object_store, event=event, cadet=partner_cadet, day=day
    )

    return av_first and av_second


def join_two_cadets_in_new_partnership_after_making_changes(
    interface: abstractInterface,
    event: Event,
    cadet: Cadet,
    partner_cadet: Cadet,
    day: Day,
):
    print("joining %s %s on %s " % (cadet, partner_cadet, day))
    interface.update(
        interface.object_store.data_api.data_list_of_cadets_with_dinghies_at_event.add_two_handed_partnership_on_day_for_new_cadet_when_have_dinghy_for_existing_cadet,
        event_id=event.id,
        original_cadet_id=cadet.id,
        new_cadet_id=partner_cadet.id,
        day=day,
    )


def existing_partnership(
    interface: abstractInterface,
    event: Event,
    cadet_boat_class_group_club_dinghy_and_partner_on_day: CadetBoatClassClubDinghyGroupAndPartnerAtEventOnDay,
):
    data_with_ids = interface.object_store.data_api.data_list_of_cadets_with_dinghies_at_event.get_cadet_at_event_with_boat_class_and_partner_with_ids(
        event_id=event.id,
        cadet_id=cadet_boat_class_group_club_dinghy_and_partner_on_day.cadet.id,
        day=cadet_boat_class_group_club_dinghy_and_partner_on_day.day,
        default=None,
    )
    if data_with_ids is None:
        return False
    existing = valid_partnership_given_partner_id_or_str(data_with_ids.partner_cadet_id)

    return existing


def write_changes_to_cadets_in_existing_partnership(
    interface: abstractInterface,
    event: Event,
    cadet_boat_class_group_club_dinghy_and_partner_on_day: CadetBoatClassClubDinghyGroupAndPartnerAtEventOnDay,
):
    if not both_cadets_available_on_this_day(
        interface=interface,
        event=event,
        cadet_boat_class_group_club_dinghy_and_partner_on_day=cadet_boat_class_group_club_dinghy_and_partner_on_day,
    ):
        print("No changes can be made to existing partnership as not both available")
        return

    print("Existing partnership writing individual changes")
    write_changes_to_single_cadet(
        interface=interface,
        event=event,
        cadet_boat_class_group_club_dinghy_and_partner_on_day=cadet_boat_class_group_club_dinghy_and_partner_on_day,
    )

    write_changes_to_single_cadet(
        interface=interface,
        event=event,
        cadet_boat_class_group_club_dinghy_and_partner_on_day=cadet_boat_class_group_club_dinghy_and_partner_on_day.switch_partner(),
    )


def breakup_partnership(
    interface: abstractInterface, event: Event, cadet: Cadet, list_of_days: List[Day]
):
    for day in list_of_days:
        interface.update(
            interface.object_store.data_api.data_list_of_cadets_with_dinghies_at_event.breakup_partnership_with_cadet_on_day,
            event_id=event.id,
            existing_cadet_id=cadet.id,
            day=day,
        )


def write_changes_to_single_cadet(
    interface: abstractInterface,
    event: Event,
    cadet_boat_class_group_club_dinghy_and_partner_on_day: CadetBoatClassClubDinghyGroupAndPartnerAtEventOnDay,
):
    print(
        "changes to single cadet %s "
        % cadet_boat_class_group_club_dinghy_and_partner_on_day
    )

    propagate_changes_to_club_dinghies_for_cadet_in_underlying_data(
        interface=interface,
        event=event,
        cadet_boat_class_group_club_dinghy_and_partner_on_day=cadet_boat_class_group_club_dinghy_and_partner_on_day,
    )
    propagate_changes_to_boat_class_and_sail_number_but_not_partners_for_cadet_in_underlying_data(
        interface=interface,
        event=event,
        cadet_boat_class_group_club_dinghy_and_partner_on_day=cadet_boat_class_group_club_dinghy_and_partner_on_day,
    )
    propagate_changes_to_days_and_groups_for_cadet_in_underlying_data(
        interface=interface,
        event=event,
        cadet_boat_class_group_club_dinghy_and_partner_on_day=cadet_boat_class_group_club_dinghy_and_partner_on_day,
    )


def is_primary_cadet_available_on_day(
    interface: abstractInterface,
    event: Event,
    cadet_boat_class_group_club_dinghy_and_partner_on_day: CadetBoatClassClubDinghyGroupAndPartnerAtEventOnDay,
):
    return is_cadet_available_on_day_loading_all_event_data(
        object_store=interface.object_store,
        event=event,
        cadet=cadet_boat_class_group_club_dinghy_and_partner_on_day.cadet,
        day=cadet_boat_class_group_club_dinghy_and_partner_on_day.day,
    )


def propagate_changes_to_club_dinghies_for_cadet_in_underlying_data(
    interface: abstractInterface,
    event: Event,
    cadet_boat_class_group_club_dinghy_and_partner_on_day: CadetBoatClassClubDinghyGroupAndPartnerAtEventOnDay,
):
    add_club_dinghy_for_cadet_on_day(
        interface=interface,
        event=event,
        cadet=cadet_boat_class_group_club_dinghy_and_partner_on_day.cadet,
        club_dinghy=cadet_boat_class_group_club_dinghy_and_partner_on_day.club_dinghy,
        day=cadet_boat_class_group_club_dinghy_and_partner_on_day.day,
    )


def propagate_changes_to_boat_class_and_sail_number_but_not_partners_for_cadet_in_underlying_data(
    interface: abstractInterface,
    event: Event,
    cadet_boat_class_group_club_dinghy_and_partner_on_day: CadetBoatClassClubDinghyGroupAndPartnerAtEventOnDay,
):
    print("propogating %s" % cadet_boat_class_group_club_dinghy_and_partner_on_day)
    interface.update(
        interface.object_store.data_api.data_list_of_cadets_with_dinghies_at_event.update_or_add_boat_classes_and_sail_number_not_not_partner_for_cadet,
        event_id=event.id,
        cadet_id=cadet_boat_class_group_club_dinghy_and_partner_on_day.cadet.id,
        day=cadet_boat_class_group_club_dinghy_and_partner_on_day.day,
        boat_class_id=cadet_boat_class_group_club_dinghy_and_partner_on_day.boat_class.id,
        sail_number=cadet_boat_class_group_club_dinghy_and_partner_on_day.sail_number,
    )


def propagate_changes_to_days_and_groups_for_cadet_in_underlying_data(
    interface: abstractInterface,
    event: Event,
    cadet_boat_class_group_club_dinghy_and_partner_on_day: CadetBoatClassClubDinghyGroupAndPartnerAtEventOnDay,
):
    interface.update(
        interface.object_store.data_api.data_list_of_cadets_with_groups.update_or_add_cadet_in_group_on_day,
        event_id=event.id,
        cadet_id=cadet_boat_class_group_club_dinghy_and_partner_on_day.cadet.id,
        day=cadet_boat_class_group_club_dinghy_and_partner_on_day.day,
        group_id=cadet_boat_class_group_club_dinghy_and_partner_on_day.group.id,
    )
