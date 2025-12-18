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
from app.objects.composed.people_at_event_with_club_dinghies import (
    DictOfPeopleAndClubDinghiesAtEvent,
)
from app.objects.composed.cadets_at_event_with_groups import (
    DEPRECATE_DictOfCadetsWithDaysAndGroupsAtEvent,
)
from app.objects.composed.cadets_at_event_with_registration_data import (
    DictOfCadetsWithRegistrationData,
)
from app.objects.day_selectors import Day, DaySelector
from app.objects.groups import unallocated_group
from app.objects.partners import valid_partnership_given_partner_cadet, NoCadetPartner


def cadets_not_allocated_to_group_but_attending_on_day(
    dict_of_cadets_with_registration_data: DictOfCadetsWithRegistrationData,
    dict_of_cadets_with_days_and_groups: DEPRECATE_DictOfCadetsWithDaysAndGroupsAtEvent,
    day: Day,
) -> ListOfCadets:
    list_of_cadets = []
    for cadet in dict_of_cadets_with_registration_data.list_of_cadets():
        inactive = (
            not dict_of_cadets_with_registration_data.registration_data_for_cadet(
                cadet
            ).status.is_active
        )
        if inactive:
            continue

        attending = dict_of_cadets_with_registration_data.registration_data_for_cadet(
            cadet
        ).availability.available_on_day(day)
        if not attending:
            continue

        group = dict_of_cadets_with_days_and_groups.get_days_and_groups_for_cadet(
            cadet
        ).group_on_day(day, default=unallocated_group)
        if group is unallocated_group:
            list_of_cadets.append(cadet)

    return ListOfCadets(list_of_cadets)


def cadets_not_allocated_to_group_on_at_least_one_day_attending(
    dict_of_cadets_with_registration_data: DictOfCadetsWithRegistrationData,
    dict_of_cadets_with_days_and_groups: DEPRECATE_DictOfCadetsWithDaysAndGroupsAtEvent,
) -> ListOfCadets:
    list_of_cadets = []
    for cadet in dict_of_cadets_with_registration_data.list_of_cadets():
        inactive = (
            not dict_of_cadets_with_registration_data.registration_data_for_cadet(
                cadet
            ).status.is_active
        )
        if inactive:
            continue

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
    dict_of_cadets_with_days_and_groups: DEPRECATE_DictOfCadetsWithDaysAndGroupsAtEvent,
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
        return (
            self.did_have_partner
            and self.now_has_partner
            and self.original_partner == self.new_partner
        )

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
    dict_of_cadets_and_club_dinghies_at_event: DictOfPeopleAndClubDinghiesAtEvent
    dict_of_cadets_with_days_and_groups: DEPRECATE_DictOfCadetsWithDaysAndGroupsAtEvent
    availability_dict: Dict[Cadet, DaySelector]

    def add_single_cadet_to_list(self, cadet: Cadet):
        self.add_affected_cadets_to_list(ListOfCadets([cadet]))

    def add_affected_cadets_to_list(self, affected_cadets: ListOfCadets):
        current_affected_cadets = self.affected_cadets
        current_affected_cadets = current_affected_cadets + affected_cadets
        current_affected_cadets = ListOfCadets(list(set(current_affected_cadets)))

        self.affected_cadets = current_affected_cadets

    @property
    def affected_cadets(self):
        default = ListOfCadets.create_empty()
        return getattr(self, "_affected_cadets", default)

    @affected_cadets.setter
    def affected_cadets(self, affected_cadets: ListOfCadets):
        self._affected_cadets = affected_cadets


def update_boat_info_for_updated_cadet_at_event_and_return_affected_cadets(
    required_dict_for_allocation: RequiredDictForAllocation,
    cadet_boat_class_group_club_dinghy_and_partner_on_day: CadetBoatClassClubDinghyGroupAndPartnerAtEventOnDay,
) -> RequiredDictForAllocation:
    if availability_is_bad_for_sailor_or_partner(
        required_dict_for_allocation=required_dict_for_allocation,
        cadet_boat_class_group_club_dinghy_and_partner_on_day=cadet_boat_class_group_club_dinghy_and_partner_on_day,
    ):

        return required_dict_for_allocation

    required_dict_for_allocation = update_cadets_own_info_excluding_partner(
        required_dict_for_allocation=required_dict_for_allocation,
        cadet_boat_class_group_club_dinghy_and_partner_on_day=cadet_boat_class_group_club_dinghy_and_partner_on_day,
    )

    required_dict_for_allocation = update_partnership_info_for_updated_cadet_at_event(
        required_dict_for_allocation=required_dict_for_allocation,
        cadet_boat_class_group_club_dinghy_and_partner_on_day=cadet_boat_class_group_club_dinghy_and_partner_on_day,
    )

    return required_dict_for_allocation


