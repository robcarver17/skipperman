from app.objects.clothing import *

from app.backend.data.clothing import ClothingData
from app.objects.events import Event

from app.objects.abstract_objects.abstract_interface import abstractInterface


def is_cadet_with_id_already_at_event_with_clothing(interface: abstractInterface, event: Event, cadet_id: str)-> bool:
    clothing_data = ClothingData(interface.data)
    cadets_with_clothing = clothing_data.get_list_of_cadets_with_clothing_at_event(event)

    return cadet_id in cadets_with_clothing.list_of_cadet_ids()



def add_new_cadet_with_clothing_to_event(
        interface: abstractInterface,
        event: Event,
        cadet_id: str,
        size: str,
        colour: str = UNALLOCATED_COLOUR
    ):
    clothing_data = ClothingData(interface.data)
    clothing_data.add_new_cadet_with_clothing_to_event(event=event, cadet_id=cadet_id,
                                                       size=size,
                                                       colour=colour)

