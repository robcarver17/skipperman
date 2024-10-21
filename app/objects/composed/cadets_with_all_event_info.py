from dataclasses import dataclass
from typing import Dict

from app.objects.events import Event, ListOfEvents

from app.objects.cadets import Cadet

from app.objects.composed.cadets_at_event_with_boat_classes_and_partners import DictOfDaysBoatClassAndPartners, DictOfCadetsAndBoatClassAndPartners

from app.objects.composed.cadets_at_event_with_club_dinghies import DictOfDaysAndClubDinghiesAtEventForCadet, DictOfCadetsAndClubDinghiesAtEvent

from app.objects.composed.cadets_at_event_with_registration_data import CadetRegistrationData, DictOfCadetsWithRegistrationData
from app.objects.composed.cadets_at_event_with_groups import DaysAndGroups, DictOfCadetsWithDaysAndGroupsAtEvent


@dataclass
class AllEventInfoForCadet:
    registration_data: CadetRegistrationData
    days_and_groups: DaysAndGroups
    days_and_club_dinghies: DictOfDaysAndClubDinghiesAtEventForCadet
    days_and_boat_class: DictOfDaysBoatClassAndPartners

    def is_active_registration(self):
        return self.registration_data.status.is_active

class DictOfAllEventInfoForCadet(Dict[Cadet, AllEventInfoForCadet]):
    def __init__(self, raw_dict: Dict[Cadet, AllEventInfoForCadet],
                 dict_of_cadets_and_boat_class_and_partners: DictOfCadetsAndBoatClassAndPartners,
                 dict_of_cadets_and_club_dinghies_at_event: DictOfCadetsAndClubDinghiesAtEvent,
                 dict_of_cadets_with_registration_data: DictOfCadetsWithRegistrationData,
                 dict_of_cadets_with_days_and_groups: DictOfCadetsWithDaysAndGroupsAtEvent,
                 event: Event
                 ):

        super().__init__(raw_dict)

        self._dict_of_cadets_and_boat_class_and_partners = dict_of_cadets_and_boat_class_and_partners
        self._dict_of_cadets_and_club_dinghies_at_event = dict_of_cadets_and_club_dinghies_at_event
        self._dict_of_cadets_with_registration_data = dict_of_cadets_with_registration_data
        self._dict_of_cadets_with_days_and_groups = dict_of_cadets_with_days_and_groups
        self._event = event


    @property
    def dict_of_cadets_and_boat_class_and_partners(self):
        return self._dict_of_cadets_and_boat_class_and_partners

    @property
    def dict_of_cadets_and_club_dinghies_at_event(self):
        return self._dict_of_cadets_and_club_dinghies_at_event

    @property
    def dict_of_cadets_with_registration_data(self) -> DictOfCadetsWithRegistrationData:
        return self._dict_of_cadets_with_registration_data

    @property
    def dict_of_cadets_with_days_and_groups(self):
        return self._dict_of_cadets_with_days_and_groups

    @property
    def event(self):
        return self._event


def compose_dict_of_all_event_info_for_cadet(
    event_id: str,
    list_of_events: ListOfEvents,
    dict_of_cadets_and_boat_class_and_partners: DictOfCadetsAndBoatClassAndPartners,
    dict_of_cadets_and_club_dinghies_at_event: DictOfCadetsAndClubDinghiesAtEvent,
    dict_of_cadets_with_registration_data: DictOfCadetsWithRegistrationData,
    dict_of_cadets_with_days_and_groups: DictOfCadetsWithDaysAndGroupsAtEvent,
        active_only:bool
) -> DictOfAllEventInfoForCadet:

    event = list_of_events.object_with_id(event_id)
    raw_dict= compose_raw_dict_of_all_event_info_for_cadet(
        dict_of_cadets_with_registration_data=dict_of_cadets_with_registration_data,
        dict_of_cadets_and_club_dinghies_at_event=dict_of_cadets_and_club_dinghies_at_event,
        dict_of_cadets_with_days_and_groups=dict_of_cadets_with_days_and_groups,
        dict_of_cadets_and_boat_class_and_partners=dict_of_cadets_and_boat_class_and_partners,
        active_only=active_only
    )
    return DictOfAllEventInfoForCadet(
        raw_dict=raw_dict,
        dict_of_cadets_with_registration_data=dict_of_cadets_with_registration_data,
        dict_of_cadets_and_club_dinghies_at_event=dict_of_cadets_and_club_dinghies_at_event,
        dict_of_cadets_with_days_and_groups=dict_of_cadets_with_days_and_groups,
        dict_of_cadets_and_boat_class_and_partners=dict_of_cadets_and_boat_class_and_partners,
        event=event
    )

def compose_raw_dict_of_all_event_info_for_cadet(
    dict_of_cadets_and_boat_class_and_partners: DictOfCadetsAndBoatClassAndPartners,
    dict_of_cadets_and_club_dinghies_at_event: DictOfCadetsAndClubDinghiesAtEvent,
    dict_of_cadets_with_registration_data: DictOfCadetsWithRegistrationData,
    dict_of_cadets_with_days_and_groups: DictOfCadetsWithDaysAndGroupsAtEvent,
    active_only: bool

) -> Dict[Cadet, AllEventInfoForCadet]:

    if active_only:
        list_of_all_cadets_with_event_data = dict_of_cadets_with_registration_data.list_of_active_cadets()
    else:
        list_of_all_cadets_with_event_data= dict_of_cadets_with_registration_data.list_of_cadets()

    return dict(
        [(cadet,
         AllEventInfoForCadet(
            registration_data=dict_of_cadets_with_registration_data[cadet],
            days_and_boat_class=dict_of_cadets_and_boat_class_and_partners.get(cadet, DictOfDaysBoatClassAndPartners()),
            days_and_groups=dict_of_cadets_with_days_and_groups.get(cadet, DaysAndGroups()),
            days_and_club_dinghies=dict_of_cadets_and_club_dinghies_at_event.get(cadet, DictOfDaysAndClubDinghiesAtEventForCadet())
         ))
        for cadet in list_of_all_cadets_with_event_data]
    )
