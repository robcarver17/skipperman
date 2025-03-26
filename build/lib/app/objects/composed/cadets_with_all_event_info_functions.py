from dataclasses import dataclass
from typing import Union, Dict

from app.objects.cadets import ListOfCadets, Cadet
from app.objects.composed.cadets_at_event_with_boat_classes_and_partners import (
    DictOfCadetsAndBoatClassAndPartners,
)
from app.objects.composed.cadets_at_event_with_boat_classes_groups_club_dnghies_and_partners import (
    CadetBoatClassClubDinghyGroupAndPartnerAtEventOnDay,
    are_partners_equal,
)
from app.objects.composed.cadets_at_event_with_club_dinghies import (
    DictOfCadetsAndClubDinghiesAtEvent,
)
from app.objects.composed.cadets_at_event_with_groups import (
    DictOfCadetsWithDaysAndGroupsAtEvent,
)
from app.objects.composed.cadets_at_event_with_registration_data import (
    DictOfCadetsWithRegistrationData,
)
from app.objects.day_selectors import Day, DaySelector
from app.objects.groups import unallocated_group
from app.objects.partners import valid_partnership_given_partner_cadet, NoCadetPartner


def cadets_not_allocated_to_group_on_at_least_one_day_attending(
    dict_of_cadets_with_registration_data: DictOfCadetsWithRegistrationData,
    dict_of_cadets_with_days_and_groups: DictOfCadetsWithDaysAndGroupsAtEvent,
) -> ListOfCadets:

    list_of_cadets = []
    for cadet in dict_of_cadets_with_registration_data.list_of_cadets():
        if cadet_is_not_allocated_to_group_on_at_least_one_day_attending(
            cadet=cadet,
            dict_of_cadets_with_registration_data=dict_of_cadets_with_registration_data,
            dict_of_cadets_with_days_and_groups=dict_of_cadets_with_days_and_groups,
        ):
            list_of_cadets.append(cadet)

    return ListOfCadets(list_of_cadets)


def cadet_is_not_allocated_to_group_on_at_least_one_day_attending(
    cadet: Cadet,
    dict_of_cadets_with_registration_data: DictOfCadetsWithRegistrationData,
    dict_of_cadets_with_days_and_groups: DictOfCadetsWithDaysAndGroupsAtEvent,
) -> bool:

    availability = dict_of_cadets_with_registration_data.registration_data_for_cadet(
        cadet
    ).availability
    days_when_cadet_is_available = availability.days_available()
    for day in days_when_cadet_is_available:
        days_and_groups = (
            dict_of_cadets_with_days_and_groups.get_days_and_groups_for_cadet(cadet)
        )
        group_on_day = days_and_groups.group_on_day(day)
        if group_on_day is unallocated_group:
            return True

    return False


@dataclass
class PartnershipChange:
    cadet: Cadet
    day: Day
    original_partner: Union[Cadet, NoCadetPartner]
    new_partner: Union[Cadet, NoCadetPartner]
    new_partner_who_was_their_partner: Union[Cadet, NoCadetPartner] = None

    @property
    def had_no_partner_and_still_doesnt(self):
        if self.now_has_partner or self.did_have_partner:
            return False

        return True

    @property
    def has_unchanged_partner(self):
        return self.did_have_partner and self.now_has_partner and self.original_partner == self.new_partner


    @property
    def had_partner_and_now_does_not(self):
        return self.did_have_partner and (not self.now_has_partner)

    @property
    def unchanged(self):
        return are_partners_equal(self.original_partner, self.new_partner)

    @property
    def now_has_partner(self):
        return valid_partnership_given_partner_cadet(self.new_partner)

    @property
    def did_have_partner(self):
        return valid_partnership_given_partner_cadet(self.original_partner)

    @property
    def new_partner_had_partner(self):
        if self.new_partner_who_was_their_partner is None:
            return False
        return valid_partnership_given_partner_cadet(
            self.new_partner_who_was_their_partner
        )


@dataclass
class RequiredDictForAllocation:
    dict_of_cadets_and_boat_class_and_partners: DictOfCadetsAndBoatClassAndPartners
    dict_of_cadets_and_club_dinghies_at_event: DictOfCadetsAndClubDinghiesAtEvent
    dict_of_cadets_with_days_and_groups: DictOfCadetsWithDaysAndGroupsAtEvent
    availability_dict: Dict[Cadet, DaySelector]


