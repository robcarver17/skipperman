from dataclasses import dataclass
from typing import List, Dict

from app.objects.utils import flatten

from app.objects.events import ListOfEvents, Event

from app.objects.cadets import Cadet, ListOfCadets
from app.objects.club_dinghies import ClubDinghy, ListOfClubDinghies
from app.objects.day_selectors import Day
from app.objects.cadet_at_event_with_club_boat_with_ids import (
    ListOfCadetAtEventWithIdAndClubDinghies,
    CadetAtEventWithClubDinghyWithId,
)


@dataclass
class ClubDinghyAtEventOnDayForCadet:
    cadet: Cadet
    day: Day
    club_dinghy: ClubDinghy

    @classmethod
    def from_cadet_at_event_with_club_dinghy_and_id(
        cls,
        cadet_at_event_with_club_dinghy_and_id: CadetAtEventWithClubDinghyWithId,
        list_of_cadets: ListOfCadets,
        list_of_club_dinghies: ListOfClubDinghies,
    ):
        return cls(
            cadet=list_of_cadets.cadet_with_id(
                cadet_at_event_with_club_dinghy_and_id.cadet_id
            ),
            day=cadet_at_event_with_club_dinghy_and_id.day,
            club_dinghy=list_of_club_dinghies.object_with_id(
                cadet_at_event_with_club_dinghy_and_id.club_dinghy_id
            ),
        )


class DictOfDaysAndClubDinghiesAtEventForCadet(Dict[Day, ClubDinghy]):
    def has_dinghy_on_day(self, day: Day, dinghy: ClubDinghy):
        dinghy_on_day = self.get(day,None)
        if dinghy_on_day is None:
            return False

        return dinghy_on_day == dinghy

    def unique_list_of_dinghies(self) -> ListOfClubDinghies:
        return ListOfClubDinghies(list(set(self.values())))

    def remove_cadet_from_event_on_day(self, day):
        try:
            self.pop(day)
        except:
            pass

class ListOfClubDinghysAtEventOnDayForCadet(List[ClubDinghyAtEventOnDayForCadet]):
    @classmethod
    def from_list_of_cadets_at_event_with_id_and_club_dinghy(
        cls,
        list_of_cadets_at_event_with_id_and_club_dinghy: ListOfCadetAtEventWithIdAndClubDinghies,
        list_of_cadets: ListOfCadets,
        list_of_club_dinghies: ListOfClubDinghies,
    ):
        return cls(
            [
                ClubDinghyAtEventOnDayForCadet.from_cadet_at_event_with_club_dinghy_and_id(
                    cadet_at_event_with_club_dinghy_and_id=cadet_at_event_with_club_dinghy_and_id,
                    list_of_cadets=list_of_cadets,
                    list_of_club_dinghies=list_of_club_dinghies,
                )
                for cadet_at_event_with_club_dinghy_and_id in list_of_cadets_at_event_with_id_and_club_dinghy
            ]
        )

    def unique_list_of_cadets(self) -> ListOfCadets:
        list_of_cadets = [cadet_and_boat.cadet for cadet_and_boat in self]
        return ListOfCadets(list(set(list_of_cadets)))

    def dict_of_days_and_club_dinghies_for_cadet(
        self, cadet: Cadet
    ) -> DictOfDaysAndClubDinghiesAtEventForCadet:
        subset_for_cadet = self.subset_for_cadet(cadet)

        return DictOfDaysAndClubDinghiesAtEventForCadet(
            dict(
                [
                    (cadet_and_boat.day, cadet_and_boat.club_dinghy)
                    for cadet_and_boat in subset_for_cadet
                ]
            )
        )

    def subset_for_cadet(self, cadet: Cadet):
        return ListOfClubDinghysAtEventOnDayForCadet(
            [cadet_and_boat for cadet_and_boat in self if cadet_and_boat.cadet == cadet]
        )


