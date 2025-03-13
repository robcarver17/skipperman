from app.backend.groups.list_of_groups import get_group_with_name
from app.objects.boat_classes import BoatClass
from app.objects.club_dinghies import ClubDinghy, no_club_dinghy
from app.objects.composed.cadets_at_event_with_boat_classes_groups_club_dnghies_and_partners import (
    CadetBoatClassClubDinghyGroupAndPartnerAtEventOnDay,
    ListOfCadetBoatClassClubDinghyGroupAndPartnerAtEventOnDay,
)
from app.objects.composed.cadets_with_all_event_info import DictOfAllEventInfoForCadets
from app.objects.groups import unallocated_group, Group
from app.objects.partners import (
    no_partnership_given_partner_cadet_as_str,
    no_partnership_object_given_str,
)

from dataclasses import dataclass
from typing import List
from app.backend.cadets.list_of_cadets import (
    get_cadet_from_list_of_cadets_given_name_of_cadet,
)
from app.backend.boat_classes.list_of_boat_classes import (
    get_boat_class_from_name,
)
from app.backend.cadets_at_event.dict_of_all_cadet_at_event_data import (
    get_dict_of_all_event_info_for_cadets,
    update_dict_of_all_event_info_for_cadets,
)
from app.data_access.store.object_store import ObjectStore

from app.objects.cadets import Cadet
from app.objects.day_selectors import Day
from app.objects.events import Event
from app.objects.exceptions import missing_data, MISSING_FROM_FORM
from app.backend.registration_data.cadet_registration_data import (
    is_cadet_unavailable_on_day,
)
from app.objects.utils import print_list
from build.lib.app.objects.boat_classes import no_boat_class


@dataclass
class CadetWithDinghySailNumberBoatClassAndPartner:
    cadet: Cadet
    sail_number: str
    boat_class_name: str
    two_handed_partner_cadet_as_str: str
    group_name: str
    club_boat_name: str


def update_boat_class_sail_number_group_club_dinghy_and_partner_for_cadets_at_event(
    object_store: ObjectStore,
    event: Event,
    list_of_updates: List[CadetWithDinghySailNumberBoatClassAndPartner],
    day: Day,
):
    dict_of_all_event_info_for_cadets = get_dict_of_all_event_info_for_cadets(
        object_store=object_store, event=event
    )
    list_of_existing_cadets_boats_groups_club_dinghies_and_partners = dict_of_all_event_info_for_cadets.list_of_cadets_boat_classes_groups_sail_numbers_and_partners_at_event_on_day(
        day
    )
    print_list(
        list_of_existing_cadets_boats_groups_club_dinghies_and_partners, "Existing:"
    )

    list_of_potentially_updated_cadets_boats_groups_club_dinghies_and_partners = (
        convert_list_of_inputs_to_list_of_cadet_at_event_objects(
            list_of_updates=list_of_updates,
            object_store=object_store,
            day=day,
            dict_of_all_event_info_for_cadets=dict_of_all_event_info_for_cadets,
        )
    )
    print_list(
        list_of_potentially_updated_cadets_boats_groups_club_dinghies_and_partners,
        "Potential updates:",
    )

    list_of_updated_cadets_boats_groups_club_dinghies_and_partners = compare_list_of_cadets_with_dinghies_and_return_list_with_changed_values(
        new_list=list_of_potentially_updated_cadets_boats_groups_club_dinghies_and_partners,
        existing_list=list_of_existing_cadets_boats_groups_club_dinghies_and_partners,
    )

    print_list(
        list_of_updated_cadets_boats_groups_club_dinghies_and_partners,
        "Actual updates:",
    )

    update_boat_info_for_updated_cadets_at_event(
        object_store=object_store,
        event=event,
        list_of_updated_cadets_boats_groups_club_dinghies_and_partners=list_of_updated_cadets_boats_groups_club_dinghies_and_partners,
    )


def convert_list_of_inputs_to_list_of_cadet_at_event_objects(
    object_store: ObjectStore,
    dict_of_all_event_info_for_cadets: DictOfAllEventInfoForCadets,
    list_of_updates: List[CadetWithDinghySailNumberBoatClassAndPartner],
    day: Day,
) -> ListOfCadetBoatClassClubDinghyGroupAndPartnerAtEventOnDay:
    return ListOfCadetBoatClassClubDinghyGroupAndPartnerAtEventOnDay(
        [
            convert_single_input_to_cadet_with_class_and_partner_at_event(
                object_store=object_store,
                dict_of_all_event_info_for_cadets=dict_of_all_event_info_for_cadets,
                update=update,
                day=day,
            )
            for update in list_of_updates
        ]
    )