def update_boat_info_for_updated_cadet_at_event_and_return_affected_cadets(
    required_dict_for_allocation: RequiredDictForAllocation,
    cadet_boat_class_group_club_dinghy_and_partner_on_day: CadetBoatClassClubDinghyGroupAndPartnerAtEventOnDay,
) -> ListOfCadets:


    if availability_is_bad_for_sailor_or_partner(
        required_dict_for_allocation=required_dict_for_allocation,
        cadet_boat_class_group_club_dinghy_and_partner_on_day=cadet_boat_class_group_club_dinghy_and_partner_on_day,
    ):
        print(
            "Availablity is bad - not updating %s"
            % cadet_boat_class_group_club_dinghy_and_partner_on_day
        )
        return ListOfCadets.create_empty()

    cadet = update_cadets_own_info_excluding_partner_and_return_cadet(
        required_dict_for_allocation=required_dict_for_allocation,
        cadet_boat_class_group_club_dinghy_and_partner_on_day=cadet_boat_class_group_club_dinghy_and_partner_on_day,
    )

    modified_cadet_partners = update_partnership_info_for_updated_cadet_at_event_and_return_affected_cadets(
        required_dict_for_allocation=required_dict_for_allocation,
        cadet_boat_class_group_club_dinghy_and_partner_on_day=cadet_boat_class_group_club_dinghy_and_partner_on_day,
    )
    modified_cadets = [cadet]+modified_cadet_partners
    unique_list_of_modified_cadets = ListOfCadets(list(set(modified_cadets)))

    return unique_list_of_modified_cadets


def availability_is_bad_for_sailor_or_partner(
    required_dict_for_allocation: RequiredDictForAllocation,
    cadet_boat_class_group_club_dinghy_and_partner_on_day: CadetBoatClassClubDinghyGroupAndPartnerAtEventOnDay,
) -> bool:
    cadet = cadet_boat_class_group_club_dinghy_and_partner_on_day.cadet
    partner_cadet = cadet_boat_class_group_club_dinghy_and_partner_on_day.partner_cadet
    day = cadet_boat_class_group_club_dinghy_and_partner_on_day.day

    cadet_availability = required_dict_for_allocation.availability_dict[cadet]

    if not cadet_availability.available_on_day(day):
        print("Cadet %s not available on %s" % (cadet, day.name))
        return True

    if valid_partnership_given_partner_cadet(partner_cadet):
        partner_availabilty = required_dict_for_allocation.availability_dict[
            partner_cadet
        ]
        if not partner_availabilty.available_on_day(day):
            print("Partner %s not available on %s" % (cadet, day.name))
            return True

    return False


def update_partnership_info_for_updated_cadet_at_event_and_return_affected_cadets(
    required_dict_for_allocation: RequiredDictForAllocation,
    cadet_boat_class_group_club_dinghy_and_partner_on_day: CadetBoatClassClubDinghyGroupAndPartnerAtEventOnDay,
) -> ListOfCadets:

    how_changed = how_has_partnership_changed(
        dict_of_cadets_and_boat_class_and_partners=required_dict_for_allocation.dict_of_cadets_and_boat_class_and_partners,
        cadet_boat_class_group_club_dinghy_and_partner_on_day=cadet_boat_class_group_club_dinghy_and_partner_on_day,
    )

    if how_changed.unchanged:
        if how_changed.has_unchanged_partner:
            ## Ensure changes are in synch
            partner = clone_cadet_group_club_dinghy_boat_class_sail_number_to_partner_and_return_partner(
                required_dict_for_allocation=required_dict_for_allocation,
                cadet_boat_class_group_club_dinghy_and_partner_on_day=cadet_boat_class_group_club_dinghy_and_partner_on_day,
            )
            affected_partners = [partner]
        else:
            affected_partners = []

    elif how_changed.had_no_partner_and_still_doesnt:
        ## change only this cadet, change of state from singlehanded to not allocated or reverse
        modify_no_partnership_status_for_existing_cadet(
            required_dict_for_allocation=required_dict_for_allocation,
            how_changed=how_changed,
        )
        affected_partners = []

    elif how_changed.had_partner_and_now_does_not:
        partner = break_up_existing_partnership_and_return_old_partner(
            required_dict_for_allocation=required_dict_for_allocation,
            how_changed=how_changed,
        )
        affected_partners = [partner]

    elif how_changed.now_has_partner:
        affected_partners = create_partnership_and_return_affected_partners(
            required_dict_for_allocation=required_dict_for_allocation,
            how_changed=how_changed,
            cadet_boat_class_group_club_dinghy_and_partner_on_day=cadet_boat_class_group_club_dinghy_and_partner_on_day,
        )

    else:
        raise Exception("Shouldn't get here!")

    return ListOfCadets(affected_partners)