def availability_is_bad_for_sailor_or_partner(
    required_dict_for_allocation: RequiredDictForAllocation,
    cadet_boat_class_group_club_dinghy_and_partner_on_day: CadetBoatClassClubDinghyGroupAndPartnerAtEventOnDay,
) -> bool:
    cadet = cadet_boat_class_group_club_dinghy_and_partner_on_day.cadet
    partner_cadet = cadet_boat_class_group_club_dinghy_and_partner_on_day.partner_cadet
    day = cadet_boat_class_group_club_dinghy_and_partner_on_day.day

    cadet_availability = required_dict_for_allocation.availability_dict[cadet]

    if not cadet_availability.available_on_day(day):
        return True

    if valid_partnership_given_partner_cadet(partner_cadet):
        partner_availabilty = required_dict_for_allocation.availability_dict[
            partner_cadet
        ]
        if not partner_availabilty.available_on_day(day):
            return True

    return False


def update_partnership_info_for_updated_cadet_at_event(
    required_dict_for_allocation: RequiredDictForAllocation,
    cadet_boat_class_group_club_dinghy_and_partner_on_day: CadetBoatClassClubDinghyGroupAndPartnerAtEventOnDay,
) -> RequiredDictForAllocation:
    how_changed = how_has_partnership_changed(
        dict_of_cadets_and_boat_class_and_partners=required_dict_for_allocation.dict_of_cadets_and_boat_class_and_partners,
        cadet_boat_class_group_club_dinghy_and_partner_on_day=cadet_boat_class_group_club_dinghy_and_partner_on_day,
    )

    if how_changed.unchanged:
        if how_changed.has_unchanged_partner:
            ## Ensure changes are in synch
            required_dict_for_allocation = clone_cadet_group_club_dinghy_boat_class_sail_number_to_partner(
                required_dict_for_allocation=required_dict_for_allocation,
                cadet_boat_class_group_club_dinghy_and_partner_on_day=cadet_boat_class_group_club_dinghy_and_partner_on_day,
            )

    elif how_changed.had_no_partner_and_still_doesnt:
        ## change only this cadet, change of state from singlehanded to not allocated or reverse
        required_dict_for_allocation = modify_no_partnership_status_for_existing_cadet(
            required_dict_for_allocation=required_dict_for_allocation,
            how_changed=how_changed,
        )

    elif how_changed.had_partner_and_now_does_not:
        required_dict_for_allocation = break_up_existing_partnership(
            required_dict_for_allocation=required_dict_for_allocation,
            how_changed=how_changed,
        )

    elif how_changed.now_has_partner:
        required_dict_for_allocation = create_partnership(
            required_dict_for_allocation=required_dict_for_allocation,
            how_changed=how_changed,
            cadet_boat_class_group_club_dinghy_and_partner_on_day=cadet_boat_class_group_club_dinghy_and_partner_on_day,
        )

    else:
        raise Exception("Shouldn't get here!")

    return required_dict_for_allocation


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
    required_dict_for_allocation.add_single_cadet_to_list(cadet)

    return required_dict_for_allocation


def break_up_existing_partnership(
    required_dict_for_allocation: RequiredDictForAllocation,
    how_changed: PartnershipChange,
) -> RequiredDictForAllocation:
    cadet = how_changed.cadet
    day = how_changed.day
    partner_cadet = how_changed.original_partner

    required_dict_for_allocation.dict_of_cadets_and_boat_class_and_partners.breakup_partnership(
        cadet=cadet, partner_cadet=partner_cadet, day=day
    )
    required_dict_for_allocation.add_affected_cadets_to_list(
        ListOfCadets([cadet, partner_cadet])
    )

    return required_dict_for_allocation


def create_partnership(
    required_dict_for_allocation: RequiredDictForAllocation,
    how_changed: PartnershipChange,
    cadet_boat_class_group_club_dinghy_and_partner_on_day: CadetBoatClassClubDinghyGroupAndPartnerAtEventOnDay,
):
    required_dict_for_allocation = (
        if_new_partner_had_partner_remove_them_and_return_removed_partner_in_list(
            required_dict_for_allocation=required_dict_for_allocation,
            how_changed=how_changed,
        )
    )

    required_dict_for_allocation = (
        if_cadet_had_existing_partner_remove_them_and_return_affected_cadets_in_list(
            required_dict_for_allocation=required_dict_for_allocation,
            how_changed=how_changed,
        )
    )

    required_dict_for_allocation = create_fresh_two_handed_partnership(
        required_dict_for_allocation=required_dict_for_allocation,
        cadet_boat_class_group_club_dinghy_and_partner_on_day=cadet_boat_class_group_club_dinghy_and_partner_on_day,
    )

    return required_dict_for_allocation


def if_new_partner_had_partner_remove_them_and_return_removed_partner_in_list(
    required_dict_for_allocation: RequiredDictForAllocation,
    how_changed: PartnershipChange,
) -> RequiredDictForAllocation:
    did_new_partner_have_partner = how_changed.new_partner_had_partner

    if did_new_partner_have_partner:
        new_partner = how_changed.new_partner
        day = how_changed.day
        new_partner_original_partner = how_changed.new_partner_who_was_their_partner
        required_dict_for_allocation.dict_of_cadets_and_boat_class_and_partners.breakup_partnership(
            cadet=new_partner, partner_cadet=new_partner_original_partner, day=day
        )
        required_dict_for_allocation.add_affected_cadets_to_list(
            ListOfCadets([new_partner_original_partner, new_partner])
        )

    return required_dict_for_allocation


