from app.OLD_backend.data.cadet_committee import CadetCommitteeData

from app.objects.committee import ListOfCadetsWithIdOnCommittee

from app.objects.events import Event

from app.data_access.store.data_access import DataLayer
from app.objects.cadets import ListOfCadets
from app.objects.clothing import (
    ListOfCadetsWithClothingAndIdsAtEvent,
)
from app.objects.composed.clothing_at_event import ListOfCadetsWithClothingAtEvent
from app.OLD_backend.data.cadets_at_event_id_level import CadetsAtEventIdLevelData
from app.OLD_backend.data.cadets import CadetData


class ClothingData:
    def __init__(self, data_api: DataLayer):
        self.data_api = data_api

    def change_clothing_size_for_cadet(self, event: Event, cadet_id: str, size: str):
        list_of_clothing = self.get_list_of_cadets_with_clothing_at_event(event)
        list_of_clothing.change_clothing_size_for_cadet(cadet_id=cadet_id, size=size)
        self.save_list_of_cadets_with_clothing_at_event(
            event=event, list_of_cadets_with_clothing=list_of_clothing
        )

    def change_colour_group_for_cadet(self, event: Event, cadet_id: str, colour: str):
        list_of_clothing = self.get_list_of_cadets_with_clothing_at_event(event)
        list_of_clothing.change_colour_group_for_cadet(cadet_id=cadet_id, colour=colour)
        self.save_list_of_cadets_with_clothing_at_event(
            event=event, list_of_cadets_with_clothing=list_of_clothing
        )

    def clear_colour_group_for_cadet(
        self,
        event: Event,
        cadet_id: str,
    ):
        list_of_clothing = self.get_list_of_cadets_with_clothing_at_event(event)
        list_of_clothing.clear_colour_group_for_cadet(cadet_id=cadet_id)
        self.save_list_of_cadets_with_clothing_at_event(
            event=event, list_of_cadets_with_clothing=list_of_clothing
        )

    def add_new_cadet_with_clothing_to_event(
        self, event: Event, cadet_id: str, size: str, colour: str
    ):
        list_of_clothing = self.get_list_of_cadets_with_clothing_at_event(event)
        list_of_clothing.add_new_cadet_with_clothing_size_and_optionally_colour(
            cadet_id=cadet_id, size=size, colour=colour
        )
        self.save_list_of_cadets_with_clothing_at_event(
            event=event, list_of_cadets_with_clothing=list_of_clothing
        )

    def get_list_of_active_cadet_objects_with_clothing_at_event(
        self, event: Event, only_committee: bool = False
    ) -> ListOfCadetsWithClothingAtEvent:
        active_cadets_with_clothing = (
            self.get_list_of_active_cadets_with_clothing_at_event(
                event=event, only_committee=only_committee
            )
        )
        all_cadets = self.list_of_all_cadets()

        return ListOfCadetsWithClothingAtEvent.from_list_of_cadets(
            list_of_cadets=all_cadets,
            list_of_cadets_with_clothing=active_cadets_with_clothing,
        )

    def get_list_of_active_cadets_with_clothing_at_event(
        self, event: Event, only_committee: bool = False
    ) -> ListOfCadetsWithClothingAndIdsAtEvent:
        cadets_with_clothing = self.get_list_of_cadets_with_clothing_at_event(event)
        active_cadets = self.active_cadets_at_event(event)
        if only_committee:
            committee = self.list_of_current_cadet_committee()
            committee_ids = committee.list_of_cadet_ids()
            cadets_with_clothing = cadets_with_clothing.filter_for_list_of_cadet_ids(
                committee_ids
            )

        active_cadets_with_clothing = cadets_with_clothing.filter_for_list_of_cadet_ids(
            active_cadets.list_of_ids
        )

        return active_cadets_with_clothing

    def active_cadets_at_event(self, event: Event) -> ListOfCadets:
        return self.cadets_at_event_data.list_of_active_cadets_at_event(event)

    def list_of_all_cadets(self) -> ListOfCadets:
        return self.cadet_data.get_list_of_cadets()

    def list_of_current_cadet_committee(self) -> ListOfCadetsWithIdOnCommittee:
        return self.committee_data.get_list_of_current_cadets_on_committee()

    def get_list_of_cadets_with_clothing_at_event(
        self, event: Event
    ) -> ListOfCadetsWithClothingAndIdsAtEvent:
        return self.data_api.get_list_of_cadets_with_clothing_at_event(event)

    def save_list_of_cadets_with_clothing_at_event(
        self,
        event: Event,
        list_of_cadets_with_clothing: ListOfCadetsWithClothingAndIdsAtEvent,
    ):
        self.data_api.save_list_of_cadets_with_clothing_at_event(
            event=event, list_of_cadets_with_clothing=list_of_cadets_with_clothing
        )

    @property
    def cadets_at_event_data(self) -> CadetsAtEventIdLevelData:
        return CadetsAtEventIdLevelData(self.data_api)

    @property
    def cadet_data(self) -> CadetData:
        return CadetData(self.data_api)

    @property
    def committee_data(self) -> CadetCommitteeData:
        return CadetCommitteeData(self.data_api)
