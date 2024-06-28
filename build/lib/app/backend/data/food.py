from typing import List

from app.objects.volunteers_at_event import ListOfVolunteersAtEventWithId

from app.objects.events import Event


from app.data_access.storage_layer.api import DataLayer
from app.objects.cadets import ListOfCadets
from app.objects.food import (
    ListOfCadetsWithFoodRequirementsAtEvent,
    FoodRequirements,
    ListOfVolunteersWithFoodRequirementsAtEvent,
)
from app.backend.data.cadets_at_event_id_level import CadetsAtEventIdLevelData
from app.backend.data.volunteer_allocation import VolunteerAllocationData


class FoodData:
    def __init__(self, data_api: DataLayer):
        self.data_api = data_api

    def change_food_requirements_for_cadet(
        self, event: Event, cadet_id: str, food_requirements: FoodRequirements
    ):
        list_of_requirements = self.get_list_of_cadets_with_food_at_event(event)
        list_of_requirements.change_food_requirements_for_cadet(
            cadet_id=cadet_id, food_requirements=food_requirements
        )
        self.save_list_of_cadets_with_food_at_event(
            event=event, list_of_cadets_with_food_requirements=list_of_requirements
        )

    def change_food_requirements_for_volunteer(
        self, event: Event, volunteer_id: str, food_requirements: FoodRequirements
    ):
        list_of_requirements = self.get_list_of_volunteeers_with_food_at_event(event)
        list_of_requirements.change_food_requirements_for_volunteer(
            volunteer_id=volunteer_id, food_requirements=food_requirements
        )
        self.save_list_of_volunteers_with_food_at_event(
            event=event, list_of_volunteers_with_food_requirements=list_of_requirements
        )

    def add_new_volunteer_with_food_to_event(
        self, event: Event, food_requirements: FoodRequirements, volunteer_id: str
    ):
        list_of_requirements = self.get_list_of_volunteeers_with_food_at_event(event)
        list_of_requirements.add_new_volunteer_with_food_to_event(
            volunteer_id=volunteer_id, food_requirements=food_requirements
        )
        self.save_list_of_volunteers_with_food_at_event(
            event=event, list_of_volunteers_with_food_requirements=list_of_requirements
        )

    def add_new_cadet_with_food_to_event(
        self, event: Event, food_requirements: FoodRequirements, cadet_id: str
    ):
        list_of_requirements = self.get_list_of_cadets_with_food_at_event(event)
        list_of_requirements.add_new_cadet_with_food_to_event(
            cadet_id=cadet_id, food_requirements=food_requirements
        )
        self.save_list_of_cadets_with_food_at_event(
            event=event, list_of_cadets_with_food_requirements=list_of_requirements
        )

    def get_combined_list_of_food_requirement_items(self, event: Event) -> List[str]:
        list_of_requirements_for_cadets = self.get_list_of_cadets_with_food_at_event(
            event
        ).unique_list_of_food_requirements()
        list_of_requirements_for_volunteers = (
            self.get_list_of_volunteeers_with_food_at_event(
                event
            ).unique_list_of_food_requirements()
        )

        return list(
            set(list_of_requirements_for_volunteers + list_of_requirements_for_cadets)
        )

    def list_of_active_cadets_with_food_at_event(
        self, event: Event
    ) -> ListOfCadetsWithFoodRequirementsAtEvent:
        list_of_requirements = self.get_list_of_cadets_with_food_at_event(event)
        list_of_active_cadets = self.list_of_active_cadets_at_event(event)
        list_of_active_cadet_ids = list_of_active_cadets.list_of_ids

        return list_of_requirements.filter_for_list_of_cadet_ids(
            list_of_active_cadet_ids
        )

    def list_of_active_volunteers_with_food_at_event(
        self, event: Event
    ) -> ListOfVolunteersWithFoodRequirementsAtEvent:
        list_of_requirements = self.get_list_of_volunteeers_with_food_at_event(event)
        list_of_volunteers = self.list_of_active_volunteers_at_event(event)
        list_of_volunteer_ids = list_of_volunteers.list_of_volunteer_ids

        return list_of_requirements.filter_for_list_of_volunteer_ids(
            list_of_volunteer_ids
        )

    def list_of_active_cadets_at_event(self, event: Event) -> ListOfCadets:
        return self.cadets_at_event_data.list_of_active_cadets_at_event(event)

    def list_of_active_volunteers_at_event(
        self, event: Event
    ) -> ListOfVolunteersAtEventWithId:
        return self.volunteer_allocation_data.load_list_of_volunteers_with_ids_at_event(
            event
        )

    def get_list_of_volunteeers_with_food_at_event(
        self, event: Event
    ) -> ListOfVolunteersWithFoodRequirementsAtEvent:
        return self.data_api.get_list_of_volunteers_with_food_at_event(event)

    def save_list_of_volunteers_with_food_at_event(
        self,
        event: Event,
        list_of_volunteers_with_food_requirements: ListOfVolunteersWithFoodRequirementsAtEvent,
    ):
        self.data_api.save_list_of_volunteers_with_food_at_event(
            event=event,
            list_of_volunteers_with_food=list_of_volunteers_with_food_requirements,
        )

    def get_list_of_cadets_with_food_at_event(
        self, event: Event
    ) -> ListOfCadetsWithFoodRequirementsAtEvent:
        return self.data_api.get_list_of_cadets_with_food_at_event(event)

    def save_list_of_cadets_with_food_at_event(
        self,
        event: Event,
        list_of_cadets_with_food_requirements: ListOfCadetsWithFoodRequirementsAtEvent,
    ):
        self.data_api.save_list_of_cadets_with_food_at_event(
            list_of_cadets_with_food=list_of_cadets_with_food_requirements, event=event
        )

    @property
    def cadets_at_event_data(self) -> CadetsAtEventIdLevelData:
        return CadetsAtEventIdLevelData(self.data_api)

    @property
    def volunteer_allocation_data(self) -> VolunteerAllocationData:
        return VolunteerAllocationData(self.data_api)
