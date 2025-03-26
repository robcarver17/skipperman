from typing import Dict, List

import pandas as pd

from app.backend.club_boats.club_boat_limits import get_dict_of_club_dinghy_limits, \
    update_limit_for_club_dinghy_at_event
from app.backend.club_boats.summary import summarise_club_boat_allocations_for_event
from app.backend.club_boats.list_of_club_dinghies import get_list_of_club_dinghies
from app.frontend.shared.events_state import get_event_from_state
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_tables import Table, RowInTable
from app.objects.club_dinghies import ClubDinghy
from app.objects.events import Event
from app.objects.abstract_objects.abstract_form import intInput
from app.objects.abstract_objects.abstract_buttons import Button


def get_club_dinghies_form(interface: abstractInterface, event: Event) -> Table:
    object_store =interface.object_store
    club_dinghies_as_df = summarise_club_boat_allocations_for_event(
        event=event, object_store=object_store
    )
    limits = get_dict_of_club_dinghy_limits(object_store)
    limits_for_event  = limits.dict_of_limits_for_all_visible_club_boats(event)

    list_of_club_dinghies = get_list_of_club_dinghies(interface.object_store)
    visible_dinghies = list_of_club_dinghies.visible_only()
    list_of_dinghy_names = visible_dinghies.list_of_names()
    list_of_dinghy_names = [name for name in list_of_dinghy_names if len(name)>0] ##FIXME weird bug

    top_row = get_top_row_in_club_dinghy_form(event)

    rows_in_table = [
        get_row_in_club_dinghy_form(
            event=event, name_of_dinghy=boat_name,
            limits_for_event=limits_for_event,
            club_dinghies_as_df=club_dinghies_as_df
        ) for boat_name in list_of_dinghy_names
    ]

    bottom_row = get_bottom_row_in_club_dinghy_form(event)

    table = Table(
        [top_row]+rows_in_table+[bottom_row],
        has_column_headings=True, has_row_headings=True
    )

    return table


def get_top_row_in_club_dinghy_form(event: Event) -> RowInTable:
    list_of_days = [day.name for day in event.days_in_event()]

    return RowInTable(
        ['Club boat']+list_of_days+['Spaces in boat available at event (x2 boats for double handers)']
    , is_heading_row=True)

def get_row_in_club_dinghy_form(event: Event, name_of_dinghy: str, club_dinghies_as_df: pd.DataFrame, limits_for_event: Dict[str, int]) -> RowInTable:
    limit_value = limits_for_event[name_of_dinghy]
    day_values_in_df = get_boats_allocated_per_day(event, name_of_dinghy, club_dinghies_as_df, limit_value)
    input_cell = get_input_cell_for_boat_limits(current_limit=limit_value, name_of_dinghy=name_of_dinghy)

    return RowInTable(
        [name_of_dinghy]+day_values_in_df+[input_cell]
    )



def get_boats_allocated_per_day(event: Event, name_of_dinghy:str, club_dinghies_as_df: pd.DataFrame, limit_value: int) -> List[str]:
    try:
        row_in_df = club_dinghies_as_df.loc[name_of_dinghy]
        day_values_in_df = [int(x) for x in list(row_in_df.values)]
    except KeyError:
        day_values_in_df= [0]*len(event.days_in_event())

    def _str_add_start(value: int, limit_value:int):
        if int(value)>int(limit_value):
            return "%d *" % value
        else:
            return str(value)

    day_values_in_df = [_str_add_start(value, limit_value) for value in day_values_in_df]

    return day_values_in_df


def get_input_cell_for_boat_limits(current_limit: int, name_of_dinghy: str) -> intInput:
    return intInput(input_name=get_cell_name_for_boat_limits(name_of_dinghy),
                    input_label='',
                    value = int(current_limit))

BOAT_LIMIT_INPUT = "Boatlimitinput"
def get_cell_name_for_boat_limits(boat_name:str):
    return BOAT_LIMIT_INPUT+"^"+boat_name

update_limits_button = Button("Update club boat limits for event")

def get_bottom_row_in_club_dinghy_form(event: Event) -> RowInTable:
    pad_list_of_days = ["" for __ in range(len(event.days_in_event())+1)]

    return RowInTable(
        pad_list_of_days+[update_limits_button]
    )


def update_club_boat_limits_for_event_from_form(interface: abstractInterface):

    event = get_event_from_state(interface)
    list_of_club_dinghies = get_list_of_club_dinghies(interface.object_store)

    for club_dinghy in list_of_club_dinghies:
        update_club_boat_limit_for_specific_boat_and_event(
            interface=interface,
            event=event,
            club_dinghy=club_dinghy
        )

def update_club_boat_limit_for_specific_boat_and_event(interface: abstractInterface, event: Event, club_dinghy: ClubDinghy):
    new_limit = get_limit_for_boat_from_form(interface=interface, club_dinghy=club_dinghy)
    update_limit_for_club_dinghy_at_event(object_store=interface.object_store,
                                          club_dinghy=club_dinghy,
                                          event=event,
                                          new_limit=new_limit)

def get_limit_for_boat_from_form(interface: abstractInterface, club_dinghy: ClubDinghy) -> int:
    cell_name = get_cell_name_for_boat_limits(club_dinghy.name)
    limit = interface.value_from_form(cell_name, default=0)

    return limit
