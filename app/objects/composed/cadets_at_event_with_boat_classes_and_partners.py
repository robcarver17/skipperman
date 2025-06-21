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
from app.objects.events import Event, ListOfEvents
from app.objects.utilities.exceptions import missing_data, arg_not_passed
from app.objects.partners import (
    no_cadet_partner_required,
    from_cadet_id_to_partner_cadet,
    no_partner_allocated,
    from_partner_cadet_to_id_or_string,
    NoCadetPartner,
    valid_partnership_given_partner_cadet,
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

    def delete_boat_class_and_partner_on_day_and_return_deleted_item(self, day: Day):
        original_item = self.boat_class_and_partner_on_day(day, default=missing_data)
        if original_item is missing_data:
            return missing_data
        self.pop(day)

        return original_item

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

    def boat_class_on_day(self, day: Day, default=no_boat_class) -> BoatClass:
        boat_class_and_partner = self.boat_class_and_partner_on_day(
            day, default=missing_data
        )
        if boat_class_and_partner is missing_data:
            return default

        return boat_class_and_partner.boat_class

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

    def remove_boat_and_partner_on_day(self, day: Day):
        try:
            self.pop(day)
        except:
            pass


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
    def __init__(
        self,
        raw_dict: Dict[Cadet, DictOfDaysBoatClassAndPartners],
        list_of_cadets_at_event_with_boat_class_and_partners_with_ids: ListOfCadetAtEventWithBoatClassAndPartnerWithIds,
        list_of_boat_classes: ListOfBoatClasses,
        event: Event,
    ):
        super().__init__(raw_dict)
        self._list_of_cadets_at_event_with_boat_class_and_partners_with_ids = (
            list_of_cadets_at_event_with_boat_class_and_partners_with_ids
        )
        self._list_of_boat_classes = list_of_boat_classes
        self._event = event

    def delete_cadet_from_event_and_return_messages(self, cadet: Cadet):
        messages = []
        for day in self.event.days_in_event():
            messages += self.delete_cadet_from_event_on_day_and_return_messages(
                cadet=cadet, day=day
            )

        return messages

    def delete_cadet_from_event_on_day_and_return_messages(
        self, cadet: Cadet, day: Day
    ):
        messages = []

        ## do this first or will fail later
        partner = self.boat_classes_and_partner_for_cadet(cadet).partner_on_day(day)
        if valid_partnership_given_partner_cadet(partner):
            self.breakup_partnership(cadet, partner, day)
            messages.append(
                "- was sailing with %s on %s, partnership broken up"
                % (partner.name, day.name)
            )

        deleted_item = self.boat_classes_and_partner_for_cadet(
            cadet
        ).delete_boat_class_and_partner_on_day_and_return_deleted_item(day)

        if deleted_item is missing_data:
            return messages
        else:
            messages.append(" - deleted %s on %s" % (str(deleted_item), day.name))

        self.list_of_cadets_at_event_with_boat_class_and_partners_with_ids.clear_boat_details_from_existing_cadet_id(
            cadet_id=cadet.id, day=day
        )

        return messages

    def create_fresh_two_handed_partnership(
        self, cadet: Cadet, partner_cadet: Cadet, day: Day
    ):
        print("PArtnering %s and %s" % (cadet.name, partner_cadet.name))
        self.allocate_partner_for_cadet_on_day(
            cadet=cadet, cadet_partner=partner_cadet, day=day
        )
        self.allocate_partner_for_cadet_on_day(
            cadet=partner_cadet, cadet_partner=cadet, day=day
        )

    def breakup_partnership(self, cadet: Cadet, partner_cadet: Cadet, day: Day):
        self.unallocate_partner_for_cadet_on_day(cadet=cadet, day=day)
        self.unallocate_partner_for_cadet_on_day(cadet=partner_cadet, day=day)

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

        self.list_of_cadets_at_event_with_boat_class_and_partners_with_ids.allocate_partner_for_cadet_on_day(
            cadet_id=cadet.id,
            day=day,
            partner_id=from_partner_cadet_to_id_or_string(cadet_partner),
        )

    def update_boat_class_and_sail_number_on_day(
        self, cadet: Cadet, day: Day, boat_class: BoatClass, sail_number: str
    ):
        boat_class_and_partners = self.boat_classes_and_partner_for_cadet(cadet=cadet)
        boat_class_and_partners.update_boat_class_and_sail_number_on_day(
            day=day, boat_class=boat_class, sail_number=sail_number
        )
        self[cadet] = boat_class_and_partners

        self.list_of_cadets_at_event_with_boat_class_and_partners_with_ids.update_boat_and_sail_number_for_cadet_on_day(
            cadet_id=cadet.id,
            day=day,
            boat_class_id=boat_class.id,
            sail_number=sail_number,
        )

    def as_list_of_cadets_boat_classes_and_partners_at_event_on_day(
        self, day: Day
    ) -> ListOfCadetBoatClassAndPartnerAtEventOnDay:
        new_list = []
        for cadet, dict_of_boat_class_and_partners in self.items():
            boat_class_and_partner = (
                dict_of_boat_class_and_partners.boat_class_and_partner_on_day(day)
            )
            new_list.append(
                CadetBoatClassAndPartnerAtEventOnDay(
                    cadet=cadet,
                    boat_class=boat_class_and_partner.boat_class,
                    partner_cadet=boat_class_and_partner.partner_cadet,
                    sail_number=boat_class_and_partner.sail_number,
                    day=day,
                )
            )

        return ListOfCadetBoatClassAndPartnerAtEventOnDay(new_list)

    def unique_sorted_list_of_boat_classes_at_event(self) -> ListOfBoatClasses:
        boat_classes_for_cadets = [
            dict_of_days_and_boat_classes.unique_list_of_boat_classes()
            for dict_of_days_and_boat_classes in self.values()
        ]
        boat_classes_across_cadets = flatten(boat_classes_for_cadets)

        sorted_list = [
            boat_class
            for boat_class in self.list_of_boat_classes
            if boat_class in boat_classes_across_cadets
        ]

        return ListOfBoatClasses(sorted_list)

    def remove_cadet_from_event_and_return_messages(self, cadet: Cadet) -> List[str]:
        all_messages = []
        for day in self.event.days_in_event():
            message = self.remove_cadet_from_event_on_day_and_return_message(
                cadet=cadet, day=day
            )
            all_messages.append(message)

        try:
            self.pop(cadet)
        except:
            pass

        return all_messages

    def remove_cadet_from_event_on_day_and_return_message(
        self, cadet: Cadet, day: Day
    ) -> str:
        boat_classes_and_partners = self.boat_classes_and_partner_for_cadet(cadet)
        boat_classes_and_partner_on_day = (
            boat_classes_and_partners.boat_class_and_partner_on_day(day)
        )

        has_partner = boat_classes_and_partner_on_day.has_partner
        if has_partner:
            partner_cadet = boat_classes_and_partner_on_day.partner_cadet
            message = (
                "%s was sailing with partner %s, now they aren't sailing: %s has no partner on %s"
                % (cadet.name, partner_cadet.name, partner_cadet.name, day.name)
            )
            self.breakup_partnership(cadet, partner_cadet, day)
        else:
            message = ""

        boat_classes_and_partners.remove_boat_and_partner_on_day(day)
        self[cadet] = boat_classes_and_partners

        self.list_of_cadets_at_event_with_boat_class_and_partners_with_ids.clear_boat_details_from_existing_cadet_id(
            cadet_id=cadet.id, day=day
        )

        return message

    def boat_classes_and_partner_for_cadet(
        self, cadet: Cadet, default=arg_not_passed
    ) -> DictOfDaysBoatClassAndPartners:
        if default is arg_not_passed:
            default = DictOfDaysBoatClassAndPartners()
        return self.get(cadet, default)

    def list_of_cadets(self) -> ListOfCadets:
        return ListOfCadets(list(self.keys()))

    @property
    def list_of_cadets_at_event_with_boat_class_and_partners_with_ids(
        self,
    ) -> ListOfCadetAtEventWithBoatClassAndPartnerWithIds:
        return self._list_of_cadets_at_event_with_boat_class_and_partners_with_ids

    @property
    def event(self) -> Event:
        return self._event

    @property
    def list_of_boat_classes(self) -> ListOfBoatClasses:
        return self._list_of_boat_classes


def compose_dict_of_cadets_and_boat_classes_and_partners(
    event_id: str,
    list_of_cadets: ListOfCadets,
    list_of_events: ListOfEvents,
    list_of_boat_classes: ListOfBoatClasses,
    list_of_cadets_at_event_with_boat_class_and_partners_with_ids: ListOfCadetAtEventWithBoatClassAndPartnerWithIds,
) -> DictOfCadetsAndBoatClassAndPartners:
    event = list_of_events.event_with_id(event_id)

    raw_dict = compose_raw_dict_of_cadets_and_boat_classes_and_partners(
        list_of_cadets=list_of_cadets,
        list_of_boat_classes=list_of_boat_classes,
        list_of_cadets_at_event_with_boat_class_and_partners_with_ids=list_of_cadets_at_event_with_boat_class_and_partners_with_ids,
    )

    return DictOfCadetsAndBoatClassAndPartners(
        raw_dict=raw_dict,
        event=event,
        list_of_cadets_at_event_with_boat_class_and_partners_with_ids=list_of_cadets_at_event_with_boat_class_and_partners_with_ids,
        list_of_boat_classes=list_of_boat_classes,
    )


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
