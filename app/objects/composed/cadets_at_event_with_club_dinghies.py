from dataclasses import dataclass
from typing import List, Dict

from app.objects.events import ListOfEvents, Event

from app.objects.cadets import Cadet, ListOfCadets
from app.objects.club_dinghies import ClubDinghy, ListOfClubDinghies
from app.objects.day_selectors import Day
from app.objects.cadet_at_event_with_club_boat_with_ids import ListOfCadetAtEventWithIdAndClubDinghies, CadetAtEventWithClubDinghyWithId

@dataclass
class ClubDinghyAtEventOnDayForCadet:
    cadet: Cadet
    day: Day
    club_dinghy: ClubDinghy

    @classmethod
    def from_cadet_at_event_with_club_dinghy_and_id(cls, cadet_at_event_with_club_dinghy_and_id: CadetAtEventWithClubDinghyWithId,
                                                    list_of_cadets: ListOfCadets, list_of_club_dinghies: ListOfClubDinghies):

        return cls(
            cadet=list_of_cadets.cadet_with_id(cadet_at_event_with_club_dinghy_and_id.cadet_id),
            day = cadet_at_event_with_club_dinghy_and_id.day,
            club_dinghy=list_of_club_dinghies.object_with_id(cadet_at_event_with_club_dinghy_and_id.club_dinghy_id)
        )



class DictOfDaysAndClubDinghiesAtEventForCadet(Dict[Day, ClubDinghy]):
    pass

class ListOfClubDinghysAtEventOnDayForCadet(List[ClubDinghyAtEventOnDayForCadet]):
    @classmethod
    def from_list_of_cadets_at_event_with_id_and_club_dinghy(cls,  list_of_cadets_at_event_with_id_and_club_dinghy: ListOfCadetAtEventWithIdAndClubDinghies,
                                                             list_of_cadets: ListOfCadets,
                                                             list_of_club_dinghies: ListOfClubDinghies ):

        return cls(
            [
                ClubDinghyAtEventOnDayForCadet.from_cadet_at_event_with_club_dinghy_and_id(
                    cadet_at_event_with_club_dinghy_and_id=cadet_at_event_with_club_dinghy_and_id,
                    list_of_cadets=list_of_cadets,
                    list_of_club_dinghies=list_of_club_dinghies
                ) for cadet_at_event_with_club_dinghy_and_id in list_of_cadets_at_event_with_id_and_club_dinghy
            ]
        )

    def unique_list_of_cadets(self) -> ListOfCadets:
        list_of_cadets = [cadet_and_boat.cadet for cadet_and_boat in self]
        return ListOfCadets(list(set(list_of_cadets)))

    def dict_of_days_and_club_dinghies_for_cadet(self, cadet: Cadet) -> DictOfDaysAndClubDinghiesAtEventForCadet:
        subset_for_cadet = self.subset_for_cadet(cadet)

        return DictOfDaysAndClubDinghiesAtEventForCadet(
            dict(
                [
                    (
                    cadet_and_boat.day,
                    cadet_and_boat.club_dinghy
                    )
                    for cadet_and_boat in subset_for_cadet
                ]
            )
        )

    def subset_for_cadet(self, cadet: Cadet):
        return ListOfClubDinghysAtEventOnDayForCadet([
            cadet_and_boat
            for cadet_and_boat in self
            if cadet_and_boat.cadet == cadet
        ])

class DictOfCadetsAndClubDinghiesAtEvent(Dict[Cadet, DictOfDaysAndClubDinghiesAtEventForCadet]):
    def __init__(self,  raw_dict, event: Event,
                                                      list_of_cadets_at_event_with_id_and_club_dinghy: ListOfCadetAtEventWithIdAndClubDinghies):
        super().__init__(raw_dict)

        self._list_of_cadets_at_event_with_id_and_club_dinghy = list_of_cadets_at_event_with_id_and_club_dinghy
        self._event = event

    @property
    def list_of_cadets_at_event_with_id_and_club_dinghy(self) -> ListOfCadetAtEventWithIdAndClubDinghies:
        return self._list_of_cadets_at_event_with_id_and_club_dinghy

    @property
    def event(self) -> Event:
        return self._event




def compose_dict_of_cadets_and_club_dinghies_at_event(event_id: str,
                                                      list_of_events: ListOfEvents,
                                                      list_of_cadets: ListOfCadets,
                                                      list_of_club_dinghies: ListOfClubDinghies,
                                                      list_of_cadets_at_event_with_id_and_club_dinghy: ListOfCadetAtEventWithIdAndClubDinghies) -> DictOfCadetsAndClubDinghiesAtEvent:

    event = list_of_events.object_with_id(event_id)
    raw_dict = compose_raw_dict_of_cadets_and_club_dinghies_at_event(
        list_of_cadets=list_of_cadets,
        list_of_club_dinghies=list_of_club_dinghies,
        list_of_cadets_at_event_with_id_and_club_dinghy=list_of_cadets_at_event_with_id_and_club_dinghy
    )

    return DictOfCadetsAndClubDinghiesAtEvent(
        raw_dict=raw_dict,
        event=event,
        list_of_cadets_at_event_with_id_and_club_dinghy=list_of_cadets_at_event_with_id_and_club_dinghy
    )

def compose_raw_dict_of_cadets_and_club_dinghies_at_event(
                                                      list_of_cadets: ListOfCadets,
                                                      list_of_club_dinghies: ListOfClubDinghies,
                                                      list_of_cadets_at_event_with_id_and_club_dinghy: ListOfCadetAtEventWithIdAndClubDinghies) -> Dict[Cadet, DictOfDaysAndClubDinghiesAtEventForCadet]:

    list_of_club_dinghies_at_event_on_day_for_cadet = ListOfClubDinghysAtEventOnDayForCadet.from_list_of_cadets_at_event_with_id_and_club_dinghy(
        list_of_club_dinghies=list_of_club_dinghies,
        list_of_cadets=list_of_cadets,
        list_of_cadets_at_event_with_id_and_club_dinghy=list_of_cadets_at_event_with_id_and_club_dinghy
    )

    cadets_at_event = list_of_club_dinghies_at_event_on_day_for_cadet.unique_list_of_cadets()

    return dict(
        [
            (cadet,
             list_of_club_dinghies_at_event_on_day_for_cadet.dict_of_days_and_club_dinghies_for_cadet(cadet))
            for cadet in cadets_at_event
        ]
    )
