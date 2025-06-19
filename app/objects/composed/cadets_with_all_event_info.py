from copy import copy
from dataclasses import dataclass
from typing import Dict, List

from app.objects.composed.cadets_at_event_with_boat_classes_groups_club_dnghies_and_partners import (
    ListOfCadetBoatClassClubDinghyGroupAndPartnerAtEventOnDay,
    CadetBoatClassClubDinghyGroupAndPartnerAtEventOnDay,
)
from app.objects.composed.cadets_with_all_event_info_functions import (
    cadets_not_allocated_to_group_on_at_least_one_day_attending,
    update_boat_info_for_updated_cadet_at_event_and_return_affected_cadets,
    RequiredDictForAllocation,
)
from app.objects.day_selectors import DaySelector, Day
from app.objects.registration_data import RowInRegistrationData
from app.objects.utilities.exceptions import MissingData, arg_not_passed
from app.objects.food import no_food_requirements
from app.objects.groups import Group, unallocated_group

from app.objects.registration_status import RegistrationStatus

from app.objects.events import Event, ListOfEvents

from app.objects.cadets import Cadet, ListOfCadets

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


from app.objects.composed.clothing_at_event import (
    DictOfCadetsWithClothingAtEvent,
)
from app.objects.clothing import ClothingAtEvent, no_clothing_requirements
from app.objects.composed.food_at_event import (
    DictOfCadetsWithFoodRequirementsAtEvent,
    FoodRequirements,
)


@dataclass
class AllEventInfoForCadet:
    registration_data: CadetRegistrationData
    days_and_groups: DaysAndGroups
    days_and_club_dinghies: DictOfDaysAndClubDinghiesAtEventForPerson
    days_and_boat_class: DictOfDaysBoatClassAndPartners
    food_requirements: FoodRequirements
    clothing: ClothingAtEvent

    def is_active_registration(self):
        return self.registration_data.status.is_active

    def update_notes(self, new_notes: str):
        self.registration_data.update_notes(new_notes)


