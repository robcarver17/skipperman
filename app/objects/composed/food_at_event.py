from dataclasses import dataclass
from typing import Dict, List

from app.objects.exceptions import MissingData

from app.objects.food import (
    ListOfCadetsWithFoodRequirementsAtEvent,
    FoodRequirements,
    ListOfVolunteersWithFoodRequirementsAtEvent,
)
from app.objects.cadets import ListOfCadets, Cadet
from app.objects.volunteers import ListOfVolunteers, Volunteer


class DictOfCadetsWithFoodRequirementsAtEvent(Dict[Cadet, FoodRequirements]):
    def __init__(
        self,
        raw_dict: Dict[Cadet, FoodRequirements],
        list_of_cadets_with_ids_and_food_requirements: ListOfCadetsWithFoodRequirementsAtEvent,
    ):
        super().__init__(raw_dict)
        self._list_of_cadets_with_ids_and_food_requirements = (
            list_of_cadets_with_ids_and_food_requirements
        )

    def add_new_cadet_with_food_to_event(
        self,
        cadet: Cadet,
        food_requirements: FoodRequirements,
    ):
        self[cadet] = food_requirements
        self.list_of_cadets_with_ids_and_food_requirements.add_new_cadet_with_food_to_event(
            cadet_id=cadet.id, food_requirements=food_requirements
        )

    def remove_food_requirements_for_cadet_at_event(self, cadet: Cadet):

        try:
            self.pop(cadet)
            self.list_of_cadets_with_ids_and_food_requirements.remove_food_requirements_for_cadet_at_event(
                cadet_id=cadet.id
            )
        except:
            pass

    def subset_matches_food_required_description(
        self, specific_food_requirements: FoodRequirements
    ):
        raw_dict = dict(
            [
                (cadet, food_requirements)
                for cadet, food_requirements in self
                if food_requirements == specific_food_requirements
            ]
        )
        subset_list_of_cadets_and_food_requirements = self.list_of_cadets_with_ids_and_food_requirements.subset_matches_food_required_description(
            specific_food_requirements
        )
        return DictOfCadetsWithFoodRequirementsAtEvent(
            raw_dict=raw_dict,
            list_of_cadets_with_ids_and_food_requirements=subset_list_of_cadets_and_food_requirements,
        )

    def unique_list_of_food_requirements(self) -> List[FoodRequirements]:
        return list(set(self.values()))

    def update_cadet_food_data(
        self,
        cadet: Cadet,
        new_food_requirements: FoodRequirements,
    ):
        self[cadet] = new_food_requirements
        self.list_of_cadets_with_ids_and_food_requirements.change_food_requirements_for_cadet(
            cadet_id=cadet.id, food_requirements=new_food_requirements
        )

    def filter_for_list_of_cadets(self, list_of_cadets: ListOfCadets):
        raw_dict = dict(
            [(cadet, self.food_for_cadet(cadet)) for cadet in list_of_cadets]
        )
        return self._create_with_new_raw_dict(raw_dict)

    def _create_with_new_raw_dict(self, raw_dict: Dict[Cadet, FoodRequirements]):
        filtered_list_of_cadet_ids = ListOfCadets(list(raw_dict.keys())).list_of_ids
        return DictOfCadetsWithFoodRequirementsAtEvent(
            raw_dict=raw_dict,
            list_of_cadets_with_ids_and_food_requirements=self.list_of_cadets_with_ids_and_food_requirements.filter_for_list_of_cadet_ids(
                filtered_list_of_cadet_ids
            ),
        )

    @property
    def list_of_cadets_with_ids_and_food_requirements(
        self,
    ) -> ListOfCadetsWithFoodRequirementsAtEvent:
        return self._list_of_cadets_with_ids_and_food_requirements

    def list_of_cadets(self) -> ListOfCadets:
        return ListOfCadets(list(self.keys()))

    def food_for_cadet(self, cadet: Cadet) -> FoodRequirements:
        food = self.get(cadet, None)
        if food is None:
            raise MissingData

        return food


def compose_dict_of_cadets_with_food_requirements_at_event(
    list_of_cadets: ListOfCadets,
    list_of_cadets_with_ids_and_food_requirements: ListOfCadetsWithFoodRequirementsAtEvent,
) -> DictOfCadetsWithFoodRequirementsAtEvent:

    raw_dict = dict(
        [
            (
                list_of_cadets.cadet_with_id(cadet_with_id_and_food.cadet_id),
                cadet_with_id_and_food.food_requirements,
            )
            for cadet_with_id_and_food in list_of_cadets_with_ids_and_food_requirements
        ]
    )

    return DictOfCadetsWithFoodRequirementsAtEvent(
        raw_dict=raw_dict,
        list_of_cadets_with_ids_and_food_requirements=list_of_cadets_with_ids_and_food_requirements,
    )


