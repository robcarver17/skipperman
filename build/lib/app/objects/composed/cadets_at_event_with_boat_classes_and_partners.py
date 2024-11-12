from dataclasses import dataclass
from typing import List, Dict, Union

from app.objects.events import Event, ListOfEvents

from app.objects.boat_classes import BoatClass, ListOfBoatClasses
from app.objects.cadet_at_event_with_dinghy_with_ids import (
    ListOfCadetAtEventWithBoatClassAndPartnerWithIds,
    CadetAtEventWithBoatClassAndPartnerWithIds,
    NO_PARTNER_REQUIRED,
    NOT_ALLOCATED,
)
from app.objects.cadets import Cadet, ListOfCadets
from app.objects.day_selectors import Day

NoPartnerCadetRequired = object()
NoPartnerAllocated = object()


@dataclass
class CadetBoatClassAndPartnerAtEventOnDay:
    cadet: Cadet
    boat_class: BoatClass
    sail_number: str
    day: Day
    partner_cadet: Cadet = NoPartnerCadetRequired

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
            boat_class=list_of_boats.object_with_id(
                cadet_at_event_with_boat_class_and_partner_with_ids.boat_class_id
            ),
            day=cadet_at_event_with_boat_class_and_partner_with_ids.day,
            sail_number=cadet_at_event_with_boat_class_and_partner_with_ids.sail_number,
            partner_cadet=partner_cadet,
        )


def from_cadet_id_to_partner_cadet(
    cadet_id: str, list_of_cadets: ListOfCadets
) -> Union[Cadet, object]:
    if cadet_id == NOT_ALLOCATED:
        return NoPartnerAllocated
    elif cadet_id == NO_PARTNER_REQUIRED:
        return NoPartnerCadetRequired
    else:
        return list_of_cadets.cadet_with_id(cadet_id)


@dataclass
class BoatClassAndPartnerAtEventOnDay:
    boat_class: BoatClass
    sail_number: str
    partner_cadet: Cadet = NoPartnerCadetRequired


class DictOfDaysBoatClassAndPartners(Dict[Day, BoatClassAndPartnerAtEventOnDay]):
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
        event: Event,
    ):
        super().__init__(raw_dict)
        self._list_of_cadets_at_event_with_boat_class_and_partners_with_ids = (
            list_of_cadets_at_event_with_boat_class_and_partners_with_ids
        )
        self._event = event

    @property
    def list_of_cadets_at_event_with_boat_class_and_partners_with_ids(
        self,
    ) -> ListOfCadetAtEventWithBoatClassAndPartnerWithIds:
        return self._list_of_cadets_at_event_with_boat_class_and_partners_with_ids

    @property
    def event(self) -> Event:
        return self._event


def compose_dict_of_cadets_and_boat_classes_and_partners(
    event_id: str,
    list_of_cadets: ListOfCadets,
    list_of_events: ListOfEvents,
    list_of_boat_classes: ListOfBoatClasses,
    list_of_cadets_at_event_with_boat_class_and_partners_with_ids: ListOfCadetAtEventWithBoatClassAndPartnerWithIds,
) -> DictOfCadetsAndBoatClassAndPartners:
    event = list_of_events.object_with_id(event_id)

    raw_dict = compose_raw_dict_of_cadets_and_boat_classes_and_partners(
        list_of_cadets=list_of_cadets,
        list_of_boat_classes=list_of_boat_classes,
        list_of_cadets_at_event_with_boat_class_and_partners_with_ids=list_of_cadets_at_event_with_boat_class_and_partners_with_ids,
    )

    return DictOfCadetsAndBoatClassAndPartners(
        raw_dict=raw_dict,
        event=event,
        list_of_cadets_at_event_with_boat_class_and_partners_with_ids=list_of_cadets_at_event_with_boat_class_and_partners_with_ids,
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