class DictOfAllEventInfoForCadets(Dict[Cadet, AllEventInfoForCadet]):
    def __init__(
        self,
        raw_dict: Dict[Cadet, AllEventInfoForCadet],
        dict_of_cadets_and_boat_class_and_partners: DictOfCadetsAndBoatClassAndPartners,
        dict_of_cadets_and_club_dinghies_at_event: DictOfPeopleAndClubDinghiesAtEvent,
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

    def delete_cadet_from_event_and_return_messages(self, cadet: Cadet) -> List[str]:

        messages = []
        messages += self.dict_of_cadets_with_days_and_groups.delete_cadet_from_event_and_return_messages(
            cadet
        )
        messages += self.dict_of_cadets_and_boat_class_and_partners.delete_cadet_from_event_and_return_messages(
            cadet
        )
        messages += self.dict_of_cadets_with_food_required_at_event.remove_food_requirements_for_cadet_at_event(
            cadet
        )
        messages += self.dict_of_cadets_with_clothing_at_event.remove_clothing_for_cadet_at_event(
            cadet
        )
        messages += (
            self.dict_of_cadets_and_club_dinghies_at_event.remove_person_from_event(
                cadet
            )
        )

        messages += self.dict_of_cadets_with_registration_data.delete_cadet_from_event_and_return_messages(
            cadet
        )  ## do last or may get errors

        if len(messages) > 0:
            messages.insert(0, "Will remove cadet from event %s" % str(self.event))

        return messages

    def update_data_row_for_existing_cadet_at_event(
        self, cadet: Cadet, column_name: str, new_value_for_column
    ):
        registration_data = self.dict_of_cadets_with_registration_data
        registration_data.update_row_in_registration_data_for_existing_cadet_at_event(
            cadet=cadet,
            column_name=column_name,
            new_value_for_column=new_value_for_column,
        )

        self.propagate_changes_to_cadet_in_underlying_data(cadet)

    def update_health_for_existing_cadet_at_event(self, cadet: Cadet, new_health: str):
        event_data = self.event_data_for_cadet(cadet)
        current_health = event_data.registration_data.health
        if current_health == new_health:
            return

        registration_data = self.dict_of_cadets_with_registration_data
        registration_data.update_health_for_existing_cadet_at_event(
            cadet=cadet, new_health=new_health
        )

        self.propagate_changes_to_cadet_in_underlying_data(cadet)

    def update_notes_for_existing_cadet_at_event(self, cadet: Cadet, notes: str):
        ## my level
        event_data = self.event_data_for_cadet(cadet)
        current_notes = event_data.registration_data.notes
        if current_notes == notes:
            return

        ## propogate down
        registration_data = self.dict_of_cadets_with_registration_data
        registration_data.update_notes_for_existing_cadet_at_event(
            cadet=cadet, notes=notes
        )

        self.propagate_changes_to_cadet_in_underlying_data(cadet)

    def update_boat_info_for_updated_cadet_at_event(
        self,
        cadet_boat_class_group_club_dinghy_and_partner_on_day: CadetBoatClassClubDinghyGroupAndPartnerAtEventOnDay,
    ):
        availability_dict = (
            self.dict_of_cadets_with_registration_data.availability_dict()
        )
        required_dict_for_allocation = RequiredDictForAllocation(
            dict_of_cadets_and_boat_class_and_partners=self.dict_of_cadets_and_boat_class_and_partners,
            dict_of_cadets_and_club_dinghies_at_event=self.dict_of_cadets_and_club_dinghies_at_event,
            dict_of_cadets_with_days_and_groups=self.dict_of_cadets_with_days_and_groups,
            availability_dict=availability_dict,
        )

        required_dict_for_allocation = update_boat_info_for_updated_cadet_at_event_and_return_affected_cadets(
            cadet_boat_class_group_club_dinghy_and_partner_on_day=cadet_boat_class_group_club_dinghy_and_partner_on_day,
            required_dict_for_allocation=required_dict_for_allocation,
        )

        self._dict_of_cadets_and_boat_class_and_partners = (
            required_dict_for_allocation.dict_of_cadets_and_boat_class_and_partners
        )
        self._dict_of_cadets_and_club_dinghies_at_event = (
            required_dict_for_allocation.dict_of_cadets_and_club_dinghies_at_event
        )
        self._dict_of_cadets_with_days_and_groups = (
            required_dict_for_allocation.dict_of_cadets_with_days_and_groups
        )

        affected_cadets = required_dict_for_allocation.affected_cadets

        self.propagate_changes_to_list_of_cadets_in_underlying_data(affected_cadets)

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

    def dict_of_cadets_with_groups_for_all_cadets_in_data(
        self,
    ) -> DictOfCadetsWithDaysAndGroupsAtEvent:
        return self.dict_of_cadets_with_days_and_groups.subset_for_list_of_cadets(
            self.list_of_cadets
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

    def get_most_common_partner_name_across_days(self, cadet: Cadet) -> Cadet:
        event_data_for_cadet = self.event_data_for_cadet(cadet)
        partner = event_data_for_cadet.days_and_boat_class.most_common_partner()

        return partner.name

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

    def update_availability_of_existing_cadet_at_event_and_return_messages(
        self,
        cadet: Cadet,
        new_availabilty: DaySelector,
    ) -> List[str]:

        existing_availablity = copy(
            self.dict_of_cadets_with_registration_data.registration_data_for_cadet(
                cadet
            ).availability
        )

        messages = []
        for day in self.event.days_in_event():
            if existing_availablity.available_on_day(
                day
            ) == new_availabilty.available_on_day(day):
                continue

            if new_availabilty.available_on_day(day):
                self.make_cadet_available_on_day(day=day, cadet=cadet)
            else:
                message_for_day = self.remove_availability_of_existing_cadet_on_day_and_return_messages(
                    cadet=cadet, day=day
                )

                messages += message_for_day

        return messages

    def make_cadet_available_on_day(self, cadet: Cadet, day: Day):
        self.dict_of_cadets_with_registration_data.make_cadet_available_on_day(
            cadet=cadet, day=day
        )
        self.propagate_changes_to_cadet_in_underlying_data(cadet)

    def remove_availability_of_existing_cadet_on_day_and_return_messages(
        self, cadet: Cadet, day: Day
    ) -> List[str]:

        self.dict_of_cadets_with_registration_data.make_cadet_unavailable_on_day(
            cadet=cadet, day=day
        )

        self.dict_of_cadets_and_club_dinghies_at_event.remove_persons_club_boat_allocation_on_day(
            person=cadet, day=day
        )

        self.dict_of_cadets_with_days_and_groups.remove_cadet_from_event_on_day(
            cadet=cadet, day=day
        )

        message = self.dict_of_cadets_and_boat_class_and_partners.remove_cadet_from_event_on_day_and_return_message(
            cadet=cadet, day=day
        )

        self.propagate_changes_to_cadet_in_underlying_data(cadet)

        return [message]

    def update_registration_data_for_existing_cadet(self, cadet: Cadet,
        row_in_registration_data: RowInRegistrationData):
        self.dict_of_cadets_with_registration_data.update_registration_data_for_existing_cadet(
            cadet=cadet,
            row_in_registration_data=row_in_registration_data
        )
        self.propagate_changes_to_cadet_in_underlying_data(cadet)

    def update_status_of_existing_cadet_at_event_when_not_cancelling_or_deleting(
        self,
        cadet: Cadet,
        new_status: RegistrationStatus,
    ):
        self.dict_of_cadets_with_registration_data.update_status_of_existing_cadet_in_event_info(
            cadet=cadet, new_status=new_status
        )
        self.propagate_changes_to_cadet_in_underlying_data(cadet)

    def update_status_of_existing_cadet_in_event_info_to_cancelled_or_deleted_and_return_messages(
        self, cadet: Cadet, new_status: RegistrationStatus
    ) -> List[str]:

        assert new_status.is_cancelled_or_deleted
        self.dict_of_cadets_with_registration_data.update_status_of_existing_cadet_in_event_info(
            cadet=cadet, new_status=new_status
        )

        self.dict_of_cadets_and_club_dinghies_at_event.remove_person_from_event(
            person=cadet
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

        self.propagate_changes_to_cadet_in_underlying_data(cadet)

        return messages

    def propagate_changes_to_list_of_cadets_in_underlying_data(
        self, list_of_cadets: ListOfCadets
    ):
        [
            self.propagate_changes_to_cadet_in_underlying_data(cadet)
            for cadet in list_of_cadets
        ]

    def propagate_changes_to_cadet_in_underlying_data(self, cadet: Cadet):
        event_data_for_cadet = AllEventInfoForCadet(
            registration_data=self.dict_of_cadets_with_registration_data[cadet],
            days_and_boat_class=self.dict_of_cadets_and_boat_class_and_partners.get(
                cadet, DictOfDaysBoatClassAndPartners()
            ),
            days_and_groups=self.dict_of_cadets_with_days_and_groups.get(
                cadet, DaysAndGroups()
            ),
            days_and_club_dinghies=self.dict_of_cadets_and_club_dinghies_at_event.get(
                cadet, DictOfDaysAndClubDinghiesAtEventForPerson()
            ),
            food_requirements=self.dict_of_cadets_with_food_required_at_event.get(
                cadet, no_food_requirements
            ),
            clothing=self.dict_of_cadets_with_clothing_at_event.get(
                cadet, no_clothing_requirements
            ),
        )
        self.update_event_data_for_cadet(cadet, event_data=event_data_for_cadet)

    def update_event_data_for_cadet(
        self, cadet: Cadet, event_data: AllEventInfoForCadet
    ):
        self[cadet] = event_data

    def event_data_for_cadet(
        self, cadet: Cadet, default=arg_not_passed
    ) -> AllEventInfoForCadet:
        all_data = self.get(cadet, default)
        if all_data is arg_not_passed:
            raise MissingData

        return all_data

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
    dict_of_cadets_and_club_dinghies_at_event: DictOfPeopleAndClubDinghiesAtEvent,
    dict_of_cadets_with_registration_data: DictOfCadetsWithRegistrationData,
    dict_of_cadets_with_days_and_groups: DictOfCadetsWithDaysAndGroupsAtEvent,
    dict_of_cadets_with_clothing_at_event: DictOfCadetsWithClothingAtEvent,
    dict_of_cadets_with_food_required_at_event: DictOfCadetsWithFoodRequirementsAtEvent,
    active_only: bool,
) -> DictOfAllEventInfoForCadets:
    event = list_of_events.event_with_id(event_id)
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
    dict_of_cadets_and_club_dinghies_at_event: DictOfPeopleAndClubDinghiesAtEvent,
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
                        cadet, DictOfDaysAndClubDinghiesAtEventForPerson()
                    ),
                    food_requirements=dict_of_cadets_with_food_required_at_event.get(
                        cadet, no_food_requirements
                    ),
                    clothing=dict_of_cadets_with_clothing_at_event.get(
                        cadet, no_clothing_requirements
                    ),
                ),
            )
            for cadet in list_of_all_cadets_with_event_data
        ]
    )
