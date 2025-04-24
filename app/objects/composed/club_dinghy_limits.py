from dataclasses import dataclass
from typing import Dict, Union, List

from app.objects.club_dinghies import ClubDinghy, ListOfClubDinghyLimits, ListOfClubDinghies, event_id_for_generic_limit
from app.objects.events import Event, ListOfEvents
from app.objects.utilities.exceptions import missing_data

generic_limit_event = object()

@dataclass
class ClubDinghyAndGenericLimit:
    club_dinghy: ClubDinghy
    limit: int
    hidden: bool = False

    def __repr__(self):
        return self.club_dinghy.name

class DictOfClubDinghyLimitsForEvent(Dict[ClubDinghy, int]):
    @classmethod
    def create_empty(cls):
        return cls({})

    def limit_for_boat(self, club_dinghy: ClubDinghy, default = 0) -> int:
        return self.get(club_dinghy, default)

    def set_limit_for_boat(self, club_dinghy: ClubDinghy, limit: int):
        self[club_dinghy] = limit

    def clear_limit_for_boat(self, club_dinghy: ClubDinghy):
        try:
            self.pop(club_dinghy)
        except:
            pass


class DictOfClubDinghyLimits(Dict[Event, DictOfClubDinghyLimitsForEvent]):
    def __init__(self, raw_dict: Dict[Event, DictOfClubDinghyLimitsForEvent],
                 list_of_club_dinghy_limits: ListOfClubDinghyLimits,
                 list_of_club_dinghies: ListOfClubDinghies):
        super().__init__(raw_dict)
        self._list_of_club_dinghy_limits = list_of_club_dinghy_limits
        self._list_of_club_dinghies = list_of_club_dinghies

    @property
    def list_of_club_dinghy_limits(self):
        return self._list_of_club_dinghy_limits

    @property
    def list_of_club_dinghies(self):
        return self._list_of_club_dinghies

    def dict_of_limits_for_all_visible_club_boats(self, event: Event) -> Dict[str, int]:
        return dict(
            [
                (boat.name,
                 self.get_limit_at_event(
                     event=event, club_boat=boat, default=0
                 ))
                for boat in self.list_of_club_dinghies
                if not boat.hidden
            ]
        )

    def list_of_generic_limits_for_all_boats(self) -> List[ClubDinghyAndGenericLimit]:
        return \
            [
                ClubDinghyAndGenericLimit(club_dinghy=boat, limit=
                 self.get_generic_limit(
                     club_boat=boat, default=0,

                 ),
                                          hidden=boat.hidden)
                for boat in self.list_of_club_dinghies
            ]


    def dict_of_limits_for_all_boats_at_event(self, event: Event) -> Dict[ClubDinghy, int]:
        return dict(
            [
                (boat,
                 self.get_limit_at_event(
                     event=event, club_boat=boat
                 ))
                for boat in self.list_of_club_dinghies
            ]
        )

    def get_limit_at_event(self, event: Union[Event, object], club_boat: ClubDinghy, default =0) -> int:
        limit = self.get_underlying_limit_at_event(event, club_boat, default=missing_data)
        if limit is missing_data:
            limit = self.get_generic_limit(club_boat, default=default)

        return limit

    def get_generic_limit(self, club_boat: ClubDinghy, default=0) -> int:
        return self.get_underlying_limit_at_event(event=generic_limit_event, club_boat=club_boat, default=default)

    def get_underlying_limit_at_event(self, event: Union[Event, object], club_boat: ClubDinghy, default =0) -> int:
        limits_at_event = self.get_limits_for_event(event)
        limit = limits_at_event.limit_for_boat(club_boat, default=default)

        return limit

    def clear_and_set_generic_limit(self,  original_boat: ClubDinghy, new_boat: ClubDinghy, new_limit:int):
        self.clear_generic_limit(original_boat)
        self.set_generic_limit(new_boat, new_limit)

    def clear_generic_limit(self, club_boat: ClubDinghy):
        limits_at_event = self.get_limits_for_event(generic_limit_event)
        limits_at_event.clear_limit_for_boat(club_boat)

    def set_generic_limit(self, club_boat: ClubDinghy, limit: int):
        self.set_limit_at_event(event=generic_limit_event, club_boat=club_boat, limit=limit)

    def set_limit_at_event(self, event: Union[Event, object], club_boat: ClubDinghy, limit: int):
        limits_at_event = self.get_limits_for_event(event)
        limits_at_event.set_limit_for_boat(club_dinghy=club_boat, limit=limit)

        if event is generic_limit_event:
            self.list_of_club_dinghy_limits.update_general_limit_for_club_dinghy_id(club_dinghy_id=club_boat.id,
                                                                                    limit=limit)
        else:
            self.list_of_club_dinghy_limits.update_limit_for_event_id_and_club_dinghy_id(
                event_id=event.id,
                club_dinghy_id=club_boat.id,
                limit=limit
            )

    def get_limits_for_event(self, event: Union[Event, object]) -> DictOfClubDinghyLimitsForEvent:

        limits = self.get(event, missing_data)
        if limits is missing_data:
            self[event] = limits = DictOfClubDinghyLimitsForEvent.create_empty()

        return limits


def compose_club_dinghy_limits(
        list_of_club_dinghy_limits: ListOfClubDinghyLimits,
        list_of_club_dinghies: ListOfClubDinghies,
        list_of_events: ListOfEvents
) -> DictOfClubDinghyLimits:
    raw_dict =get_raw_dict_of_club_dinghy_limits(
        list_of_club_dinghy_limits=list_of_club_dinghy_limits,
        list_of_events=list_of_events,
        list_of_club_dinghies=list_of_club_dinghies
    )

    return DictOfClubDinghyLimits(
        raw_dict=raw_dict,
        list_of_club_dinghy_limits=list_of_club_dinghy_limits,
        list_of_club_dinghies=list_of_club_dinghies
    )

def get_raw_dict_of_club_dinghy_limits(
        list_of_club_dinghy_limits: ListOfClubDinghyLimits,
        list_of_club_dinghies: ListOfClubDinghies,
        list_of_events: ListOfEvents
):
    list_of_event_ids= list_of_club_dinghy_limits.unique_list_of_event_ids()
    raw_dict = {}
    for event_id  in list_of_event_ids:
        all_limits_for_event = DictOfClubDinghyLimitsForEvent()

        for limit_item in list_of_club_dinghy_limits:
            if not limit_item.event_id == event_id:
                continue
            club_dinghy = list_of_club_dinghies.club_dinghy_with_id(limit_item.club_dinghy_id)

            all_limits_for_event[club_dinghy] = limit_item.limit

        if event_id == event_id_for_generic_limit:
            event = generic_limit_event
        else:
            event = list_of_events.event_with_id(event_id)

        raw_dict[event] = all_limits_for_event

    return raw_dict
