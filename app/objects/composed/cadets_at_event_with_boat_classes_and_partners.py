from dataclasses import dataclass
from typing import Dict, List, Union

from app.objects.boat_classes import (
    BoatClass,
    ListOfBoatClasses,
    BoatClassAndPartnerAtEventOnDay,
    no_boat_class,
    no_boat_class_partner_or_sail_number,
)
from app.objects.cadet_at_event_with_boat_class_and_partners_with_ids import (
    CadetAtEventWithBoatClassAndPartnerWithIds,
    ListOfCadetAtEventWithBoatClassAndPartnerWithIds,
)

from app.objects.cadets import Cadet, ListOfCadets, NO_CADET_ID
from app.objects.day_selectors import Day
from app.objects.utilities.exceptions import missing_data, arg_not_passed, MultipleMatches
from app.objects.partners import (
    no_cadet_partner_required,
    from_cadet_id_to_partner_cadet,
    no_partner_allocated,
    from_partner_cadet_to_id_or_string,
    NoCadetPartner, no_partnership_given_partner_cadet, valid_partnership_given_partner_cadet,
)
from app.objects.utilities.utils import most_common, flatten


@dataclass
class CadetBoatClassAndPartnerAtEventOnDay:
    cadet: Cadet
    boat_class: BoatClass
    sail_number: str
    day: Day
    partner_cadet: Cadet = no_partner_allocated

    @property
    def partner_cadet_id(self):
        return from_partner_cadet_to_id_or_string(self.partner_cadet)

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


class DictOfDaysBoatClassAndPartners(Dict[Day, BoatClassAndPartnerAtEventOnDay]):
    @property
    def list_of_days(self):
        return list(self.keys())


    def most_common_boat_class(self) -> BoatClass:
        list_of_boat_classes = [
            boat_class_and_partner.boat_class
            for boat_class_and_partner in self.values()
        ]

        return most_common(list_of_boat_classes, no_boat_class)

    def most_common_partner(self) -> Cadet:
        list_of_partners = self.list_of_partners_across_days()

        return most_common(list_of_partners, default=no_partner_allocated)

    def has_multiple_partners(self):
        list_of_partners = self.list_of_partners_across_days()

        return len(set(list_of_partners))>1

    def list_of_partners_across_days(self):
        list_of_partners = [
            boat_class_and_partner.partner_cadet
            for boat_class_and_partner in self.values()
            if valid_partnership_given_partner_cadet(boat_class_and_partner.partner_cadet)
        ]

        return list_of_partners

    def get_most_common_partner_id_across_days(self,  default=NO_CADET_ID) -> str:
        partner = self.most_common_partner()
        if no_partnership_given_partner_cadet(partner):
            return default

        return partner.id

    def unique_list_of_boat_classes(self) -> ListOfBoatClasses:
        list_of_boat_classes = [
            boat_class_and_partner.boat_class
            for boat_class_and_partner in self.values()
        ]
        return ListOfBoatClasses(list(set(list_of_boat_classes)))

    def is_in_boat_class_on_day(self, day: Day, boat_class: BoatClass):
        boat_class_and_partner = self.boat_class_and_partner_on_day(
            day, default=missing_data
        )
        if boat_class_and_partner is missing_data:
            return False

        return boat_class_and_partner.boat_class == boat_class

    def sail_number_on_day(self, day: Day, default="") -> str:
        boat_class_and_partner = self.boat_class_and_partner_on_day(
            day, default=missing_data
        )
        if boat_class_and_partner is missing_data:
            return default

        return boat_class_and_partner.sail_number

    def has_boat_class_on_day(self, day: Day):
        boat_class_on_day = self.boat_class_on_day(day, default=no_boat_class)
        no_boat = boat_class_on_day is no_boat_class
        return not no_boat

    def boat_class_on_day(self, day: Day, default=no_boat_class) -> BoatClass:
        boat_class_and_partner = self.boat_class_and_partner_on_day(
            day, default=missing_data
        )
        if boat_class_and_partner is missing_data:
            return default

        return boat_class_and_partner.boat_class

    def has_valid_partner_on_day(self, day: Day):
        boat_class_and_partner = self.boat_class_and_partner_on_day(
            day, default=missing_data
        )
        if boat_class_and_partner is missing_data:
            return False

        return boat_class_and_partner.has_partner

    def partner_id_on_day(self, day: Day, default=NO_CADET_ID
    ) -> str:
        partner_on_day = self.partner_on_day(day, default=no_partner_allocated)
        if no_partnership_given_partner_cadet(partner_on_day):
            return default

        return partner_on_day.id


    def partner_on_day(
        self, day: Day, default=no_partner_allocated
    ) -> [Cadet, object]:
        boat_class_and_partner = self.boat_class_and_partner_on_day(
            day, default=missing_data
        )
        if boat_class_and_partner is missing_data:
            return default

        return boat_class_and_partner.partner_cadet

    def boat_class_and_partner_on_day(
        self, day: Day, default=arg_not_passed
    ) -> BoatClassAndPartnerAtEventOnDay:
        if default is arg_not_passed:
            default = no_boat_class_partner_or_sail_number
        return self.get(day, default)


