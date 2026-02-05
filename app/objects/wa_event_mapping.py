from dataclasses import dataclass

from app.objects.utilities.exceptions import arg_not_passed, missing_data
from app.objects.utilities.generic_list_of_objects import (
    GenericListOfObjects,
    get_unique_object_with_attr_in_list,
    get_idx_of_unique_object_with_attr_in_list,
)
from app.objects.utilities.generic_objects import GenericSkipperManObject

NO_WA_ID = Exception
NO_EVENT_ID = Exception


@dataclass
class WAEventMap(GenericSkipperManObject):
    event_id: str
    wa_id: str


class ListOfWAEventMaps(GenericListOfObjects):
    @property
    def _object_class_contained(self):
        return WAEventMap

    def get_wa_id_for_event(self, event_id: str) -> str:
        wa_and_event_id = self.get_event_map_with_event_id(
            event_id, default=missing_data
        )
        if wa_and_event_id is missing_data:
            raise NO_EVENT_ID()

        return str(wa_and_event_id.wa_id)

    def get_event_id_for_wa(self, wa_id: str) -> str:
        wa_and_event_id = self.get_event_map_with_wa_id(wa_id, default=missing_data)
        if wa_and_event_id is missing_data:
            raise NO_WA_ID()

        return wa_and_event_id.event_id

    def get_event_map_with_event_id(
        self, event_id: str, default=arg_not_passed
    ) -> WAEventMap:
        return get_unique_object_with_attr_in_list(
            some_list=self, attr_name="event_id", attr_value=event_id, default=default
        )

    def get_event_map_with_wa_id(
        self, wa_id: str, default=arg_not_passed
    ) -> WAEventMap:
        return get_unique_object_with_attr_in_list(
            some_list=self, attr_name="wa_id", attr_value=wa_id, default=default
        )

