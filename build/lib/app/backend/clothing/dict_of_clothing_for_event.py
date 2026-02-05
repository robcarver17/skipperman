from collections import Counter
from copy import copy
from typing import List

from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.cadets import Cadet

from app.data_access.configuration.configuration import (
    MINIMUM_COLOUR_GROUPS_TO_DISTRIBUTE,
)
from app.data_access.store.object_store import ObjectStore
from app.objects.events import Event
from app.objects.composed.clothing_at_event import (
     DictOfCadetsWithClothingAtEvent,
)
from app.objects.clothing import ClothingAtEvent, ListOfCadetsWithClothingAndIdsAtEvent


def get_dict_of_cadets_with_clothing_at_event(
    object_store: ObjectStore, event: Event
) -> DictOfCadetsWithClothingAtEvent:
    return object_store.get(
        object_store.data_api.data_list_of_cadets_with_clothing_at_event.get_dict_of_cadets_with_clothing_at_event,
        event_id=event.id
    )

def get_list_of_cadets_with_clothing_ids_at_event(
    object_store: ObjectStore, event: Event
) -> ListOfCadetsWithClothingAndIdsAtEvent:
    return object_store.get(
        object_store.data_api.data_list_of_cadets_with_clothing_at_event.read,
        event_id=event.id
    )





def change_clothing_size_for_cadet(
    interface: abstractInterface, event: Event, cadet: Cadet, size: str
):
    interface.update(
        interface.object_store.data_api.data_list_of_cadets_with_clothing_at_event.change_clothing_size_for_cadet,
        cadet_id=cadet.id,
        event_id = event.id,
        size=size
    )




def change_colour_group_for_cadet(
    interface: abstractInterface, event: Event, cadet: Cadet, colour: str
):
    interface.update(interface.object_store.data_api.data_list_of_cadets_with_clothing_at_event.change_colour_group_for_cadet,
                     cadet_id=cadet.id,
                     event_id=event.id,
                     colour=colour
                     )

def clear_colour_group_for_cadet(
        interface: abstractInterface,
    event: Event,
    cadet: Cadet,
):
    interface.update(interface.object_store.data_api.data_list_of_cadets_with_clothing_at_event.clear_colour_group_for_cadet,
                     cadet_id=cadet.id,
                     event_id=event.id)


def remove_clothing_for_cadet_at_event(
    interface: abstractInterface,
    event: Event,
    cadet: Cadet,
):
    interface.update(interface.object_store.data_api.data_list_of_cadets_with_clothing_at_event.remove_clothing_for_cadet_at_event,
                     cadet_id=cadet.id,
                     event_id=event.id)

class NotEnoughColours(Exception):
    pass


def distribute_colour_groups_at_event(interface: abstractInterface, event: Event):
    dict_of_cadets_with_clothing = get_dict_of_cadets_with_clothing_at_event(
        object_store=interface.object_store, event=event
    )
    sorted_dict_of_cadets_with_clothing = (
        dict_of_cadets_with_clothing.sort_by_dob_asc()
    )  ## oldest first
    colour_options = dict_of_cadets_with_clothing.get_colour_options()

    if len(colour_options) < MINIMUM_COLOUR_GROUPS_TO_DISTRIBUTE:
        raise NotEnoughColours(
            "Less than %d colours defined - can't distribute until we have %d more groups"
            % (
                MINIMUM_COLOUR_GROUPS_TO_DISTRIBUTE,
                MINIMUM_COLOUR_GROUPS_TO_DISTRIBUTE - len(colour_options),
            )
        )

    for cadet, clothing in sorted_dict_of_cadets_with_clothing.items():
        allocate_best_colour_group_for_cadet(
            interface=interface,
            sorted_dict_of_cadets_with_clothing=sorted_dict_of_cadets_with_clothing,
            event=event,
            cadet=cadet,
            clothing=clothing,
        )



def allocate_best_colour_group_for_cadet(
        interface: abstractInterface,
        event: Event,
    sorted_dict_of_cadets_with_clothing: DictOfCadetsWithClothingAtEvent,
    cadet: Cadet,
    clothing: ClothingAtEvent,
):
    if clothing.has_colour:
        ## skip
        return

    colour_options_to_use_this_cadet = least_popular_colours(
        sorted_dict_of_cadets_with_clothing
    )
    least_popular_of_all = colour_options_to_use_this_cadet[0]
    current_colour = copy(least_popular_of_all)

    while probably_has_family_with_colour(
        cadet=cadet,
        dict_of_cadets_with_clothing=sorted_dict_of_cadets_with_clothing,
        colour=current_colour,
    ):
        colour_options_to_use_this_cadet.remove(current_colour)
        if len(colour_options_to_use_this_cadet) == 0:
            ## all colours taken by other people with surname, use least popular of those
            current_colour = least_popular_of_all
            break

        current_colour = colour_options_to_use_this_cadet[0]  ## next least popular

    sorted_dict_of_cadets_with_clothing.change_colour_group_for_cadet(
        cadet=cadet, colour=current_colour
    )

    ## The above doesn't change to SQL just the in memory version
    change_colour_group_for_cadet(interface=interface,
                                  event=event,
                                  cadet=cadet,
                                  colour=current_colour
                                  )


def probably_has_family_with_colour(
    cadet: Cadet,
    dict_of_cadets_with_clothing:DictOfCadetsWithClothingAtEvent,
    colour: str,
) -> bool:
    dict_of_cadets_with_clothing_and_same_surname = (
        dict_of_cadets_with_clothing.filter_for_surname(cadet.surname)
    )
    colours_allocated_this_surname = (
        dict_of_cadets_with_clothing_and_same_surname.get_colour_options()
    )
    colour_in_matching_surnames = colour in colours_allocated_this_surname
    return colour_in_matching_surnames


def least_popular_colours(
    dict_of_cadets_with_clothing:DictOfCadetsWithClothingAtEvent,
) -> List[str]:
    colours = dict_of_cadets_with_clothing.colours()
    counter = Counter(colours).most_common()

    most_popular = [item for item, count in counter]

    most_popular.reverse()

    return most_popular


def is_cadet_already_at_event_with_clothing(
    object_store: ObjectStore, event: Event, cadet: Cadet
) -> bool:
    return object_store.get(object_store.data_api.data_list_of_cadets_with_clothing_at_event.does_cadet_have_clothing_record_at_event,
        event_id=event.id,
    cadet_id=cadet.id
    )

def add_new_cadet_with_clothing_to_event(
   interface: abstractInterface,
    event: Event,
    cadet: Cadet,
    size: str,
):
    interface.update(interface.object_store.data_api.data_list_of_cadets_with_clothing_at_event.add_new_cadet_with_clothing_to_event,
                     event_id=event.id,
                     cadet_id=cadet.id,
                     size=size,
                     )