import os

import pandas as pd

from app.data_access.file_access import download_directory

from app.objects.abstract_objects.abstract_form import File

from app.backend.clothing.active_cadets_with_clothing import get_dict_of_active_cadets_with_clothing_at_event

from app.frontend.shared.events_state import get_event_from_state

from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.composed.clothing_at_event import ListOfCadetsWithClothingAtEvent


def export_committee_clothing(interface: abstractInterface) -> File:
    event = get_event_from_state(interface)
    list_of_cadets_with_clothing = (
        get_dict_of_active_cadets_with_clothing_at_event(
            interface=interface, event=event, only_committee=True
        )
    )
    new_list = []

    for cadet_with_clothing in list_of_cadets_with_clothing:
        new_list.append(
            {
                "Name": cadet_with_clothing.cadet.name,
                "Shirt Colour": "Navy Blue",
                "Stitching Colour": cadet_with_clothing.colour,
                "Shirt size": cadet_with_clothing.size,
                "Left sleeve": "%s Team" % cadet_with_clothing.colour.title(),
                "Right sleeve": "Cadet Committee",
                "Back": cadet_with_clothing.cadet.first_name,
            }
        )
    new_list.append(
        {
            "Name": "Notes:-",
            "Shirt Colour": "",
            "Stitching Colour": "",
            "Shirt size": "",
            "Left sleeve": "Where required use:",
            "Right sleeve": "Cadet Commodore / Cadet Vice-Commodore / Cadet Secretary",
            "Back": "Check nicknames with cadets",
        }
    )

    df = pd.DataFrame(new_list)
    filename = temp_file_name()
    df.to_excel(filename, index=False)

    return File(filename)


def export_all_clothing(interface: abstractInterface) -> File:
    event = get_event_from_state(interface)
    list_of_cadets_with_clothing = (
        get_dict_of_active_cadets_with_clothing_at_event(
            interface=interface, event=event, only_committee=False
        )
    )
    new_list = []
    for colour in list_of_cadets_with_clothing.get_colour_options():
        list_this_colour = list_of_cadets_with_clothing.filter_for_colour(colour)
        list_this_colour = list_this_colour.sort_by_firstname()
        new_list += list_this_colour

    list_of_cadets_with_clothing = ListOfCadetsWithClothingAtEvent(new_list)

    filename = temp_file_name()
    df = list_of_cadets_with_clothing.as_df_of_str()
    df.to_excel(filename, index=False)

    return File(filename)


def export_clothing_colours(interface: abstractInterface) -> File:
    event = get_event_from_state(interface)
    list_of_cadets_with_clothing = (
        get_dict_of_active_cadets_with_clothing_at_event(
            interface=interface, event=event, only_committee=False
        )
    )
    list_of_cadets_with_clothing_committee = (
        get_dict_of_active_cadets_with_clothing_at_event(
            interface=interface, event=event, only_committee=True
        )
    )
    colour_dict = {}
    for colour in list_of_cadets_with_clothing.get_colour_options():
        list_this_colour = list_of_cadets_with_clothing.filter_for_colour(colour)
        list_this_colour_committee = (
            list_of_cadets_with_clothing_committee.filter_for_colour(colour)
        )

        list_this_colour_committee = list_this_colour_committee.sort_by_dob_asc()

        list_this_colour = list_this_colour.remove_if_in_list_of_cadets(
            list_this_colour_committee.list_of_cadet_ids()
        )
        list_this_colour = list_this_colour.sort_by_firstname()

        list_of_cadets_with_clothing_this_colour = (
            list_this_colour_committee + list_this_colour
        )
        list_of_names = [
            object.cadet.name for object in list_of_cadets_with_clothing_this_colour
        ]

        colour_dict[colour] = pd.Series(list_of_names)

    filename = temp_file_name()
    df = pd.concat(colour_dict, axis=1)
    df.to_excel(filename, index=False)

    return File(filename)


def temp_file_name() -> str:
    return os.path.join(download_directory, "temp_clothing_file.xlsx")
