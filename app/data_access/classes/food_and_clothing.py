from app.objects.clothing import ListOfCadetsWithClothingAtEvent
from app.objects.food import ListOfVolunteersWithFoodRequirementsAtEvent, ListOfCadetsWithFoodRequirementsAtEvent, ListOfPeopleWithFoodRequirementsAtEvent

class DataListOfCadetsWithClothingAtEvent(object):
    def read(self,event_id:str) -> ListOfCadetsWithClothingAtEvent:
        raise NotImplemented

    def write(self, list_of_cadets_with_clothing_at_event: ListOfCadetsWithClothingAtEvent, event_id: str):
        raise NotImplemented



class DataListOfVolunteersWithFoodRequirementsAtEvent(object):
    def read(self, event_id: str) -> ListOfVolunteersWithFoodRequirementsAtEvent:
        raise NotImplemented

    def write(self, list_of_volunteers_with_food_requirements_at_event: ListOfVolunteersWithFoodRequirementsAtEvent, event_id: str):
        raise NotImplemented


class DataListOfCadetsWithFoodRequirementsAtEvent(object):
    def read(self, event_id: str) -> ListOfCadetsWithFoodRequirementsAtEvent:
        raise NotImplemented

    def write(self, list_of_cadets_with_food_requirements_at_event: ListOfCadetsWithFoodRequirementsAtEvent, event_id: str):
        raise NotImplemented



class DataListOfPeopleWithFoodRequirementsAtEvent(object):
    def read(self, event_id: str) -> ListOfPeopleWithFoodRequirementsAtEvent:
        raise NotImplemented

    def write(self, list_of_people_with_food_requirements_at_event: ListOfPeopleWithFoodRequirementsAtEvent, event_id: str):
        raise NotImplemented

