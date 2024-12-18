import os

import pandas as pd

from app.data_access.configuration.configuration import CADET_COMMITTEE_SHIRT_COLOUR
from app.data_access.file_access import download_directory

from app.objects.abstract_objects.abstract_form import File

from app.backend.clothing.active_cadets_with_clothing import get_dict_of_active_cadets_with_clothing_at_event

from app.frontend.shared.events_state import get_event_from_state

from app.objects.abstract_objects.abstract_interface import abstractInterface

def export_committee_clothing(interface: abstractInterface) -> File:
    event = get_event_from_state(interface)
    dict_of_cadets_with_clothing = (
        get_dict_of_active_cadets_with_clothing_at_event(
            object_store=interface.object_store, event=event, only_committee=True
        )
    )
    new_list = []

    for cadet, clothing in dict_of_cadets_with_clothing.items():
        new_list.append(
            {
                "Name": cadet.name,
                "Shirt Colour": CADET_COMMITTEE_SHIRT_COLOUR,
                "Stitching Colour": clothing.colour,
                "Shirt size": clothing.size,
                "Left sleeve": "%s Team" % clothing.colour.title(),
                "Right sleeve": "Cadet Committee",
                "Back": cadet.first_name,
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
    dict_of_cadets_with_clothing = (
        get_dict_of_active_cadets_with_clothing_at_event(
            object_store=interface.object_store, event=event, only_committee=False
        )
    )

    sorted_dict_of_cadets_with_clothing = dict_of_cadets_with_clothing.sort_by_colour_and_firstname()
    sorted_list_of_cadets_with_clothing = sorted_dict_of_cadets_with_clothing.as_list()
    filename = temp_file_name()

    df = sorted_list_of_cadets_with_clothing.as_df_of_str()
    df.to_excel(filename, index=False)

    return File(filename)


def export_clothing_colours(interface: abstractInterface) -> File:
    event = get_event_from_state(interface)
    dict_of_cadets_with_clothing = (
        get_dict_of_active_cadets_with_clothing_at_event(
            object_store=interface.object_store, event=event, only_committee=False
        )
    )
    dict_of_cadets_with_clothing_committee = (
        get_dict_of_active_cadets_with_clothing_at_event(
            object_store=interface.object_store, event=event, only_committee=True
        )
    )
    colour_dict = {}
    for colour in dict_of_cadets_with_clothing.get_colour_options():
        dict_this_colour = dict_of_cadets_with_clothing.filter_for_colour(colour)
        dict_this_colour_committee = (
            dict_of_cadets_with_clothing_committee.filter_for_colour(colour)
        )

        dict_this_colour_committee = dict_this_colour_committee.sort_by_dob_asc()

        dict_this_colour_without_committee = dict_this_colour.remove_if_in_list_of_cadets(
            dict_this_colour_committee.list_of_cadets
        )
        dict_this_colour_without_committee = dict_this_colour_without_committee.sort_by_firstname()

        list_of_names = dict_this_colour_committee.list_of_cadets.list_of_names() + dict_this_colour_without_committee.list_of_cadets.list_of_names()

        colour_dict[colour] = pd.Series(list_of_names)

    filename = temp_file_name()
    df = pd.concat(colour_dict, axis=1)
    df.to_excel(filename, index=False)

    return File(filename)


def temp_file_name() -> str:
    return os.path.join(download_directory, "temp_clothing_file.xlsx")
