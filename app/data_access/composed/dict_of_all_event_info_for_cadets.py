from typing import Dict

from app.data_access.composed.composed_base import ComposedBaseData
from app.objects.cadets import Cadet
from app.objects.composed.cadets_at_event_with_boat_classes_and_partners import \
     DictOfDaysBoatClassAndPartners, DictOfCadetsAndBoatClassAndPartners
from app.objects.composed.cadets_at_event_with_groups import  DaysAndGroups, DictOfCadetsWithDaysAndGroupsAtEvent
from app.objects.composed.cadets_at_event_with_registration_data import DictOfCadetsWithRegistrationData
from app.objects.composed.cadets_with_all_event_info import DictOfAllEventInfoForCadets, AllEventInfoForCadet
from app.objects.composed.people_at_event_with_club_dinghies import  DictOfDaysAndClubDinghiesAtEventForPerson, DictOfPeopleAndClubDinghiesAtEvent
from app.objects.events import ListOfEvents, Event


class ComposedDataAllEventInfoForCadets(ComposedBaseData):
    def get_dict_of_all_event_info_for_cadets(self, event: Event):
        event_id = event.id
        dict_of_cadets_and_boat_classes_and_partners =self.object_store.get(
            self.object_store.data_api.data_list_of_cadets_with_dinghies_at_event.get_dict_of_cadets_and_boat_classes_and_partners_at_events,
            event_id=event_id)

        dict_of_cadets_and_club_dinghies_at_event = self.object_store.get(
            self.object_store.data_api.data_list_of_cadets_at_event_with_club_dinghies.read_dict_of_cadets_and_club_dinghies_at_event,
            event_id=event_id)

        dict_of_cadets_with_registration_data=self.object_store.get(self.object_store.data_api.data_cadets_at_event.read_dict_of_cadets_with_registration_data_at_event,
                         event_id=event_id)

        dict_of_cadets_with_days_and_groups = self.object_store.get(
            self.object_store.data_api.data_list_of_cadets_with_groups.get_dict_of_cadets_with_groups_at_event,
        event_id=event_id,
    )


        return compose_dict_of_all_event_info_for_cadet(event=event,
                                                        dict_of_cadets_and_boat_class_and_partners=dict_of_cadets_and_boat_classes_and_partners,
                                                        dict_of_cadets_and_club_dinghies_at_event=dict_of_cadets_and_club_dinghies_at_event,
                                                        dict_of_cadets_with_registration_data=dict_of_cadets_with_registration_data,
                                                        dict_of_cadets_with_days_and_groups=dict_of_cadets_with_days_and_groups
                                                        )


def compose_dict_of_all_event_info_for_cadet(
    event: Event,
    dict_of_cadets_and_boat_class_and_partners: DictOfCadetsAndBoatClassAndPartners,
    dict_of_cadets_and_club_dinghies_at_event: DictOfPeopleAndClubDinghiesAtEvent,
    dict_of_cadets_with_registration_data: DictOfCadetsWithRegistrationData,
    dict_of_cadets_with_days_and_groups: DictOfCadetsWithDaysAndGroupsAtEvent,

) -> DictOfAllEventInfoForCadets:
    raw_dict = compose_raw_dict_of_all_event_info_for_cadet(
        dict_of_cadets_with_registration_data=dict_of_cadets_with_registration_data,
        dict_of_cadets_and_club_dinghies_at_event=dict_of_cadets_and_club_dinghies_at_event,
        dict_of_cadets_with_days_and_groups=dict_of_cadets_with_days_and_groups,
        dict_of_cadets_and_boat_class_and_partners=dict_of_cadets_and_boat_class_and_partners,
    )
    return DictOfAllEventInfoForCadets(
        raw_dict=raw_dict,
        dict_of_cadets_with_registration_data=dict_of_cadets_with_registration_data,
        dict_of_cadets_and_club_dinghies_at_event=dict_of_cadets_and_club_dinghies_at_event,
        dict_of_cadets_with_days_and_groups=dict_of_cadets_with_days_and_groups,
        dict_of_cadets_and_boat_class_and_partners=dict_of_cadets_and_boat_class_and_partners,
        event=event,
    )


def compose_raw_dict_of_all_event_info_for_cadet(
    dict_of_cadets_and_boat_class_and_partners: DictOfCadetsAndBoatClassAndPartners,
    dict_of_cadets_and_club_dinghies_at_event: DictOfPeopleAndClubDinghiesAtEvent,
    dict_of_cadets_with_registration_data: DictOfCadetsWithRegistrationData,
    dict_of_cadets_with_days_and_groups: DictOfCadetsWithDaysAndGroupsAtEvent,
) -> Dict[Cadet, AllEventInfoForCadet]:
    list_of_all_cadets_with_event_data = (
        dict_of_cadets_with_registration_data.list_of_active_cadets()
    )

    return dict(
        [
            (
                cadet,
                AllEventInfoForCadet(
                    registration_data=dict_of_cadets_with_registration_data[cadet],
                    days_and_boat_class=dict_of_cadets_and_boat_class_and_partners.get(
                        cadet, DictOfDaysBoatClassAndPartners()
                    ),
                    days_and_groups=dict_of_cadets_with_days_and_groups.get(
                        cadet, DaysAndGroups()
                    ),
                    days_and_club_dinghies=dict_of_cadets_and_club_dinghies_at_event.get(
                        cadet, DictOfDaysAndClubDinghiesAtEventForPerson()
                    ),
                ),
            )
            for cadet in list_of_all_cadets_with_event_data
        ]
    )
