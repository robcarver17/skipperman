from dataclasses import dataclass
from typing import Dict

from app.objects.boat_classes import ListOfBoatClasses
from app.objects.club_dinghies import ListOfClubDinghies
from app.objects.composed.cadets_at_event_with_boat_classes_groups_club_dnghies_and_partners import (
    ListOfCadetBoatClassClubDinghyGroupAndPartnerAtEventOnDay,
    CadetBoatClassClubDinghyGroupAndPartnerAtEventOnDay,
)
from app.objects.composed.cadets_with_all_event_info_functions import (
    cadets_not_allocated_to_group_on_at_least_one_day_attending,
)
from app.objects.day_selectors import Day
from app.objects.partners import no_partnership_given_partner_cadet
from app.objects.utilities.exceptions import MissingData, arg_not_passed
from app.objects.groups import Group, unallocated_group, ListOfGroups

from app.objects.events import Event

from app.objects.cadets import Cadet, ListOfCadets, NO_CADET_ID

from app.objects.composed.cadets_at_event_with_boat_classes_and_partners import (
    DictOfDaysBoatClassAndPartners,
    DictOfCadetsAndBoatClassAndPartners,
)

from app.objects.composed.people_at_event_with_club_dinghies import (
    DictOfDaysAndClubDinghiesAtEventForPerson,
    DictOfPeopleAndClubDinghiesAtEvent,
)

from app.objects.composed.cadets_at_event_with_registration_data import (
    CadetRegistrationData,
    DictOfCadetsWithRegistrationData,
)
from app.objects.composed.cadets_at_event_with_groups import (
    DaysAndGroups,
    DictOfCadetsWithDaysAndGroupsAtEvent,
)


@dataclass
class AllEventInfoForCadet:
    registration_data: CadetRegistrationData
    days_and_groups: DaysAndGroups
    days_and_club_dinghies: DictOfDaysAndClubDinghiesAtEventForPerson
    days_and_boat_class: DictOfDaysBoatClassAndPartners

    def is_active_registration(self):
        return self.registration_data.status.is_active


class DictOfAllEventInfoForCadets(Dict[Cadet, AllEventInfoForCadet]):
    def __init__(
        self,
        raw_dict: Dict[Cadet, AllEventInfoForCadet],
        dict_of_cadets_and_boat_class_and_partners: DictOfCadetsAndBoatClassAndPartners,
        dict_of_cadets_and_club_dinghies_at_event: DictOfPeopleAndClubDinghiesAtEvent,
        dict_of_cadets_with_registration_data: DictOfCadetsWithRegistrationData,
        dict_of_cadets_with_days_and_groups: DictOfCadetsWithDaysAndGroupsAtEvent,
        list_of_groups: ListOfGroups,
        list_of_club_dinghies: ListOfClubDinghies,
        list_of_boat_classes: ListOfBoatClasses,
        event: Event,
    ):
        super().__init__(raw_dict)

        self._dict_of_cadets_and_boat_class_and_partners = (
            dict_of_cadets_and_boat_class_and_partners
        )
        self._dict_of_cadets_and_club_dinghies_at_event = (
            dict_of_cadets_and_club_dinghies_at_event
        )
        self._dict_of_cadets_with_registration_data = (
            dict_of_cadets_with_registration_data
        )
        self._dict_of_cadets_with_days_and_groups = dict_of_cadets_with_days_and_groups
        self._list_of_groups = list_of_groups
        self._list_of_club_dinghies = list_of_club_dinghies
        self._list_of_boat_classes = list_of_boat_classes

        self._event = event

    def get_most_common_partner_id_across_days(
        self, cadet: Cadet, default=NO_CADET_ID
    ) -> str:
        event_data_for_cadet = self.event_data_for_cadet(cadet)

        return event_data_for_cadet.days_and_boat_class.get_most_common_partner_id_across_days(
            default
        )

    def list_of_cadets_boat_classes_groups_sail_numbers_and_partners_at_event_on_day(
        self, day: Day
    ) -> ListOfCadetBoatClassClubDinghyGroupAndPartnerAtEventOnDay:
        new_list = []
        for cadet in self.list_of_cadets:
            group = (
                self.dict_of_cadets_with_days_and_groups.get_days_and_groups_for_cadet(
                    cadet
                ).group_on_day(day)
            )
            club_dinghy = (
                self.dict_of_cadets_and_club_dinghies_at_event.club_dinghys_for_person(
                    cadet
                ).dinghy_on_day(day)
            )
            boat_class_partners_for_cadet = self.dict_of_cadets_and_boat_class_and_partners.boat_classes_and_partner_for_cadet(
                cadet
            )

            sail_number = boat_class_partners_for_cadet.sail_number_on_day(day)
            partner_cadet = boat_class_partners_for_cadet.partner_on_day(day)
            boat_class = boat_class_partners_for_cadet.boat_class_on_day(day)

            new_list.append(
                CadetBoatClassClubDinghyGroupAndPartnerAtEventOnDay(
                    cadet=cadet,
                    day=day,
                    group=group,
                    club_dinghy=club_dinghy,
                    partner_cadet=partner_cadet,
                    sail_number=sail_number,
                    boat_class=boat_class,
                )
            )

        return ListOfCadetBoatClassClubDinghyGroupAndPartnerAtEventOnDay(new_list)

    def cadets_in_group_during_event(self, group: Group) -> ListOfCadets:
        if group is unallocated_group:
            return cadets_not_allocated_to_group_on_at_least_one_day_attending(
                dict_of_cadets_with_registration_data=self.dict_of_cadets_with_registration_data,
                dict_of_cadets_with_days_and_groups=self.dict_of_cadets_with_days_and_groups,
            )
        else:
            return (
                self.dict_of_cadets_with_days_and_groups.cadets_in_group_during_event(
                    group
                )
            )

    def get_most_common_boat_class_name_across_days(self, cadet: Cadet) -> str:
        event_data_for_cadet = self.event_data_for_cadet(cadet)
        boat_class = event_data_for_cadet.days_and_boat_class.most_common_boat_class()

        return boat_class.name

    def get_most_common_club_boat_name_across_days(self, cadet: Cadet) -> str:
        event_data_for_cadet = self.event_data_for_cadet(cadet)
        club_dinghy = event_data_for_cadet.days_and_club_dinghies.most_common()
        return club_dinghy.name

    def get_most_common_group_name_across_days(self, cadet: Cadet) -> str:
        event_data_for_cadet = self.event_data_for_cadet(cadet)
        group = event_data_for_cadet.days_and_groups.most_common()
        return group.name

    def event_data_for_cadet(
        self, cadet: Cadet, default=arg_not_passed
    ) -> AllEventInfoForCadet:
        all_data = self.get(cadet, default)
        if all_data is arg_not_passed:
            raise MissingData

        return all_data

    def sorted_list_of_groups_at_event(self):
        return self.dict_of_cadets_with_days_and_groups.sorted_all_groups_at_event(
            self.list_of_groups
        )

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
    def dict_of_cadets_with_days_and_groups(
        self,
    ) -> DictOfCadetsWithDaysAndGroupsAtEvent:
        return self._dict_of_cadets_with_days_and_groups

    @property
    def list_of_cadets(self) -> ListOfCadets:
        return ListOfCadets(list(self.keys()))

    @property
    def list_of_groups(self) -> ListOfGroups:
        return self._list_of_groups

    @property
    def list_of_boat_classes(self) -> ListOfBoatClasses:
        return self._list_of_boat_classes

    @property
    def list_of_club_dinghies(self) -> ListOfClubDinghies:
        return self._list_of_club_dinghies

    @property
    def event(self):
        return self._event
