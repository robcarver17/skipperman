from datetime import datetime
from typing import List

from app.objects.events import Event

from app.objects.constants import arg_not_passed, missing_data

from app.data_access.storage_layer.api import DataLayer
from app.objects.cadets import Cadet, ListOfCadets
from app.objects.committee import CadetCommitteeMember, ListOfCadetsOnCommittee
from app.objects.clothing import ListOfCadetsWithClothingAtEvent


class ClothingData():
    def __init__(self, data_api: DataLayer):
        self.data_api = data_api


    def add_new_cadet_with_clothing_to_event(
            self,
            event: Event,
            cadet_id: str,
            size: str,
            colour: str
    ):
        list_of_clothing =self.get_list_of_cadets_with_clothing_at_event(event)
        list_of_clothing.add_new_cadet_with_clothing_size_and_optionally_colour(
            cadet_id=cadet_id,
            size=size,
            colour=colour
        )
        self.save_list_of_cadets_with_clothing_at_event(event=event, list_of_cadets_with_clothing=list_of_clothing)


    def get_list_of_cadets_with_clothing_at_event(self, event: Event) -> ListOfCadetsWithClothingAtEvent:
        return self.data_api.get_list_of_cadets_with_clothing_at_event(event)

    def save_list_of_cadets_with_clothing_at_event(self, event: Event, list_of_cadets_with_clothing: ListOfCadetsWithClothingAtEvent):
        self.data_api.save_list_of_cadets_with_clothing_at_event(event=event, list_of_cadets_with_clothing=list_of_cadets_with_clothing)