class DictOfVolunteersWithFoodRequirementsAtEvent(Dict[Volunteer, FoodRequirements]):
    def __init__(
        self,
        raw_dict: Dict[Volunteer, FoodRequirements],
        list_of_volunteers_with_ids_and_food_requirements: ListOfVolunteersWithFoodRequirementsAtEvent,
    ):
        super().__init__(raw_dict)
        self._list_of_volunteers_with_ids_and_food_requirements = (
            list_of_volunteers_with_ids_and_food_requirements
        )

    def drop_volunteer(self, volunteer: Volunteer):
        self.pop(volunteer)
        self.list_of_volunteers_with_ids_and_food_requirements.drop_volunteer(
            volunteer_id=volunteer.id
        )

    def add_new_volunteer_with_food_to_event(
        self,
        food_requirements: FoodRequirements,
        volunteer: Volunteer,
    ):
        self[volunteer] = food_requirements
        self.list_of_volunteers_with_ids_and_food_requirements.add_new_volunteer_with_food_to_event(
            volunteer_id=volunteer.id, food_requirements=food_requirements
        )

    def subset_matches_food_required_description(
        self, specific_food_requirements: FoodRequirements
    ):
        raw_dict = dict(
            [
                (volunteer, food_requirements)
                for volunteer, food_requirements in self
                if food_requirements == specific_food_requirements
            ]
        )
        subset_list_of_volunteers_and_food_requirements = self.list_of_volunteers_with_ids_and_food_requirements.subset_matches_food_requirements(
            specific_food_requirements
        )
        return DictOfVolunteersWithFoodRequirementsAtEvent(
            raw_dict=raw_dict,
            list_of_volunteers_with_ids_and_food_requirements=subset_list_of_volunteers_and_food_requirements,
        )

    def unique_list_of_food_requirements(self) -> List[FoodRequirements]:
        return list(set(self.values()))

    def update_volunteer_food_data(
        self,
        volunteer: Volunteer,
        new_food_requirements: FoodRequirements,
    ):

        self[volunteer] = new_food_requirements
        self.list_of_volunteers_with_ids_and_food_requirements.change_food_requirements_for_volunteer(
            volunteer_id=volunteer.id, food_requirements=new_food_requirements
        )

    def filter_for_list_of_volunteers(self, list_of_volunteers: ListOfVolunteers):
        raw_dict = dict(
            [
                (volunteer, self.food_for_volunteer(volunteer))
                for volunteer in list_of_volunteers
            ]
        )
        return self._create_with_new_raw_dict(raw_dict)

    def _create_with_new_raw_dict(self, raw_dict: Dict[Volunteer, FoodRequirements]):
        filtered_list_of_volunteer_ids = ListOfVolunteers(
            list(raw_dict.keys())
        ).list_of_ids
        return DictOfVolunteersWithFoodRequirementsAtEvent(
            raw_dict=raw_dict,
            list_of_volunteers_with_ids_and_food_requirements=self.list_of_volunteers_with_ids_and_food_requirements.filter_for_list_of_volunteer_ids(
                filtered_list_of_volunteer_ids
            ),
        )

    def food_for_volunteer(
        self, volunteer: Volunteer, return_empty: bool = False
    ) -> FoodRequirements:
        try:
            return self.get(volunteer)
        except:
            if return_empty:
                return FoodRequirements()
            else:
                raise MissingData

    def list_of_volunteers(self) -> ListOfVolunteers:
        return ListOfVolunteers(list(self.keys()))

    @property
    def list_of_volunteers_with_ids_and_food_requirements(
        self,
    ) -> ListOfVolunteersWithFoodRequirementsAtEvent:
        return self._list_of_volunteers_with_ids_and_food_requirements


def compose_dict_of_volunteers_with_food_requirements_at_event(
    list_of_volunteers: ListOfVolunteers,
    list_of_volunteers_with_ids_and_food_requirements: ListOfVolunteersWithFoodRequirementsAtEvent,
) -> DictOfVolunteersWithFoodRequirementsAtEvent:

    raw_dict = dict(
        [
            (
                list_of_volunteers.volunteer_with_id(
                    volunteer_with_id_and_food.volunteer_id
                ),
                volunteer_with_id_and_food.food_requirements,
            )
            for volunteer_with_id_and_food in list_of_volunteers_with_ids_and_food_requirements
        ]
    )

    return DictOfVolunteersWithFoodRequirementsAtEvent(
        raw_dict=raw_dict,
        list_of_volunteers_with_ids_and_food_requirements=list_of_volunteers_with_ids_and_food_requirements,
    )
