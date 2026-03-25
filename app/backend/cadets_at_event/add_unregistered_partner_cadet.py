from typing import List

from app.backend.boat_classes.update_boat_information import link_two_cadets_in_new_partnership_return_message_if_fails
from app.backend.cadets_at_event.dict_of_all_cadet_at_event_data import get_dict_of_all_event_info_for_cadets
from app.backend.registration_data.cadet_registration_data import (
    add_new_cadet_to_event_from_row_in_registration_data,
)
from app.backend.registration_data.identified_cadets_at_event import (
    add_identified_cadet_and_row,
    get_row_in_registration_data_for_cadet_both_cancelled_and_active,
)
from app.backend.registration_data.raw_mapped_registration_data import (
    add_row_to_raw_mapped_registration_data,
)
from app.data_access.store.object_store import ObjectStore
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.cadets import Cadet
from app.objects.composed.cadets_at_event_with_boat_classes_groups_club_dnghies_and_partners import \
    CadetBoatClassClubDinghyGroupAndPartnerAtEventOnDay
from app.objects.composed.cadets_with_all_event_info import AllEventInfoForCadet
from app.objects.day_selectors import Day
from app.objects.events import Event
from app.objects.utilities.exceptions import NoMoreData
from app.objects.registration_data import (
    RowInRegistrationData,
    modify_row_to_clone_for_new_cadet_partner,
)
from app.backend.registration_data.cadet_registration_data import (
    get_registration_data_for_single_cadet_at_event,
)


def get_registered_two_handed_partner_name_for_cadet_at_event(
    object_store: ObjectStore, event: Event, cadet: Cadet
) -> str:
    cadet_at_event = get_registration_data_for_single_cadet_at_event(
        object_store=object_store, event=event, cadet=cadet
    )
    return cadet_at_event.two_handed_partner(default="")


def add_unregistered_partner_cadet(
    interface: abstractInterface,
    original_cadet: Cadet,
    new_cadet: Cadet,
    event: Event,
):
    print("Adding %s to registration data" % new_cadet)
    new_row = add_cloned_row_to_raw_registration_data_and_return_row(
        interface=interface,
        original_cadet=original_cadet,
        new_cadet=new_cadet,
        event=event,
    )

    print("Adding %s as idenitified cadet" % new_cadet)
    add_identified_cadet_and_row(
        interface=interface, event=event, row_id=new_row.row_id, cadet=new_cadet
    )

    print("Adding %s to event data" % new_cadet)
    add_new_cadet_to_event_from_row_in_registration_data(
        interface=interface,
        event=event,
        row_in_registration_data=new_row,
        cadet=new_cadet,
    )

    print("Adding %s as partner " % new_cadet)
    msgs = add_two_handed_partnership_for_new_cadet_modifies_groups_club_boats_class_returns_messages(
        interface=interface,
        event=event,
        original_cadet=original_cadet,
        new_cadet=new_cadet,
    )

    for msg in msgs:
        interface.log_error(msg)


def add_cloned_row_to_raw_registration_data_and_return_row(
    interface: abstractInterface, original_cadet: Cadet, new_cadet: Cadet, event: Event
) -> RowInRegistrationData:
    try:
        existing_row = get_row_in_registration_data_for_cadet_both_cancelled_and_active(
            object_store=interface.object_store,
            cadet=original_cadet,
            event=event,
            raise_error_on_duplicate=False,
        )
    except NoMoreData:
        print(
            "Event has probably been cleaned, original registration data not available"
        )

        existing_row = RowInRegistrationData()

    new_row = modify_row_to_clone_for_new_cadet_partner(
        original_cadet=original_cadet, new_cadet=new_cadet, existing_row=existing_row
    )
    add_row_to_raw_mapped_registration_data(
        interface=interface, event=event, row_in_registration_data=new_row
    )

    return new_row


def add_two_handed_partnership_for_new_cadet_modifies_groups_club_boats_class_returns_messages(
    interface: abstractInterface,
    event: Event,
    original_cadet: Cadet,
    new_cadet: Cadet,
) -> List[str]:
    ## We only need to include the original cadet as will copy over
    list_of_days = get_list_of_days_given_original_cadet(
        object_store=interface.object_store,
        event=event,
        original_cadet=original_cadet,
    )
    all_event_data = get_dict_of_all_event_info_for_cadets(object_store=interface.object_store, event=event)

    data_for_cadet= all_event_data.event_data_for_cadet(original_cadet)
    data_for_new_partner = all_event_data.event_data_for_cadet(new_cadet)

    msgs=[]
    for day in list_of_days:
        ## already partnered?
        if is_cadet_already_partnered_on_day(
            data_for_cadet=data_for_cadet, day=day
        ):
            msgs.append("Cadet %s is already partnered on %s, not adding new partner that day" % (original_cadet, day))
            continue

        if is_cadet_already_partnered_on_day(
            data_for_cadet=data_for_new_partner, day=day
        ):
            msgs.append("Cadet %s is already partnered on %s, not adding new partner that day" % (original_cadet, day.name))
            continue


        cadet_boat_class_group_club_dinghy_and_partner_on_day=CadetBoatClassClubDinghyGroupAndPartnerAtEventOnDay(
            day=day,
            cadet=original_cadet,
            partner_cadet=new_cadet,
            sail_number=data_for_cadet.days_and_boat_class.sail_number_on_day(day),
            club_dinghy=data_for_cadet.days_and_club_dinghies.dinghy_on_day(day),
            boat_class=data_for_cadet.days_and_boat_class.boat_class_on_day(day),
            group=data_for_cadet.days_and_groups.group_on_day(day)
        )
        print(cadet_boat_class_group_club_dinghy_and_partner_on_day)
        msg = link_two_cadets_in_new_partnership_return_message_if_fails(
            interface=interface,
            event=event,
            cadet_boat_class_group_club_dinghy_and_partner_on_day=cadet_boat_class_group_club_dinghy_and_partner_on_day
        )
        if len(msg)>0:
            msgs.append(msg)

    return msgs

def is_cadet_already_partnered_on_day(data_for_cadet: AllEventInfoForCadet, day: Day ):

    return data_for_cadet.days_and_boat_class.has_valid_partner_on_day(day)

def get_list_of_days_given_original_cadet(
    object_store: ObjectStore,
    event: Event,
    original_cadet: Cadet,
) -> List[Day]:
    registration_data = get_registration_data_for_single_cadet_at_event(
        object_store=object_store, event=event, cadet=original_cadet
    )
    list_of_days = registration_data.availability.days_available()

    return list_of_days