class ListOfCadetBoatClassAndPartnerAtEventOnDay(
    List[CadetBoatClassAndPartnerAtEventOnDay]
):
    @classmethod
    def from_list_of_cadets_at_event_with_boat_class_and_partner_with_ids(
        cls,
        list_of_cadet_at_event_with_boat_class_and_partner_with_ids: ListOfCadetAtEventWithBoatClassAndPartnerWithIds,
        list_of_cadets: ListOfCadets,
        list_of_boats: ListOfBoatClasses,
    ):
        return cls(
            [
                CadetBoatClassAndPartnerAtEventOnDay.from_cadet_at_event_with_boat_class_and_partner_with_ids(
                    cadet_at_event_with_boat_class_and_partner_with_ids,
                    list_of_cadets=list_of_cadets,
                    list_of_boats=list_of_boats,
                )
                for cadet_at_event_with_boat_class_and_partner_with_ids in list_of_cadet_at_event_with_boat_class_and_partner_with_ids
            ]
        )

    def unique_list_of_cadets(self) -> ListOfCadets:
        list_of_cadets = [cadet_boat_class.cadet for cadet_boat_class in self]
        return ListOfCadets(list(set(list_of_cadets)))

    def dict_of_days_boat_class_and_partners_for_cadet(
        self, cadet: Cadet
    ) -> DictOfDaysBoatClassAndPartners:
        subset_for_cadet = self.subset_for_cadet(cadet)

        return DictOfDaysBoatClassAndPartners(
            [
                (
                    cadet_with_boat.day,
                    BoatClassAndPartnerAtEventOnDay(
                        boat_class=cadet_with_boat.boat_class,
                        partner_cadet=cadet_with_boat.partner_cadet,
                        sail_number=cadet_with_boat.sail_number,
                    ),
                )
                for cadet_with_boat in subset_for_cadet
            ]
        )

    def subset_for_cadet(
        self, cadet: Cadet
    ) -> "ListOfCadetBoatClassAndPartnerAtEventOnDay":
        return ListOfCadetBoatClassAndPartnerAtEventOnDay(
            [
                cadet_with_boat
                for cadet_with_boat in self
                if cadet_with_boat.cadet == cadet
            ]
        )


class DictOfCadetsAndBoatClassAndPartners(Dict[Cadet, DictOfDaysBoatClassAndPartners]):

    def unique_sorted_list_of_boat_classes_at_event(
        self, sorted_list_of_boat_classes: ListOfBoatClasses
    ):
        boat_classes_for_cadets = [
            dict_of_days_and_boat_classes.unique_list_of_boat_classes()
            for dict_of_days_and_boat_classes in self.values()
        ]
        boat_classes_across_cadets = flatten(boat_classes_for_cadets)

        sorted_list = [
            boat_class
            for boat_class in sorted_list_of_boat_classes
            if boat_class in boat_classes_across_cadets
        ]

        return ListOfBoatClasses(sorted_list)


    def boat_classes_and_partner_for_cadet(
        self, cadet: Cadet, default=arg_not_passed
    ) -> DictOfDaysBoatClassAndPartners:
        if default is arg_not_passed:
            default = DictOfDaysBoatClassAndPartners()
        return self.get(cadet, default)

    def list_of_cadets(self) -> ListOfCadets:
        return ListOfCadets(list(self.keys()))


