from dataclasses import dataclass
from typing import Dict, List

from app.objects.boat_classes import BoatClass
from app.objects.club_dinghies import ClubDinghy
from app.objects.day_selectors import DaySelector, Day
from app.objects.exceptions import MissingData
from app.objects.groups import Group, unallocated_group

from app.objects.registration_status import RegistrationStatus

from app.objects.events import Event, ListOfEvents

from app.objects.cadets import Cadet, ListOfCadets

from app.objects.composed.cadets_at_event_with_boat_classes_and_partners import (
    DictOfDaysBoatClassAndPartners,
    DictOfCadetsAndBoatClassAndPartners,
)

from app.objects.composed.cadets_at_event_with_club_dinghies import (
    DictOfDaysAndClubDinghiesAtEventForCadet,
    DictOfCadetsAndClubDinghiesAtEvent,
)

from app.objects.composed.cadets_at_event_with_registration_data import (
    CadetRegistrationData,
    DictOfCadetsWithRegistrationData,
)
from app.objects.composed.cadets_at_event_with_groups import (
    DaysAndGroups,
    DictOfCadetsWithDaysAndGroupsAtEvent,
)


from app.objects.composed.clothing_at_event import (
    DictOfCadetsWithClothingAtEvent,
    ClothingAtEvent,
)
from app.objects.composed.food_at_event import (
    ListOfCadetsWithFoodRequirementsAtEvent,
    DictOfCadetsWithFoodRequirementsAtEvent,
    FoodRequirements,
)


@dataclass
class AllEventInfoForCadet:
    registration_data: CadetRegistrationData
    days_and_groups: DaysAndGroups
    days_and_club_dinghies: DictOfDaysAndClubDinghiesAtEventForCadet
    days_and_boat_class: DictOfDaysBoatClassAndPartners
    food_requirements: FoodRequirements
    clothing: ClothingAtEvent

    def is_active_registration(self):
        return self.registration_data.status.is_active