def modify_no_partnership_status_for_existing_cadet(
    required_dict_for_allocation: RequiredDictForAllocation,
    how_changed: PartnershipChange,
):

    cadet = how_changed.cadet
    day = how_changed.day
    new_partner_status = how_changed.new_partner

    required_dict_for_allocation.dict_of_cadets_and_boat_class_and_partners.allocate_partner_for_cadet_on_day(
        cadet=cadet, day=day, cadet_partner=new_partner_status
    )


def break_up_existing_partnership_and_return_old_partner(
    required_dict_for_allocation: RequiredDictForAllocation,
    how_changed: PartnershipChange,
) -> Cadet:

    cadet = how_changed.cadet
    day = how_changed.day
    partner_cadet = how_changed.original_partner

    required_dict_for_allocation.dict_of_cadets_and_boat_class_and_partners.breakup_partnership(
        cadet=cadet, partner_cadet=partner_cadet, day=day
    )

    return partner_cadet

def create_partnership_and_return_affected_partners(
    required_dict_for_allocation: RequiredDictForAllocation,
    how_changed: PartnershipChange,
    cadet_boat_class_group_club_dinghy_and_partner_on_day: CadetBoatClassClubDinghyGroupAndPartnerAtEventOnDay,
):

    list_of_all_affected_cadets = []
    new_partner_removed_partner_in_list_or_empty_list = if_new_partner_had_partner_remove_them_and_return_removed_partner_in_list(
        required_dict_for_allocation=required_dict_for_allocation,
        how_changed=how_changed,
    )
    list_of_all_affected_cadets+=new_partner_removed_partner_in_list_or_empty_list

    existing_partner_removed_partner_in_list_or_empty_list = if_cadet_had_existing_partner_remove_them_and_return_affected_cadets_in_list(
        required_dict_for_allocation=required_dict_for_allocation,
        how_changed=how_changed,
    )
    list_of_all_affected_cadets+=existing_partner_removed_partner_in_list_or_empty_list

    new_partnership = create_fresh_two_handed_partnership_and_return_partners(
        required_dict_for_allocation=required_dict_for_allocation,
        cadet_boat_class_group_club_dinghy_and_partner_on_day=cadet_boat_class_group_club_dinghy_and_partner_on_day,
    )

    list_of_all_affected_cadets+=new_partnership

    return list_of_all_affected_cadets

def if_new_partner_had_partner_remove_them_and_return_removed_partner_in_list(
    required_dict_for_allocation: RequiredDictForAllocation,
    how_changed: PartnershipChange,
) -> ListOfCadets:

    did_new_partner_have_partner = how_changed.new_partner_had_partner

    if did_new_partner_have_partner:
        new_partner = how_changed.new_partner
        day = how_changed.day
        new_partner_original_partner = how_changed.new_partner_who_was_their_partner
        required_dict_for_allocation.dict_of_cadets_and_boat_class_and_partners.breakup_partnership(
            cadet=new_partner, partner_cadet=new_partner_original_partner, day=day
        )
        return ListOfCadets([new_partner_original_partner, new_partner])
    else:
        return ListOfCadets.create_empty()

def if_cadet_had_existing_partner_remove_them_and_return_affected_cadets_in_list(
    required_dict_for_allocation: RequiredDictForAllocation,
    how_changed: PartnershipChange,
) -> ListOfCadets:

    did_cadet_have_existing_partner = how_changed.did_have_partner

    if did_cadet_have_existing_partner:
        original_partner = how_changed.original_partner
        cadet = how_changed.cadet
        day = how_changed.day
        required_dict_for_allocation.dict_of_cadets_and_boat_class_and_partners.breakup_partnership(
            cadet=cadet, partner_cadet=original_partner, day=day
        )
        return ListOfCadets([original_partner, cadet])
    else:
        return ListOfCadets.create_empty()