def convert_single_input_to_cadet_with_class_and_partner_at_event(
    object_store: ObjectStore,
    dict_of_all_event_info_for_cadets: DictOfAllEventInfoForCadets,
    update: CadetWithDinghySailNumberBoatClassAndPartner,
    day: Day,
) -> CadetBoatClassClubDinghyGroupAndPartnerAtEventOnDay:
    cadet = update.cadet

    boat_class = get_boat_class_from_str(
        object_store=object_store,
        dict_of_all_event_info_for_cadets=dict_of_all_event_info_for_cadets,
        update=update,
        day=day,
    )

    two_handed_partner = get_two_handed_partner_from_str(
        object_store=object_store,
        dict_of_all_event_info_for_cadets=dict_of_all_event_info_for_cadets,
        update=update,
        day=day,
    )
    sail_number = get_sail_number_from_str(
        dict_of_all_event_info_for_cadets=dict_of_all_event_info_for_cadets,
        update=update,
        day=day,
    )
    group = get_group_from_str(
        object_store=object_store,
        dict_of_all_event_info_for_cadets=dict_of_all_event_info_for_cadets,
        update=update,
        day=day,
    )
    club_dinghy = get_club_dinghy_from_str(
        object_store=object_store,
        dict_of_all_event_info_for_cadets=dict_of_all_event_info_for_cadets,
        update=update,
        day=day,
    )

    return CadetBoatClassClubDinghyGroupAndPartnerAtEventOnDay(
        cadet=cadet,
        boat_class=boat_class,
        partner_cadet=two_handed_partner,
        sail_number=sail_number,
        day=day,
        club_dinghy=club_dinghy,
        group=group,
    )


def get_boat_class_from_str(
    object_store: ObjectStore,
    dict_of_all_event_info_for_cadets: DictOfAllEventInfoForCadets,
    update: CadetWithDinghySailNumberBoatClassAndPartner,
    day: Day,
) -> BoatClass:

    if update.boat_class_name == MISSING_FROM_FORM:
        current_boat_class_partner_on_day = (
            get_current_boat_class_partner_on_day_for_update(
                dict_of_all_event_info_for_cadets=dict_of_all_event_info_for_cadets,
                update=update,
                day=day,
            )
        )
        boat_class = current_boat_class_partner_on_day.boat_class

    else:
        boat_class = get_boat_class_from_name(
            object_store=object_store,
            boat_class_name=update.boat_class_name,
            default=no_boat_class,
        )

    return boat_class


def get_current_boat_class_partner_on_day_for_update(
    dict_of_all_event_info_for_cadets: DictOfAllEventInfoForCadets,
    update: CadetWithDinghySailNumberBoatClassAndPartner,
    day: Day,
) -> CadetBoatClassClubDinghyGroupAndPartnerAtEventOnDay:
    cadet = update.cadet
    dict_of_cadets_and_boat_classes_and_partners_at_events = (
        dict_of_all_event_info_for_cadets.dict_of_cadets_and_boat_class_and_partners
    )
    current_boat_class_partner_on_day = dict_of_cadets_and_boat_classes_and_partners_at_events.boat_classes_and_partner_for_cadet(
        cadet
    ).boat_class_and_partner_on_day(
        day
    )

    return current_boat_class_partner_on_day


def get_two_handed_partner_from_str(
    object_store: ObjectStore,
    dict_of_all_event_info_for_cadets: DictOfAllEventInfoForCadets,
    update: CadetWithDinghySailNumberBoatClassAndPartner,
    day: Day,
) -> Cadet:

    two_handed_partner_cadet_as_str = update.two_handed_partner_cadet_as_str

    if two_handed_partner_cadet_as_str == MISSING_FROM_FORM:
        current_boat_class_partner_on_day = (
            get_current_boat_class_partner_on_day_for_update(
                dict_of_all_event_info_for_cadets=dict_of_all_event_info_for_cadets,
                update=update,
                day=day,
            )
        )
        two_handed_partner = current_boat_class_partner_on_day.partner_cadet

    else:
        two_handed_partner = get_two_handed_partner_from_str_in_form_not_missing(
            object_store=object_store,
            two_handed_partner_cadet_as_str=two_handed_partner_cadet_as_str,
        )

    return two_handed_partner


def get_two_handed_partner_from_str_in_form_not_missing(
    object_store: ObjectStore, two_handed_partner_cadet_as_str: str
) -> Cadet:

    if no_partnership_given_partner_cadet_as_str(two_handed_partner_cadet_as_str):
        return no_partnership_object_given_str(two_handed_partner_cadet_as_str)
    else:
        return get_cadet_from_list_of_cadets_given_name_of_cadet(
            object_store=object_store, cadet_selected=two_handed_partner_cadet_as_str
        )