def if_cadet_had_existing_partner_remove_them_and_return_affected_cadets_in_list(
    required_dict_for_allocation: RequiredDictForAllocation,
    how_changed: PartnershipChange,
) -> RequiredDictForAllocation:
    did_cadet_have_existing_partner = how_changed.did_have_partner

    if did_cadet_have_existing_partner:
        original_partner = how_changed.original_partner
        cadet = how_changed.cadet
        day = how_changed.day
        required_dict_for_allocation.dict_of_cadets_and_boat_class_and_partners.breakup_partnership(
            cadet=cadet, partner_cadet=original_partner, day=day
        )
        required_dict_for_allocation.add_affected_cadets_to_list(
            ListOfCadets([original_partner, cadet])
        )

    return required_dict_for_allocation


def create_fresh_two_handed_partnership(
    required_dict_for_allocation: RequiredDictForAllocation,
    cadet_boat_class_group_club_dinghy_and_partner_on_day: CadetBoatClassClubDinghyGroupAndPartnerAtEventOnDay,
) -> RequiredDictForAllocation:
    cadet = cadet_boat_class_group_club_dinghy_and_partner_on_day.cadet
    partner_cadet = cadet_boat_class_group_club_dinghy_and_partner_on_day.partner_cadet
    day = cadet_boat_class_group_club_dinghy_and_partner_on_day.day

    required_dict_for_allocation.dict_of_cadets_and_boat_class_and_partners.create_fresh_two_handed_partnership(
        cadet=cadet, partner_cadet=partner_cadet, day=day
    )

    required_dict_for_allocation = clone_cadet_group_club_dinghy_boat_class_sail_number_to_partner(
        required_dict_for_allocation=required_dict_for_allocation,
        cadet_boat_class_group_club_dinghy_and_partner_on_day=cadet_boat_class_group_club_dinghy_and_partner_on_day,
    )
    required_dict_for_allocation.add_affected_cadets_to_list(
        ListOfCadets([cadet, partner_cadet])
    )

    return required_dict_for_allocation


def clone_cadet_group_club_dinghy_boat_class_sail_number_to_partner(
    required_dict_for_allocation: RequiredDictForAllocation,
    cadet_boat_class_group_club_dinghy_and_partner_on_day: CadetBoatClassClubDinghyGroupAndPartnerAtEventOnDay,
) -> RequiredDictForAllocation:
    cadet_boat_class_group_club_dinghy_and_partner_on_day_with_partner_as_cadet = (
        cadet_boat_class_group_club_dinghy_and_partner_on_day.switch_partner()
    )
    required_dict_for_allocation = update_cadets_own_info_excluding_partner(
        required_dict_for_allocation=required_dict_for_allocation,
        cadet_boat_class_group_club_dinghy_and_partner_on_day=cadet_boat_class_group_club_dinghy_and_partner_on_day_with_partner_as_cadet,
    )
    required_dict_for_allocation.add_single_cadet_to_list(
        cadet_boat_class_group_club_dinghy_and_partner_on_day.partner_cadet
    )

    return required_dict_for_allocation


def update_cadets_own_info_excluding_partner(
    required_dict_for_allocation: RequiredDictForAllocation,
    cadet_boat_class_group_club_dinghy_and_partner_on_day: CadetBoatClassClubDinghyGroupAndPartnerAtEventOnDay,
) -> RequiredDictForAllocation:
    cadet = cadet_boat_class_group_club_dinghy_and_partner_on_day.cadet
    day = cadet_boat_class_group_club_dinghy_and_partner_on_day.day
    group = cadet_boat_class_group_club_dinghy_and_partner_on_day.group
    club_boat = cadet_boat_class_group_club_dinghy_and_partner_on_day.club_dinghy
    sail_number = cadet_boat_class_group_club_dinghy_and_partner_on_day.sail_number
    boat_class = cadet_boat_class_group_club_dinghy_and_partner_on_day.boat_class

    required_dict_for_allocation.dict_of_cadets_with_days_and_groups.add_or_upate_group_for_cadet_on_day(
        cadet=cadet, day=day, group=group
    )

    required_dict_for_allocation.dict_of_cadets_and_club_dinghies_at_event.allocate_club_boat_on_day(
        person=cadet, day=day, club_boat=club_boat
    )

    required_dict_for_allocation.dict_of_cadets_and_boat_class_and_partners.update_boat_class_and_sail_number_on_day(
        cadet=cadet,
        day=day,
        boat_class=boat_class,
        sail_number=sail_number,
    )

    required_dict_for_allocation.add_single_cadet_to_list(cadet)

    return required_dict_for_allocation
