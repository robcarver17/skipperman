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

from app.objects.cadets import Cadet, ListOfCadets
from app.objects.day_selectors import Day
from app.objects.utilities.exceptions import missing_data, arg_not_passed
from app.objects.partners import (
    no_cadet_partner_required,
    from_cadet_id_to_partner_cadet,
    no_partner_allocated,
    from_partner_cadet_to_id_or_string,
    NoCadetPartner,
)
from app.objects.utilities.utils import most_common, flatten


@dataclass
class CadetBoatClassAndPartnerAtEventOnDay:
    cadet: Cadet
    boat_class: BoatClass
    sail_number: str
    day: Day
    partner_cadet: Cadet = no_cadet_partner_required

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


    def allocate_partner_for_cadet_on_day(
        self, day: Day, cadet_partner: Union[NoCadetPartner, Cadet]
    ):
        boat_class_and_partner_on_day = self.boat_class_and_partner_on_day(day)
        boat_class_and_partner_on_day.partner_cadet = cadet_partner

    def update_boat_class_and_sail_number_on_day(
        self, day: Day, boat_class: BoatClass, sail_number: str
    ):
        boat_class_and_partner_on_day = self.boat_class_and_partner_on_day(day)
        boat_class_and_partner_on_day.boat_class = boat_class
        boat_class_and_partner_on_day.sail_number = sail_number

        self[day] = boat_class_and_partner_on_day

    def most_common_boat_class(self) -> BoatClass:
        list_of_boat_classes = [
            boat_class_and_partner.boat_class
            for boat_class_and_partner in self.values()
        ]

        return most_common(list_of_boat_classes, no_boat_class)

    def most_common_partner(self) -> Cadet:
        list_of_partners = [
            boat_class_and_partner.partner_cadet
            for boat_class_and_partner in self.values()
        ]

        return most_common(list_of_partners, no_cadet_partner_required)

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

    def partner_on_day(
        self, day: Day, default=no_cadet_partner_required
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
    def create_fresh_two_handed_partnership(
        self, cadet: Cadet, partner_cadet: Cadet, day: Day
    ):
        print(
            "Partnering original cadet %s and new cadet %s"
            % (cadet.name, partner_cadet.name)
        )
        original_cadet_details = self.boat_classes_and_partner_for_cadet(
            cadet
        ).boat_class_and_partner_on_day(day)
        self.update_boat_class_and_sail_number_on_day(
            cadet=partner_cadet,
            day=day,
            boat_class=original_cadet_details.boat_class,
            sail_number=original_cadet_details.sail_number,
        )

        self.allocate_partner_for_cadet_on_day(
            cadet=cadet, cadet_partner=partner_cadet, day=day
        )
        self.allocate_partner_for_cadet_on_day(
            cadet=partner_cadet, cadet_partner=cadet, day=day
        )

    def breakup_partnership(self, cadet: Cadet, partner_cadet: Cadet, day: Day):
        self.unallocate_partner_for_cadet_on_day(cadet=cadet, day=day)
        self.unallocate_partner_for_cadet_on_day(cadet=partner_cadet, day=day)

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

    def unallocate_partner_for_cadet_on_day(self, cadet: Cadet, day: Day):
        self.allocate_partner_for_cadet_on_day(
            cadet=cadet, day=day, cadet_partner=no_partner_allocated
        )

    def allocate_partner_for_cadet_on_day(
        self, cadet: Cadet, day: Day, cadet_partner: Union[NoCadetPartner, Cadet]
    ):
        print(
            "Partnering %s with %s on %s" % (cadet.name, cadet_partner.name, day.name)
        )
        boat_class_and_partners = self.boat_classes_and_partner_for_cadet(cadet=cadet)
        boat_class_and_partners.allocate_partner_for_cadet_on_day(
            day=day, cadet_partner=cadet_partner
        )
        self[cadet] = boat_class_and_partners

    def update_boat_class_and_sail_number_on_day(
        self, cadet: Cadet, day: Day, boat_class: BoatClass, sail_number: str
    ):
        boat_class_and_partners = self.boat_classes_and_partner_for_cadet(cadet=cadet)
        boat_class_and_partners.update_boat_class_and_sail_number_on_day(
            day=day, boat_class=boat_class, sail_number=sail_number
        )
        self[cadet] = boat_class_and_partners

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
