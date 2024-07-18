from collections import Counter
from copy import copy

import pandas as pd

from app.objects.abstract_objects.abstract_tables import Table, PandasDFTable

from app.data_access.configuration.configuration import (
    MINIMUM_COLOUR_GROUPS_TO_DISTRIBUTE,
)
from app.objects.cadets import Cadet
from app.objects.clothing import *

from app.OLD_backend.data.clothing import ClothingData
from app.objects.clothing import (
    ListOfCadetsWithClothingAtEvent,
    ListOfCadetObjectsWithClothingAtEvent,
    CadetObjectWithClothingAtEvent,
)
from app.objects.events import Event

from app.objects.abstract_objects.abstract_interface import abstractInterface


def is_cadet_with_id_already_at_event_with_clothing(
    interface: abstractInterface, event: Event, cadet_id: str
) -> bool:
    clothing_data = ClothingData(interface.data)
    cadets_with_clothing = clothing_data.get_list_of_cadets_with_clothing_at_event(
        event
    )

    return cadet_id in cadets_with_clothing.list_of_cadet_ids()


def add_new_cadet_with_clothing_to_event(
    interface: abstractInterface,
    event: Event,
    cadet_id: str,
    size: str,
    colour: str = UNALLOCATED_COLOUR,
):
    clothing_data = ClothingData(interface.data)
    clothing_data.add_new_cadet_with_clothing_to_event(
        event=event, cadet_id=cadet_id, size=size, colour=colour
    )


def get_list_of_active_cadet_objects_with_clothing_at_event(
    interface: abstractInterface, event: Event, only_committee: bool = False
) -> ListOfCadetObjectsWithClothingAtEvent:
    clothing_data = ClothingData(interface.data)

    return clothing_data.get_list_of_active_cadet_objects_with_clothing_at_event(
        event, only_committee=only_committee
    )


def get_list_of_active_cadet_ids_with_clothing_at_event(
    interface: abstractInterface, event: Event, only_committee: bool = False
) -> ListOfCadetsWithClothingAtEvent:
    clothing_data = ClothingData(interface.data)

    return clothing_data.get_list_of_active_cadets_with_clothing_at_event(
        event, only_committee=only_committee
    )


def change_clothing_size_for_cadet(
    interface: abstractInterface, event: Event, cadet_id: str, size: str
):
    clothing_data = ClothingData(interface.data)
    clothing_data.change_clothing_size_for_cadet(
        event=event, cadet_id=cadet_id, size=size
    )


def change_colour_group_for_cadet(
    interface: abstractInterface, event: Event, cadet_id: str, colour: str
):
    clothing_data = ClothingData(interface.data)
    clothing_data.change_colour_group_for_cadet(
        event=event, cadet_id=cadet_id, colour=colour
    )


def clear_colour_group_for_cadet(
    interface: abstractInterface,
    event: Event,
    cadet_id: str,
):
    clothing_data = ClothingData(interface.data)
    clothing_data.clear_colour_group_for_cadet(event=event, cadet_id=cadet_id)


def distribute_colour_groups_at_event(interface: abstractInterface, event: Event):
    list_of_cadets_with_clothing = (
        get_list_of_active_cadet_objects_with_clothing_at_event(
            interface=interface, event=event, only_committee=False
        )
    )
    sorted_list_of_cadets_with_clothing = (
        list_of_cadets_with_clothing.sort_by_dob_asc()
    )  ## oldest first
    colour_options = list_of_cadets_with_clothing.get_colour_options()

    if len(colour_options) < MINIMUM_COLOUR_GROUPS_TO_DISTRIBUTE:
        interface.log_error(
            "Less than %d colours defined - can't distribute until we have %d more groups"
            % (
                MINIMUM_COLOUR_GROUPS_TO_DISTRIBUTE,
                MINIMUM_COLOUR_GROUPS_TO_DISTRIBUTE - len(colour_options),
            )
        )
        return

    for cadet_with_clothing in sorted_list_of_cadets_with_clothing:
        allocate_best_colour_group_for_cadet(
            sorted_list_of_cadets_with_clothing=sorted_list_of_cadets_with_clothing,
            cadet_with_clothing=cadet_with_clothing,
        )

    save_list_of_cadets_with_clothing_with_changed_colours(
        interface=interface,
        event=event,
        sorted_list_of_cadets_with_clothing=sorted_list_of_cadets_with_clothing,
    )


def allocate_best_colour_group_for_cadet(
    sorted_list_of_cadets_with_clothing: ListOfCadetObjectsWithClothingAtEvent,
    cadet_with_clothing: CadetObjectWithClothingAtEvent,
):
    if cadet_with_clothing.has_colour:
        ## skip
        return

    colour_options_to_use_this_cadet = least_popular_colours(
        sorted_list_of_cadets_with_clothing
    )
    least_popular_of_all = colour_options_to_use_this_cadet[0]
    current_colour = copy(least_popular_of_all)

    while probably_has_family_with_colour(
        cadet=cadet_with_clothing.cadet,
        list_of_cadets_with_clothing=sorted_list_of_cadets_with_clothing,
        colour=current_colour,
    ):
        colour_options_to_use_this_cadet.remove(current_colour)
        if len(colour_options_to_use_this_cadet) == 0:
            ## all colours taken by other people with surname, use least popular of those
            current_colour = least_popular_of_all
            break

        current_colour = colour_options_to_use_this_cadet[0]  ## next least popular

    cadet_with_clothing.colour = (
        current_colour  ## changes in place so will need saving as a block
    )


def save_list_of_cadets_with_clothing_with_changed_colours(
    interface: abstractInterface,
    event: Event,
    sorted_list_of_cadets_with_clothing: ListOfCadetObjectsWithClothingAtEvent,
):
    for cadet_with_clothing in sorted_list_of_cadets_with_clothing:
        change_colour_group_for_cadet(
            interface=interface,
            event=event,
            cadet_id=cadet_with_clothing.cadet.id,
            colour=cadet_with_clothing.colour,
        )


def probably_has_family_with_colour(
    cadet: Cadet,
    list_of_cadets_with_clothing: ListOfCadetObjectsWithClothingAtEvent,
    colour: str,
) -> bool:
    list_of_cadets_with_clothing_and_same_surname = (
        list_of_cadets_with_clothing.filter_for_surname(cadet.surname)
    )
    return colour in list_of_cadets_with_clothing_and_same_surname.get_colour_options()


def least_popular_colours(
    list_of_cadets_with_clothing: ListOfCadetObjectsWithClothingAtEvent,
):
    colours = list_of_cadets_with_clothing.colours()
    counter = Counter(colours).most_common()

    most_popular = [item for item, count in counter]

    most_popular.reverse()

    return most_popular


def summarise_clothing(interface: abstractInterface, event: Event) -> PandasDFTable:
    list_of_cadets_with_clothing = (
        get_list_of_active_cadet_objects_with_clothing_at_event(
            interface=interface, event=event, only_committee=False
        )
    )

    sizes = list_of_cadets_with_clothing.get_clothing_size_options()
    colours = list_of_cadets_with_clothing.get_colour_options()

    all_clothing = {}
    for size in sizes:
        clothing_for_size = {}
        for colour in colours:
            clothing_for_size[
                colour
            ] = list_of_cadets_with_clothing.count_of_size_and_colour(
                size=size, colour=colour
            )

        all_clothing[size] = clothing_for_size

    df = pd.DataFrame(all_clothing)
    df.loc["Total"] = df.sum(numeric_only=True, axis=0)
    df.loc[:, "Total"] = df.sum(numeric_only=True, axis=1)

    return PandasDFTable(df)
