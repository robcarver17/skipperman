from dataclasses import dataclass
from typing import List

from app.backend.data.resources import get_list_of_boats_excluding_boats_already_at_event
from app.objects.abstract_objects.abstract_buttons import Button
from app.objects.abstract_objects.abstract_lines import Line
from app.objects.day_selectors import Day
from app.objects.events import Event
from app.objects.abstract_objects.abstract_tables import Table, RowInTable
from app.objects.abstract_objects.abstract_form import dropDownInput
from app.objects.patrol_boats import PatrolBoat

ADD_BOAT_DROPDOWN = "add_boat_dropdown"
ADD_NEW_BOAT_BUTTON_LABEL = "Add new boat"

@dataclass
class DataToBeStoredWhilstConstructingTableBodyForBoatAllocation:
    thing: float

def get_patrol_boat_table(event: Event) -> Table:

    top_row = get_top_row_for_patrol_boat_table(event)
    other_rows = get_body_of_patrol_boat_table_at_event(event=event)
    bottom_row = get_bottom_row_for_patrol_boat_table(event)

    return Table(
        [top_row]+other_rows+[bottom_row]
    )


def get_top_row_for_patrol_boat_table(event: Event) -> RowInTable:
    list_of_days_at_event_as_str = event.weekdays_in_event_as_list_of_string()

    return RowInTable([
        "Boat",
    ]+list_of_days_at_event_as_str
                      )

def get_bottom_row_for_patrol_boat_table(event: Event) -> RowInTable:

    add_boat_dropdown = get_add_boat_dropdown(event)

    list_of_days_at_event_as_str = event.weekdays_in_event_as_list_of_string()
    number_of_padding_columns=len(list_of_days_at_event_as_str)
    padding_columns = [""]*number_of_padding_columns

    return RowInTable([
        add_boat_dropdown,
    ]+padding_columns
                      )


def get_add_boat_dropdown(event: Event) -> Line:
    list_of_boats_excluding_boats_already_at_event = get_list_of_boat_names_excluding_boats_already_at_event(event)
    list_of_boats_as_dict = dict([(boat_name, boat_name) for boat_name in list_of_boats_excluding_boats_already_at_event])
    dropdown = dropDownInput(
        input_name=ADD_BOAT_DROPDOWN,
        input_label="",
        dict_of_options=list_of_boats_as_dict
    )
    button = Button(ADD_NEW_BOAT_BUTTON_LABEL)

    return Line([dropdown, button])

def get_list_of_boat_names_excluding_boats_already_at_event(event: Event) -> List[str]:
    list_of_boats_excluding_boats_already_at_event = get_list_of_boats_excluding_boats_already_at_event(event)

    return [str(boat) for boat in list_of_boats_excluding_boats_already_at_event]


def get_body_of_patrol_boat_table_at_event(event: Event,) -> List[RowInTable]:

    #data_to_be_stored = get_patrol_boat_data_to_be_stored(event)
    data_to_be_stored = ""

    #list_of_boats_at_event = get_list_of_boats_at_event(data_to_be_stored)
    list_of_boats_at_event= []

    other_rows = [get_row_for_boat_at_event(
                                                 boat_at_event = boat_at_event,
                                                 data_to_be_stored=data_to_be_stored)

                  for boat_at_event in list_of_boats_at_event]

    return other_rows

def get_list_of_boats_at_event(
        data_to_be_stored: DataToBeStoredWhilstConstructingTableBodyForBoatAllocation,
                                ):


    return data_to_be_stored.list_of_boats_at_event

def get_row_for_boat_at_event(data_to_be_stored: DataToBeStoredWhilstConstructingTableBodyForBoatAllocation,
                              boat_at_event: PatrolBoat) -> RowInTable:


    day_inputs = [get_allocation_inputs_for_day_and_boat(
        data_to_be_stored=data_to_be_stored,
        boat_at_event=boat_at_event,
        day=day
    ) for day in data_to_be_stored.event.weekdays_in_event()]

    return RowInTable([

    ]+day_inputs)



def get_allocation_inputs_for_day_and_boat(boat_at_event: PatrolBoat,
                                                 day: Day,
                                                data_to_be_stored: DataToBeStoredWhilstConstructingTableBodyForBoatAllocation
                                                 ) -> Line:

    pass