def compose_raw_dict_of_cadets_and_boat_classes_and_partners(
    list_of_cadets: ListOfCadets,
    list_of_boat_classes: ListOfBoatClasses,
    list_of_cadets_at_event_with_boat_class_and_partners_with_ids: ListOfCadetAtEventWithBoatClassAndPartnerWithIds,
) -> Dict[Cadet, DictOfDaysBoatClassAndPartners]:
    list_of_cadet_boat_classes_and_partners_at_event_on_day = ListOfCadetBoatClassAndPartnerAtEventOnDay.from_list_of_cadets_at_event_with_boat_class_and_partner_with_ids(
        list_of_cadet_at_event_with_boat_class_and_partner_with_ids=list_of_cadets_at_event_with_boat_class_and_partners_with_ids,
        list_of_boats=list_of_boat_classes,
        list_of_cadets=list_of_cadets,
    )

    list_of_cadets_at_event = (
        list_of_cadet_boat_classes_and_partners_at_event_on_day.unique_list_of_cadets()
    )

    raw_dict = dict(
        [
            (
                cadet,
                list_of_cadet_boat_classes_and_partners_at_event_on_day.dict_of_days_boat_class_and_partners_for_cadet(
                    cadet
                ),
            )
            for cadet in list_of_cadets_at_event
        ]
    )

    return raw_dict



@dataclass
class BoatGrouping:
    first_id: str
    second_id: str

    def matches_eithier_id(self, match_id: str):
        return match_id in [self.first_id, self.second_id]

    def is_first_id(self, match_id:str):
        return match_id==self.first_id

class _InternalListOfBoatGroupings(List[BoatGrouping]):
    def does_cadet_with_id_have_edit_rights_given_partner_id(self, cadet_id: str, partner_id:str):
        existing_boat = self.grouping_matching_eithier_id(cadet_id, default=None)
        if existing_boat is None:
            self.add_new_grouping(cadet_id, partner_id)
            return True

        return existing_boat.is_first_id(cadet_id) ## should always be False, but you never know

    def add_new_grouping(self, cadet_id: str, partner_id:str):
        self.append(BoatGrouping(cadet_id, partner_id))

    def grouping_matching_eithier_id(self, match_id: str, default=None) -> BoatGrouping:
        matches = [x for x in self if x.matches_eithier_id(match_id)]
        if len(matches)>1:
            raise MultipleMatches("can't be on more than one boat")

        if len(matches)==0:
            return default
        else:
            return matches[0]


class ListOfBoatGroupings:
    def __init__(self, dict_of_cadets_boat_classes_and_partners: DictOfCadetsAndBoatClassAndPartners):
        self._dict_of_cadets_boat_classes_and_partners = dict_of_cadets_boat_classes_and_partners
        self._list_of_boat_groupings = _InternalListOfBoatGroupings()

    def does_cadet_have_edit_rights_on_day(self, cadet: Cadet, day: Day):
        partner_id = self.partner_id_for_cadet_on_day(cadet, day)

        return self.does_cadet_with_id_have_edit_rights_given_partner_id(cadet.id, partner_id)

    def does_cadet_have_edit_rights_across_days(self, cadet: Cadet):
        if self.has_multiple_partners(cadet):
            ### can't edit
            return False

        partner_id = self.partner_id_for_cadet_across_days(cadet)

        return self.does_cadet_with_id_have_edit_rights_given_partner_id(cadet.id, partner_id)

    def does_cadet_with_id_have_edit_rights_given_partner_id(self, cadet_id: str, partner_id:str):
        if partner_id==NO_CADET_ID:
            ## no partner, not an issue
            return True
        else:
            return self.list_of_boat_groupings.does_cadet_with_id_have_edit_rights_given_partner_id(cadet_id=cadet_id, partner_id=partner_id)

    def has_multiple_partners(self, cadet: Cadet):
        return self.boat_classes_and_partner_for_cadet(cadet).has_multiple_partners()

    def partner_id_for_cadet_across_days(self, cadet: Cadet):
        return self.boat_classes_and_partner_for_cadet(cadet).get_most_common_partner_id_across_days(default=NO_CADET_ID)

    def partner_id_for_cadet_on_day(self, cadet: Cadet, day: Day):
        return self.boat_classes_and_partner_for_cadet(cadet).partner_id_on_day(day, default=NO_CADET_ID)

    def boat_classes_and_partner_for_cadet(self, cadet: Cadet):
        return self.dict_of_cadets_boat_classes_and_partners.boat_classes_and_partner_for_cadet(cadet)

    @property
    def dict_of_cadets_boat_classes_and_partners(self) -> DictOfCadetsAndBoatClassAndPartners:
        return self._dict_of_cadets_boat_classes_and_partners

    @property
    def list_of_boat_groupings(self) -> _InternalListOfBoatGroupings:
        return self._list_of_boat_groupings