def create_fresh_two_handed_partnership_and_return_partners(
    required_dict_for_allocation: RequiredDictForAllocation,
    cadet_boat_class_group_club_dinghy_and_partner_on_day: CadetBoatClassClubDinghyGroupAndPartnerAtEventOnDay,
):

    cadet = cadet_boat_class_group_club_dinghy_and_partner_on_day.cadet
    partner_cadet = cadet_boat_class_group_club_dinghy_and_partner_on_day.partner_cadet
    day = cadet_boat_class_group_club_dinghy_and_partner_on_day.day

    rd = required_dict_for_allocation
    rd.dict_of_cadets_and_boat_class_and_partners.create_fresh_two_handed_partnership(
        cadet=cadet, partner_cadet=partner_cadet, day=day
    )

    clone_cadet_group_club_dinghy_boat_class_sail_number_to_partner_and_return_partner(
        required_dict_for_allocation=required_dict_for_allocation,
        cadet_boat_class_group_club_dinghy_and_partner_on_day=cadet_boat_class_group_club_dinghy_and_partner_on_day,
    )

    return ListOfCadets([cadet, partner_cadet])

def clone_cadet_group_club_dinghy_boat_class_sail_number_to_partner_and_return_partner(
    required_dict_for_allocation: RequiredDictForAllocation,
    cadet_boat_class_group_club_dinghy_and_partner_on_day: CadetBoatClassClubDinghyGroupAndPartnerAtEventOnDay,
) -> Cadet:

    cadet_boat_class_group_club_dinghy_and_partner_on_day_with_partner_as_cadet = (
        cadet_boat_class_group_club_dinghy_and_partner_on_day.switch_partner()
    )
    partner_cadet=update_cadets_own_info_excluding_partner_and_return_cadet(
        required_dict_for_allocation=required_dict_for_allocation,
        cadet_boat_class_group_club_dinghy_and_partner_on_day=cadet_boat_class_group_club_dinghy_and_partner_on_day_with_partner_as_cadet,
    )
    return partner_cadet


def update_cadets_own_info_excluding_partner_and_return_cadet(
    required_dict_for_allocation: RequiredDictForAllocation,
    cadet_boat_class_group_club_dinghy_and_partner_on_day: CadetBoatClassClubDinghyGroupAndPartnerAtEventOnDay,
) -> Cadet:

    cadet = cadet_boat_class_group_club_dinghy_and_partner_on_day.cadet
    day = cadet_boat_class_group_club_dinghy_and_partner_on_day.day
    group = cadet_boat_class_group_club_dinghy_and_partner_on_day.group
    club_boat = cadet_boat_class_group_club_dinghy_and_partner_on_day.club_dinghy
    sail_number = cadet_boat_class_group_club_dinghy_and_partner_on_day.sail_number
    boat_class = cadet_boat_class_group_club_dinghy_and_partner_on_day.boat_class

    rd = required_dict_for_allocation
    rd.dict_of_cadets_with_days_and_groups.add_or_upate_group_for_cadet_on_day(
        cadet=cadet, day=day, group=group
    )

    rd.dict_of_cadets_and_club_dinghies_at_event.allocate_club_boat_on_day(
        cadet=cadet, day=day, club_boat=club_boat
    )

    rd.dict_of_cadets_and_boat_class_and_partners.update_boat_class_sail_number_for_updated_cadet_at_event(
        cadet=cadet,
        day=day,
        boat_class=boat_class,
        sail_number=sail_number,
    )

    return cadet

def how_has_partnership_changed(
    dict_of_cadets_and_boat_class_and_partners: DictOfCadetsAndBoatClassAndPartners,
    cadet_boat_class_group_club_dinghy_and_partner_on_day: CadetBoatClassClubDinghyGroupAndPartnerAtEventOnDay,
) -> PartnershipChange:

    cadet = cadet_boat_class_group_club_dinghy_and_partner_on_day.cadet
    day = cadet_boat_class_group_club_dinghy_and_partner_on_day.day

    original_cadet_with_partner = (
        dict_of_cadets_and_boat_class_and_partners.boat_classes_and_partner_for_cadet(
            cadet
        ).boat_class_and_partner_on_day(day)
    )
    original_partner = original_cadet_with_partner.partner_cadet

    new_partner = cadet_boat_class_group_club_dinghy_and_partner_on_day.partner_cadet

    now_valid = valid_partnership_given_partner_cadet(new_partner)

    if now_valid:
        new_partner_with_partner = dict_of_cadets_and_boat_class_and_partners.boat_classes_and_partner_for_cadet(
            new_partner
        ).boat_class_and_partner_on_day(
            day
        )
        new_partner_who_was_their_partner = new_partner_with_partner.partner_cadet
    else:
        new_partner_who_was_their_partner = None

    return PartnershipChange(
        cadet=cadet,
        day=day,
        original_partner=original_partner,
        new_partner=new_partner,
        new_partner_who_was_their_partner=new_partner_who_was_their_partner,
    )