class DictOfCadetsAndClubDinghiesAtEvent(
    Dict[Cadet, DictOfDaysAndClubDinghiesAtEventForCadet]
):
    def __init__(
        self,
        raw_dict,
        event: Event,
        list_of_cadets_at_event_with_id_and_club_dinghy: ListOfCadetAtEventWithIdAndClubDinghies,
            list_of_club_dinghies: ListOfClubDinghies,
    ):
        super().__init__(raw_dict)

        self._list_of_cadets_at_event_with_id_and_club_dinghy = (
            list_of_cadets_at_event_with_id_and_club_dinghy
        )
        self._list_of_club_dinghies = list_of_club_dinghies
        self._event = event


    def unique_sorted_list_of_allocated_club_dinghys_allocated_at_event(self) -> ListOfClubDinghies:
        dinghies_for_cadet = [dict_of_dinghies.unique_list_of_dinghies() for dict_of_dinghies in self.values()]
        all_dinghies_as_single_list = flatten(dinghies_for_cadet)
        sorted_list = [dinghy for dinghy in self.list_of_club_dinghies if dinghy in all_dinghies_as_single_list]

        return ListOfClubDinghies(sorted_list)

    def remove_cadet_from_event(self, cadet: Cadet):
        for day in self.event.weekdays_in_event():
            self.remove_cadet_from_event_on_day(cadet=cadet, day=day)

        try:
            self.pop(cadet)
        except:
            pass

    def remove_cadet_from_event_on_day(self, cadet: Cadet, day: Day):
        current_allocation = self.get_club_boat_allocation_for_cadet(cadet)
        current_allocation.remove_cadet_from_event_on_day(day)
        self.list_of_cadets_at_event_with_id_and_club_dinghy.delete_allocation_for_cadet_on_day(cadet_id=cadet.id, day=day)

    def get_club_boat_allocation_for_cadet(self, cadet: Cadet):
        return self.get(cadet, DictOfDaysAndClubDinghiesAtEventForCadet())

    def club_dinghys_for_cadet(self, cadet: Cadet) -> DictOfDaysAndClubDinghiesAtEventForCadet:
        return self.get(cadet)

    @property
    def list_of_club_dinghies(self) ->ListOfClubDinghies:
        return self._list_of_club_dinghies

    @property
    def list_of_cadets_at_event_with_id_and_club_dinghy(
        self,
    ) -> ListOfCadetAtEventWithIdAndClubDinghies:
        return self._list_of_cadets_at_event_with_id_and_club_dinghy

    @property
    def event(self) -> Event:
        return self._event

    @property
    def list_of_cadets(self) -> ListOfCadets:
        return ListOfCadets(list(self.keys()))


def compose_dict_of_cadets_and_club_dinghies_at_event(
    event_id: str,
    list_of_events: ListOfEvents,
    list_of_cadets: ListOfCadets,
    list_of_club_dinghies: ListOfClubDinghies,
    list_of_cadets_at_event_with_id_and_club_dinghy: ListOfCadetAtEventWithIdAndClubDinghies,
) -> DictOfCadetsAndClubDinghiesAtEvent:
    event = list_of_events.object_with_id(event_id)
    raw_dict = compose_raw_dict_of_cadets_and_club_dinghies_at_event(
        list_of_cadets=list_of_cadets,
        list_of_club_dinghies=list_of_club_dinghies,
        list_of_cadets_at_event_with_id_and_club_dinghy=list_of_cadets_at_event_with_id_and_club_dinghy,
    )

    return DictOfCadetsAndClubDinghiesAtEvent(
        raw_dict=raw_dict,
        event=event,
        list_of_cadets_at_event_with_id_and_club_dinghy=list_of_cadets_at_event_with_id_and_club_dinghy,
        list_of_club_dinghies=list_of_club_dinghies
    )


def compose_raw_dict_of_cadets_and_club_dinghies_at_event(
    list_of_cadets: ListOfCadets,
    list_of_club_dinghies: ListOfClubDinghies,
    list_of_cadets_at_event_with_id_and_club_dinghy: ListOfCadetAtEventWithIdAndClubDinghies,
) -> Dict[Cadet, DictOfDaysAndClubDinghiesAtEventForCadet]:
    list_of_club_dinghies_at_event_on_day_for_cadet = ListOfClubDinghysAtEventOnDayForCadet.from_list_of_cadets_at_event_with_id_and_club_dinghy(
        list_of_club_dinghies=list_of_club_dinghies,
        list_of_cadets=list_of_cadets,
        list_of_cadets_at_event_with_id_and_club_dinghy=list_of_cadets_at_event_with_id_and_club_dinghy,
    )

    cadets_at_event = (
        list_of_club_dinghies_at_event_on_day_for_cadet.unique_list_of_cadets()
    )

    return dict(
        [
            (
                cadet,
                list_of_club_dinghies_at_event_on_day_for_cadet.dict_of_days_and_club_dinghies_for_cadet(
                    cadet
                ),
            )
            for cadet in cadets_at_event
        ]
    )