def get_sail_number_from_str(
    dict_of_all_event_info_for_cadets: DictOfAllEventInfoForCadets,
    update: CadetWithDinghySailNumberBoatClassAndPartner,
    day: Day,
) -> str:

    if update.sail_number == MISSING_FROM_FORM:
        current_boat_class_partner_on_day = (
            get_current_boat_class_partner_on_day_for_update(
                dict_of_all_event_info_for_cadets=dict_of_all_event_info_for_cadets,
                update=update,
                day=day,
            )
        )
        sail_number = current_boat_class_partner_on_day.sail_number
    else:
        sail_number = str(update.sail_number)

    return sail_number


def get_group_from_str(
    object_store: ObjectStore,
    dict_of_all_event_info_for_cadets: DictOfAllEventInfoForCadets,
    update: CadetWithDinghySailNumberBoatClassAndPartner,
    day: Day,
) -> Group:
    group_name = update.group_name
    if group_name == MISSING_FROM_FORM:
        cadet = update.cadet
        group = dict_of_all_event_info_for_cadets.dict_of_cadets_with_days_and_groups.get_days_and_groups_for_cadet(
            cadet
        ).group_on_day(
            day
        )
    else:
        group = get_group_with_name(
            object_store=object_store, group_name=group_name, default=unallocated_group
        )

    return group


from app.backend.club_boats.list_of_club_dinghies import get_club_dinghy_with_name


def get_club_dinghy_from_str(
    object_store: ObjectStore,
    dict_of_all_event_info_for_cadets: DictOfAllEventInfoForCadets,
    update: CadetWithDinghySailNumberBoatClassAndPartner,
    day: Day,
) -> ClubDinghy:
    club_boat_name = update.club_boat_name
    if update.club_boat_name == MISSING_FROM_FORM:
        cadet = update.cadet
        club_boat = dict_of_all_event_info_for_cadets.dict_of_cadets_and_club_dinghies_at_event.club_dinghys_for_cadet(
            cadet
        ).dinghy_on_day(
            day
        )
    else:
        club_boat = get_club_dinghy_with_name(
            object_store=object_store, boat_name=club_boat_name, default=no_club_dinghy
        )

    return club_boat


def compare_list_of_cadets_with_dinghies_and_return_list_with_changed_values(
    new_list: ListOfCadetBoatClassClubDinghyGroupAndPartnerAtEventOnDay,
    existing_list: ListOfCadetBoatClassClubDinghyGroupAndPartnerAtEventOnDay,
):

    updated_list = ListOfCadetBoatClassClubDinghyGroupAndPartnerAtEventOnDay([])
    for potentially_updated_cadet_at_event_with_info in new_list:
        cadet_in_existing_list = existing_list.element_on_day_for_cadet(
            cadet=potentially_updated_cadet_at_event_with_info.cadet,
            day=potentially_updated_cadet_at_event_with_info.day,
            default=missing_data,
        )
        already_in_a_changed_partnership = is_cadet_already_in_changed_partnership(
            updated_list=updated_list,
            potentially_updated_cadet_at_event_with_info=potentially_updated_cadet_at_event_with_info,
        )
        if cadet_in_existing_list is not missing_data:
            if cadet_in_existing_list == potentially_updated_cadet_at_event_with_info:
                ## no change
                continue

        if already_in_a_changed_partnership:
            continue

        ## changed,  includes missing data
        updated_list.append(potentially_updated_cadet_at_event_with_info)

    return updated_list


def is_cadet_already_in_changed_partnership(
    updated_list: ListOfCadetBoatClassClubDinghyGroupAndPartnerAtEventOnDay,
    potentially_updated_cadet_at_event_with_info: CadetBoatClassClubDinghyGroupAndPartnerAtEventOnDay,
) -> bool:
    list_of_changed_partners = updated_list.list_of_valid_partners()
    cadet = potentially_updated_cadet_at_event_with_info.cadet
    changed = cadet in list_of_changed_partners

    return changed


def update_boat_info_for_updated_cadets_at_event(
    object_store: ObjectStore,
    event: Event,
    list_of_updated_cadets_boats_groups_club_dinghies_and_partners: ListOfCadetBoatClassClubDinghyGroupAndPartnerAtEventOnDay,
):
    dict_of_all_event_info_for_cadets = get_dict_of_all_event_info_for_cadets(
        object_store=object_store, event=event
    )

    for (
        cadet_boat_class_group_club_dinghy_and_partner_on_day
    ) in list_of_updated_cadets_boats_groups_club_dinghies_and_partners:
        dict_of_all_event_info_for_cadets.update_boat_info_for_updated_cadet_at_event(
            cadet_boat_class_group_club_dinghy_and_partner_on_day
        )

    update_dict_of_all_event_info_for_cadets(
        object_store=object_store,
        dict_of_all_event_info_for_cadets=dict_of_all_event_info_for_cadets,
    )
