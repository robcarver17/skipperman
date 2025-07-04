from typing import List

from app.objects.cadets import Cadet

from app.objects.abstract_objects.abstract_form import listInput

from app.objects.composed.clothing_at_event import (
    SORT_BY_FIRSTNAME,
    all_sort_types,
)
from app.objects.clothing import ClothingAtEvent

from app.backend.clothing.active_cadets_with_clothing import (
    get_dict_of_active_cadets_with_clothing_at_event,
)

from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_tables import Table, RowInTable
from app.objects.events import Event

from app.objects.abstract_objects.abstract_buttons import (
    Button,
    ButtonBar,
    save_menu_button,
    cancel_menu_button,
    HelpButton,
)


sort_buttons_for_clothing = ButtonBar(
    [Button(sort_by, nav_button=True) for sort_by in all_sort_types]
)

FILTER_COMMITTEE_BUTTON_LABEL = "Show only current cadet committee"
FILTER_ALL_BUTTON_LABEL = "Show all cadets"
DISTRIBUTE_ACTION_BUTTON_LABEL = (
    "Distribute remaining colours (even age spread, avoid same surnames)"
)
CLEAR_ALL_COLOURS = "Clear all colour groups"

EXPORT_COMMITTEE = "Download committee polo shirts spreadsheet"
EXPORT_ALL = "Download spreadsheet of t-shirt sizes"
EXPORT_COLOURS = "Download spreadsheet of colour teams"

#### Sort by ... usual, plus sort by size, sort by colour
#### Filter - show only current committee
#### Auto colour


def get_button_bar_for_clothing(interface: abstractInterface) -> ButtonBar:
    if are_we_showing_only_committee(interface):
        filter_button = filter_all_button
        export_buttons = [export_committee_button]
    else:
        filter_button = filter_committee_button
        export_buttons = [export_all_clothing_button, export_colours_button]

    button_bar = ButtonBar(
        [cancel_menu_button, save_menu_button, filter_button, clear_all_colours_button]
        + export_buttons
    )

    if not are_we_showing_only_committee(interface):
        button_bar.append(distribute_action_button)

    button_bar.append(help_button)

    return button_bar


distribute_action_button = Button(DISTRIBUTE_ACTION_BUTTON_LABEL, nav_button=True)
clear_all_colours_button = Button(CLEAR_ALL_COLOURS, nav_button=True)
filter_all_button = Button(FILTER_ALL_BUTTON_LABEL, nav_button=True)
filter_committee_button = Button(FILTER_COMMITTEE_BUTTON_LABEL, nav_button=True)
export_committee_button = Button(EXPORT_COMMITTEE, nav_button=True)
export_all_clothing_button = Button(EXPORT_ALL, nav_button=True)
export_colours_button = Button(EXPORT_COLOURS, nav_button=True)
help_button = HelpButton("clothing_help")


def get_clothing_table(interface: abstractInterface, event: Event) -> Table:
    sort_order = get_sort_order(interface)
    only_committee = are_we_showing_only_committee(interface)

    dict_of_cadets_with_clothing = get_dict_of_active_cadets_with_clothing_at_event(
        object_store=interface.object_store, event=event, only_committee=only_committee
    )
    sorted_dict_of_cadets_with_clothing = dict_of_cadets_with_clothing.sort_by(
        sort_order
    )

    size_options = sorted_dict_of_cadets_with_clothing.get_clothing_size_options()
    colour_options = sorted_dict_of_cadets_with_clothing.get_colour_options()
    top_row = get_top_row_for_clothing_table()
    body = [
        get_clothing_row_for_cadet(
            cadet=cadet,
            clothing=clothing,
            size_options=size_options,
            colour_options=colour_options,
        )
        for cadet, clothing in sorted_dict_of_cadets_with_clothing.items()
    ]

    return Table([top_row] + body)


def get_top_row_for_clothing_table() -> RowInTable:
    return RowInTable(
        [
            "",
            "Size (delete existing size to see options, or type in a new value)",
            "Colour (delete existing size to see options, or type in a new value)",
        ]
    )


def get_clothing_row_for_cadet(
    size_options: List[str],
    colour_options: List[str],
    cadet: Cadet,
    clothing: ClothingAtEvent,
) -> RowInTable:
    cadet_id = cadet.id
    size_field = listInput(
        list_of_options=size_options,
        input_name=size_field_name(cadet_id=cadet_id),
        default_option=clothing.size,
        input_label="",
    )
    colour_field = listInput(
        list_of_options=colour_options,
        input_name=colour_field_name(cadet_id=cadet_id),
        default_option=clothing.colour,
        input_label="",
    )

    return RowInTable([str(cadet), size_field, colour_field])


def size_field_name(cadet_id: str) -> str:
    return "size_%s" % cadet_id


def colour_field_name(cadet_id: str) -> str:
    return "colour_%s" % cadet_id


COMMITTEE_ONLY = "com_only_cloth"
SORT_ORDER = "cloth_sort"


def set_to_showing_only_committee(interface: abstractInterface):
    interface.set_persistent_value(COMMITTEE_ONLY, True)


def set_to_showing_all(interface: abstractInterface):
    interface.set_persistent_value(COMMITTEE_ONLY, False)


def are_we_showing_only_committee(interface: abstractInterface) -> bool:
    return interface.get_persistent_value(COMMITTEE_ONLY, default=False)


def get_sort_order(interface: abstractInterface) -> str:
    return interface.get_persistent_value(SORT_ORDER, default=SORT_BY_FIRSTNAME)


def save_sort_order(interface: abstractInterface, sort_order: str):
    interface.set_persistent_value(SORT_ORDER, sort_order)