class DictOfAllEventInfoForCadets(Dict[Cadet, AllEventInfoForCadet]):
    def __init__(
        self,
        raw_dict: Dict[Cadet, AllEventInfoForCadet],
        dict_of_cadets_and_boat_class_and_partners: DictOfCadetsAndBoatClassAndPartners,
        dict_of_cadets_and_club_dinghies_at_event: DictOfCadetsAndClubDinghiesAtEvent,
        dict_of_cadets_with_registration_data: DictOfCadetsWithRegistrationData,
        dict_of_cadets_with_days_and_groups: DictOfCadetsWithDaysAndGroupsAtEvent,
        dict_of_cadets_with_clothing_at_event: DictOfCadetsWithClothingAtEvent,
        dict_of_cadets_with_food_required_at_event: DictOfCadetsWithFoodRequirementsAtEvent,
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
        self._event = event
        self._dict_of_cadets_with_clothing_at_event = (
            dict_of_cadets_with_clothing_at_event
        )
        self._dict_of_cadets_with_food_required_at_event = (
            dict_of_cadets_with_food_required_at_event
        )

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

    def get_most_common_partner_across_days(self, cadet: Cadet) -> Cadet:
        event_data_for_cadet = self.event_data_for_cadet(cadet)

        return event_data_for_cadet.days_and_boat_class.most_common_partner()

    def get_most_common_boat_class_name_across_days(self, cadet: Cadet) -> BoatClass:
        event_data_for_cadet = self.event_data_for_cadet(cadet)

        return event_data_for_cadet.days_and_boat_class.most_common_boat_class()

    def get_most_common_club_boat_name_across_days(self, cadet: Cadet) -> ClubDinghy:
        event_data_for_cadet = self.event_data_for_cadet(cadet)

        return event_data_for_cadet.days_and_club_dinghies.most_common()

    def get_most_common_group_name_across_days(self, cadet: Cadet) -> Group:
        event_data_for_cadet = self.event_data_for_cadet(cadet)
        return event_data_for_cadet.days_and_groups.most_common()

    def update_availability_of_existing_cadet_at_event_and_return_messages(
        self,
        cadet: Cadet,
        new_availabilty: DaySelector,
    ) -> List[str]:

        self.dict_of_cadets_with_registration_data.update_availability_of_existing_cadet_at_event(
            cadet=cadet, new_availabilty=new_availabilty
        )

        messages = []
        for day in self.event.days_in_event():
            if new_availabilty.available_on_day(day):
                continue

            message_for_day = (
                self.remove_availability_of_existing_cadet_on_day_and_return_messages(
                    cadet=cadet, day=day
                )
            )
            messages += message_for_day

        return messages

    def remove_availability_of_existing_cadet_on_day_and_return_messages(
        self, cadet: Cadet, day: Day
    ) -> List[str]:
        pass

        self.dict_of_cadets_and_club_dinghies_at_event.remove_cadet_club_boat_allocation_on_day(
            cadet=cadet, day=day
        )

        self.dict_of_cadets_with_days_and_groups.remove_cadet_from_event_on_day(
            cadet=cadet, day=day
        )

        message = self.dict_of_cadets_and_boat_class_and_partners.remove_cadet_from_event_on_day_and_return_message(
            cadet=cadet, day=day
        )

        return [message]

    def update_status_of_existing_cadet_in_event_info_to_cancelled_or_deleted_and_return_messages(
        self, cadet: Cadet, new_status: RegistrationStatus
    ) -> List[str]:

        assert new_status.is_cancelled_or_deleted

        self.dict_of_cadets_with_registration_data.update_status_of_existing_cadet_in_event_info_to_cancelled_or_deleted(
            cadet=cadet, new_status=new_status
        )

        self.dict_of_cadets_and_club_dinghies_at_event.remove_cadet_from_event(
            cadet=cadet
        )

        self.dict_of_cadets_with_days_and_groups.remove_cadet_from_event(cadet=cadet)

        self.dict_of_cadets_with_clothing_at_event.remove_clothing_for_cadet_at_event(
            cadet=cadet
        )

        self.dict_of_cadets_with_food_required_at_event.remove_food_requirements_for_cadet_at_event(
            cadet=cadet
        )

        messages = self.dict_of_cadets_and_boat_class_and_partners.remove_cadet_from_event_and_return_messages(
            cadet=cadet
        )

        return messages

    def event_data_for_cadet(self, cadet: Cadet):
        try:
            return self.get(cadet)
        except:
            raise MissingData

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
    def dict_of_cadets_with_clothing_at_event(self) -> DictOfCadetsWithClothingAtEvent:
        return self._dict_of_cadets_with_clothing_at_event

    @property
    def dict_of_cadets_with_food_required_at_event(
        self,
    ) -> DictOfCadetsWithFoodRequirementsAtEvent:
        return self._dict_of_cadets_with_food_required_at_event

    @property
    def event(self):
        return self._event

    @property
    def list_of_cadets(self) -> ListOfCadets:
        return ListOfCadets(list(self.keys()))


def compose_dict_of_all_event_info_for_cadet(
    event_id: str,
    list_of_events: ListOfEvents,
    dict_of_cadets_and_boat_class_and_partners: DictOfCadetsAndBoatClassAndPartners,
    dict_of_cadets_and_club_dinghies_at_event: DictOfCadetsAndClubDinghiesAtEvent,
    dict_of_cadets_with_registration_data: DictOfCadetsWithRegistrationData,
    dict_of_cadets_with_days_and_groups: DictOfCadetsWithDaysAndGroupsAtEvent,
    dict_of_cadets_with_clothing_at_event: DictOfCadetsWithClothingAtEvent,
    dict_of_cadets_with_food_required_at_event: DictOfCadetsWithFoodRequirementsAtEvent,
    active_only: bool,
) -> DictOfAllEventInfoForCadets:
    event = list_of_events.object_with_id(event_id)
    raw_dict = compose_raw_dict_of_all_event_info_for_cadet(
        dict_of_cadets_with_registration_data=dict_of_cadets_with_registration_data,
        dict_of_cadets_and_club_dinghies_at_event=dict_of_cadets_and_club_dinghies_at_event,
        dict_of_cadets_with_days_and_groups=dict_of_cadets_with_days_and_groups,
        dict_of_cadets_and_boat_class_and_partners=dict_of_cadets_and_boat_class_and_partners,
        dict_of_cadets_with_food_required_at_event=dict_of_cadets_with_food_required_at_event,
        dict_of_cadets_with_clothing_at_event=dict_of_cadets_with_clothing_at_event,
        active_only=active_only,
    )
    return DictOfAllEventInfoForCadets(
        raw_dict=raw_dict,
        dict_of_cadets_with_registration_data=dict_of_cadets_with_registration_data,
        dict_of_cadets_and_club_dinghies_at_event=dict_of_cadets_and_club_dinghies_at_event,
        dict_of_cadets_with_days_and_groups=dict_of_cadets_with_days_and_groups,
        dict_of_cadets_and_boat_class_and_partners=dict_of_cadets_and_boat_class_and_partners,
        dict_of_cadets_with_clothing_at_event=dict_of_cadets_with_clothing_at_event,
        dict_of_cadets_with_food_required_at_event=dict_of_cadets_with_food_required_at_event,
        event=event,
    )


def compose_raw_dict_of_all_event_info_for_cadet(
    dict_of_cadets_and_boat_class_and_partners: DictOfCadetsAndBoatClassAndPartners,
    dict_of_cadets_and_club_dinghies_at_event: DictOfCadetsAndClubDinghiesAtEvent,
    dict_of_cadets_with_registration_data: DictOfCadetsWithRegistrationData,
    dict_of_cadets_with_days_and_groups: DictOfCadetsWithDaysAndGroupsAtEvent,
    dict_of_cadets_with_clothing_at_event: DictOfCadetsWithClothingAtEvent,
    dict_of_cadets_with_food_required_at_event: DictOfCadetsWithFoodRequirementsAtEvent,
    active_only: bool,
) -> Dict[Cadet, AllEventInfoForCadet]:
    if active_only:
        list_of_all_cadets_with_event_data = (
            dict_of_cadets_with_registration_data.list_of_active_cadets()
        )
    else:
        list_of_all_cadets_with_event_data = (
            dict_of_cadets_with_registration_data.list_of_cadets()
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
                        cadet, DictOfDaysAndClubDinghiesAtEventForCadet()
                    ),
                    food_requirements=dict_of_cadets_with_food_required_at_event.get(
                        cadet, FoodRequirements()
                    ),
                    clothing=dict_of_cadets_with_clothing_at_event.get(
                        cadet, ClothingAtEvent()
                    ),
                ),
            )
            for cadet in list_of_all_cadets_with_event_data
        ]
    )


