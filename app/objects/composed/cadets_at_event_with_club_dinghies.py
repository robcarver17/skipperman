from dataclasses import dataclass
from typing import List, Dict

from app.objects.utilities.utils import flatten, most_common

from app.objects.events import ListOfEvents, Event

from app.objects.cadets import Cadet, ListOfCadets
from app.objects.club_dinghies import ClubDinghy, ListOfClubDinghies, no_club_dinghy
from app.objects.day_selectors import Day
from app.objects.cadet_at_event_with_club_boat_with_ids import (
    ListOfCadetAtEventWithIdAndClubDinghies,
    CadetAtEventWithClubDinghyWithId,
)
from app.objects.utilities.exceptions import arg_not_passed


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
            club_dinghy=list_of_club_dinghies.club_dinghy_with_id(
                cadet_at_event_with_club_dinghy_and_id.club_dinghy_id
            ),
        )


class DictOfDaysAndClubDinghiesAtEventForCadet(Dict[Day, ClubDinghy]):
    def allocate_club_boat_on_day(self, day: Day, club_boat: ClubDinghy):
        if club_boat is no_club_dinghy:
            try:
                self.pop(day)
            except:
                pass

        self[day] = club_boat

    def most_common(self) -> ClubDinghy:
        return most_common(self.list_of_dinghies(), default=no_club_dinghy)

    def has_any_dinghy_on_any_day(self):
        unique_list_of_dinghies = self.unique_list_of_dinghies()
        if len(unique_list_of_dinghies) > 0:
            return True
        if len(unique_list_of_dinghies) == 0:
            return False
        single_dinghy = unique_list_of_dinghies[0]
        if single_dinghy is no_club_dinghy:
            return False

    def has_any_dinghy_on_specific_day(self, day: Day) -> bool:
        dinghy_on_day = self.dinghy_on_day(day, default=no_club_dinghy)
        no_dinghy_on_day = dinghy_on_day is no_club_dinghy

        return not no_dinghy_on_day

    def has_specific_dinghy_on_day(self, day: Day, dinghy: ClubDinghy):
        dinghy_on_day = self.dinghy_on_day(day, default=no_club_dinghy)
        if dinghy_on_day == no_club_dinghy:
            return False

        return dinghy_on_day == dinghy

    def dinghy_on_day(self, day, default=arg_not_passed) -> ClubDinghy:
        if default is arg_not_passed:
            default = no_club_dinghy

        return self.get(day, default)

    def unique_list_of_dinghies(self) -> ListOfClubDinghies:
        return ListOfClubDinghies(list(set(self.values())))

    def list_of_dinghies(self) -> ListOfClubDinghies:
        return ListOfClubDinghies(list(self.values()))

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

    def allocate_club_boat_on_day(self, cadet: Cadet, day: Day, club_boat: ClubDinghy):
        boats_for_cadet = self.club_dinghys_for_cadet(cadet)
        boats_for_cadet.allocate_club_boat_on_day(day=day, club_boat=club_boat)
        self[cadet] = boats_for_cadet

        self.list_of_cadets_at_event_with_id_and_club_dinghy.update_allocation_for_cadet_on_day(
            cadet_id=cadet.id, day=day, club_dinghy_id=club_boat.id
        )

    def unique_sorted_list_of_allocated_club_dinghys_allocated_at_event(
        self,
    ) -> ListOfClubDinghies:
        dinghies_for_cadet = [
            dict_of_dinghies.unique_list_of_dinghies()
            for dict_of_dinghies in self.values()
        ]
        all_dinghies_as_single_list = flatten(dinghies_for_cadet)
        sorted_list = [
            dinghy
            for dinghy in self.list_of_club_dinghies
            if dinghy in all_dinghies_as_single_list
        ]

        return ListOfClubDinghies(sorted_list)

    def remove_cadet_from_event(self, cadet: Cadet):
        current_allocation = self.club_dinghys_for_cadet(cadet)
        if len(current_allocation) == 0:
            return []
        for day in self.event.days_in_event():
            self.remove_cadet_club_boat_allocation_on_day(cadet=cadet, day=day)

        try:
            self.pop(cadet)
        except:
            return []

        return [" - removed club boat allocation %s" % str(current_allocation)]

    def remove_cadet_club_boat_allocation_on_day(self, cadet: Cadet, day: Day):
        current_allocation = self.club_dinghys_for_cadet(cadet)
        current_allocation.remove_cadet_from_event_on_day(day)
        self[cadet] = current_allocation

        self.list_of_cadets_at_event_with_id_and_club_dinghy.delete_allocation_for_cadet_on_day(
            cadet_id=cadet.id, day=day
        )

    def club_dinghys_for_cadet(
        self, cadet: Cadet
    ) -> DictOfDaysAndClubDinghiesAtEventForCadet:
        return self.get(cadet, DictOfDaysAndClubDinghiesAtEventForCadet())

    @property
    def list_of_club_dinghies(self) -> ListOfClubDinghies:
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
    event = list_of_events.event_with_id(event_id)
    raw_dict = compose_raw_dict_of_cadets_and_club_dinghies_at_event(
        list_of_cadets=list_of_cadets,
        list_of_club_dinghies=list_of_club_dinghies,
        list_of_cadets_at_event_with_id_and_club_dinghy=list_of_cadets_at_event_with_id_and_club_dinghy,
    )

    return DictOfCadetsAndClubDinghiesAtEvent(
        raw_dict=raw_dict,
        event=event,
        list_of_cadets_at_event_with_id_and_club_dinghy=list_of_cadets_at_event_with_id_and_club_dinghy,
        list_of_club_dinghies=list_of_club_dinghies,
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
