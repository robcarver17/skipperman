from dataclasses import dataclass
from typing import List, Union

from app.objects.groups import Group, unallocated_group
from app.objects.club_dinghies import ClubDinghy, no_club_dinghy

from app.objects.utilities.exceptions import missing_data, MultipleMatches

from app.objects.boat_classes import BoatClass, ListOfBoatClasses
from app.objects.cadet_at_event_with_boat_class_and_partners_with_ids import (
    CadetAtEventWithBoatClassAndPartnerWithIds,
)
from app.objects.partners import (
    no_cadet_partner_required,
    from_cadet_id_to_partner_cadet,
    valid_partnership_given_partner_cadet,
    NoCadetPartner,
    no_partnership_given_partner_cadet,
)
from app.objects.cadets import Cadet, ListOfCadets
from app.objects.day_selectors import Day


@dataclass
class CadetBoatClassClubDinghyGroupAndPartnerAtEventOnDay:
    cadet: Cadet
    boat_class: BoatClass
    sail_number: str
    day: Day
    club_dinghy: ClubDinghy = no_club_dinghy
    group: Group = unallocated_group
    partner_cadet: Cadet = no_cadet_partner_required

    def switch_partner(self):
        return CadetBoatClassClubDinghyGroupAndPartnerAtEventOnDay(
            cadet=self.partner_cadet,
            partner_cadet=self.cadet,
            day=self.day,
            boat_class=self.boat_class,
            sail_number=self.sail_number,
            group=self.group,
            club_dinghy=self.club_dinghy,
        )

    def __eq__(self, other):
        equal_partners = are_partners_equal(self.partner_cadet, other.partner_cadet)
        return (
            self.cadet == other.cadet
            and self.boat_class == other.boat_class
            and self.sail_number == other.sail_number
            and self.day == other.day
            and self.club_dinghy == other.club_dinghy
            and self.group == other.group
            and equal_partners
        )

    @classmethod
    def from_cadet_at_event_with_boat_class_and_partner_with_ids(
        cls,
        cadet_at_event_with_boat_class_and_partner_with_ids: CadetAtEventWithBoatClassAndPartnerWithIds,
        list_of_cadets: ListOfCadets,
        list_of_boats: ListOfBoatClasses,
    ):
        partner_cadet = from_cadet_id_to_partner_cadet(
            cadet_id=cadet_at_event_with_boat_class_and_partner_with_ids.partner_cadet_id,
            list_of_cadets=list_of_cadets,
        )

        return cls(
            cadet=list_of_cadets.cadet_with_id(
                cadet_at_event_with_boat_class_and_partner_with_ids.cadet_id
            ),
            boat_class=list_of_boats.boat_with_id(
                cadet_at_event_with_boat_class_and_partner_with_ids.boat_class_id
            ),
            day=cadet_at_event_with_boat_class_and_partner_with_ids.day,
            sail_number=cadet_at_event_with_boat_class_and_partner_with_ids.sail_number,
            partner_cadet=partner_cadet,
        )


class ListOfCadetBoatClassClubDinghyGroupAndPartnerAtEventOnDay(
    List[CadetBoatClassClubDinghyGroupAndPartnerAtEventOnDay]
):
    def element_on_day_for_cadet(
        self, cadet: Cadet, day: Day, default=missing_data
    ) -> CadetBoatClassClubDinghyGroupAndPartnerAtEventOnDay:
        list_of_elements = [
            element for element in self if element.cadet == cadet and element.day == day
        ]
        if len(list_of_elements) > 1:
            raise MultipleMatches
        elif len(list_of_elements) == 0:
            return default

        return list_of_elements[0]

    def list_of_valid_partners(self) -> ListOfCadets:
        list_of_all_partners = (
            self.list_of_all_partners_including_unallocated_and_not_required()
        )
        valid_list_of_partners = ListOfCadets(
            [
                partner_cadet
                for partner_cadet in list_of_all_partners
                if valid_partnership_given_partner_cadet(partner_cadet)
            ]
        )

        return valid_list_of_partners

    def list_of_all_partners_including_unallocated_and_not_required(
        self,
    ) -> ListOfCadets:
        return ListOfCadets([element.partner_cadet for element in self])


def are_partners_equal(
    partner: Union[Cadet, NoCadetPartner], other_partner: Union[Cadet, NoCadetPartner]
) -> bool:
    no_partner = no_partnership_given_partner_cadet(partner)
    no_other_partner = no_partnership_given_partner_cadet(other_partner)
    if no_partner and no_other_partner:
        return partner == other_partner
    elif no_partner and not no_other_partner:
        return False
    elif not no_partner and no_other_partner:
        return False
    elif not no_partner and not no_other_partner:
        return partner == other_partner
    else:
        raise Exception