def cadets_not_allocated_to_group_on_at_least_one_day_attending(
    dict_of_cadets_with_registration_data: DictOfCadetsWithRegistrationData,
    dict_of_cadets_with_days_and_groups: DictOfCadetsWithDaysAndGroupsAtEvent,
) -> ListOfCadets:

    list_of_cadets = []
    for cadet in dict_of_cadets_with_registration_data.list_of_cadets():
        if cadet_is_not_allocated_to_group_on_at_least_one_day_attending(
            cadet=cadet,
            dict_of_cadets_with_registration_data=dict_of_cadets_with_registration_data,
            dict_of_cadets_with_days_and_groups=dict_of_cadets_with_days_and_groups,
        ):
            list_of_cadets.append(cadet)

    return ListOfCadets(list_of_cadets)


def cadet_is_not_allocated_to_group_on_at_least_one_day_attending(
    cadet: Cadet,
    dict_of_cadets_with_registration_data: DictOfCadetsWithRegistrationData,
    dict_of_cadets_with_days_and_groups: DictOfCadetsWithDaysAndGroupsAtEvent,
) -> bool:

    availability = dict_of_cadets_with_registration_data.registration_data_for_cadet(
        cadet
    ).availability
    days_when_cadet_is_available = availability.days_available()
    for day in days_when_cadet_is_available:
        days_and_groups = (
            dict_of_cadets_with_days_and_groups.get_days_and_groups_for_cadet(cadet)
        )
        group_on_day = days_and_groups.group_on_day(day)
        if group_on_day is unallocated_group:
            return True

    return False
